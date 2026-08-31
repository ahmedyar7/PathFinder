/* =============================================================================
   Pathfinder Visualizer — showcase site behaviour
   Plain ES5+/vanilla JS, no dependencies. Everything degrades gracefully:
   if a section is missing or motion is reduced, the page still reads fine.
   ========================================================================== */
(function () {
  "use strict";

  /* ------------------------------- helpers ------------------------------- */
  var $ = function (sel, ctx) { return (ctx || document).querySelector(sel); };
  var $$ = function (sel, ctx) {
    return Array.prototype.slice.call((ctx || document).querySelectorAll(sel));
  };

  var motionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
  var reduceMotion = motionQuery.matches;

  /* Small seeded RNG so the "random" patterns are stable between reloads. */
  function rng(seed) {
    var s = seed >>> 0;
    return function () {
      s = (s * 1664525 + 1013904223) >>> 0;
      return s / 4294967296;
    };
  }

  /* ========================================================================
     1. Navigation — sticky styling, mobile menu, active-section highlight
     ==================================================================== */
  (function nav() {
    var bar = $("#nav");
    var toggle = $("#navToggle");
    var menu = $("#navMenu");
    var links = $$(".nav__link");

    if (toggle && menu) {
      toggle.addEventListener("click", function () {
        var open = menu.classList.toggle("is-open");
        toggle.setAttribute("aria-expanded", open ? "true" : "false");
      });
      // Close the mobile menu once a destination has been picked.
      menu.addEventListener("click", function (e) {
        if (e.target.closest("a") && menu.classList.contains("is-open")) {
          menu.classList.remove("is-open");
          toggle.setAttribute("aria-expanded", "false");
        }
      });
    }

    // Add a background to the bar as soon as the page leaves the top.
    var ticking = false;
    function onScroll() {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(function () {
        if (bar) bar.classList.toggle("is-stuck", window.scrollY > 12);
        updateProgress();
        ticking = false;
      });
    }
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();

    // Highlight whichever section currently owns the middle of the viewport.
    var sections = links
      .map(function (l) { return $(l.getAttribute("href")); })
      .filter(Boolean);

    if ("IntersectionObserver" in window && sections.length) {
      var spy = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            if (!entry.isIntersecting) return;
            links.forEach(function (l) {
              l.classList.toggle(
                "is-active",
                l.getAttribute("href") === "#" + entry.target.id
              );
            });
          });
        },
        { rootMargin: "-45% 0px -50% 0px", threshold: 0 }
      );
      sections.forEach(function (s) { spy.observe(s); });
    }

    // Smooth scrolling for in-page links (and a manual fallback where
    // scroll-behaviour is disabled, e.g. reduced motion).
    $$('a[href^="#"]').forEach(function (link) {
      link.addEventListener("click", function (e) {
        var id = link.getAttribute("href");
        if (!id || id === "#") return;
        var target = document.querySelector(id);
        if (!target) return;
        e.preventDefault();
        target.scrollIntoView({
          behavior: reduceMotion ? "auto" : "smooth",
          block: "start"
        });
        history.replaceState(null, "", id);
      });
    });
  })();

  /* -------------------------- reading progress bar ----------------------- */
  var progressBar = $("#progressBar");
  function updateProgress() {
    if (!progressBar) return;
    var doc = document.documentElement;
    var max = doc.scrollHeight - window.innerHeight;
    var pct = max > 0 ? Math.min(1, window.scrollY / max) : 0;
    progressBar.style.transform = "scaleX(" + pct.toFixed(4) + ")";
  }

  /* ========================================================================
     2. Scroll reveal — fade/slide sections and cards into view
     ==================================================================== */
  (function reveal() {
    var items = $$("[data-reveal]");
    if (!items.length) return;

    if (reduceMotion || !("IntersectionObserver" in window)) {
      items.forEach(function (el) { el.classList.add("is-visible"); });
      return;
    }

    // Cards inside the same grid come in one after the other.
    $$(".cards, .controls__grid").forEach(function (group) {
      $$("[data-reveal]", group).forEach(function (card, i) {
        card.style.setProperty("--reveal-delay", i * 90 + "ms");
      });
    });

    var io = new IntersectionObserver(
      function (entries, obs) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("is-visible");
          obs.unobserve(entry.target);
        });
      },
      // threshold 0 so tall sections reveal the moment their top edge lands
      { threshold: 0, rootMargin: "0px 0px -8% 0px" }
    );
    items.forEach(function (el) { io.observe(el); });
  })();

  /* ========================================================================
     3. Hero board — a real A* search, animated cell by cell, on a loop
     ==================================================================== */
  (function heroSolver() {
    var host = $("#heroGrid");
    if (!host) return;

    var statusEl = $("#heroStatus");
    var visitedEl = $("#heroVisited");
    var lengthEl = $("#heroLength");

    var cols = 0, rows = 0, cells = [], walls = [], startIdx = 0, endIdx = 0;
    var frames = [];        // queue of [index, className] paint operations
    var cursor = 0;
    var visited = 0;
    var rafId = null;
    var holdUntil = 0;
    var running = false;
    var seed = 1;

    /* ---- board construction ---- */
    function sizeBoard() {
      var width = host.clientWidth || 420;
      cols = Math.max(14, Math.min(30, Math.round(width / 15)));
      rows = Math.max(10, Math.round(cols * 0.66));
      host.style.setProperty("--cols", cols);

      var frag = document.createDocumentFragment();
      cells = [];
      for (var i = 0; i < cols * rows; i++) {
        var cell = document.createElement("span");
        cell.className = "cell";
        frag.appendChild(cell);
        cells.push(cell);
      }
      host.textContent = "";
      host.appendChild(frag);
    }

    // Barriers are drawn as short runs so the board looks hand-made rather
    // than like TV static — and the layout is re-rolled until it is solvable.
    function buildMaze() {
      var rand = rng(seed++ * 2654435761);
      var attempt = 0;
      do {
        walls = new Array(cols * rows).fill(false);
        startIdx = 1 * cols + 1;
        endIdx = (rows - 2) * cols + (cols - 2);

        var runs = Math.round(cols * rows * 0.028) + 4;
        for (var r = 0; r < runs; r++) {
          var horizontal = rand() > 0.5;
          var len = 3 + Math.floor(rand() * 5);
          var row = Math.floor(rand() * rows);
          var col = Math.floor(rand() * cols);
          for (var k = 0; k < len; k++) {
            var rr = horizontal ? row : row + k;
            var cc = horizontal ? col + k : col;
            if (rr < 0 || rr >= rows || cc < 0 || cc >= cols) continue;
            var idx = rr * cols + cc;
            if (idx === startIdx || idx === endIdx) continue;
            walls[idx] = true;
          }
        }
        attempt++;
      } while (!isSolvable() && attempt < 20);

      if (!isSolvable()) walls = new Array(cols * rows).fill(false);
    }

    function neighbors(idx) {
      var r = Math.floor(idx / cols), c = idx % cols, out = [];
      if (r > 0) out.push(idx - cols);
      if (r < rows - 1) out.push(idx + cols);
      if (c > 0) out.push(idx - 1);
      if (c < cols - 1) out.push(idx + 1);
      return out;
    }

    function isSolvable() {
      var seen = new Uint8Array(cols * rows);
      var queue = [startIdx];
      seen[startIdx] = 1;
      while (queue.length) {
        var cur = queue.shift();
        if (cur === endIdx) return true;
        var nb = neighbors(cur);
        for (var i = 0; i < nb.length; i++) {
          if (!seen[nb[i]] && !walls[nb[i]]) { seen[nb[i]] = 1; queue.push(nb[i]); }
        }
      }
      return false;
    }

    /* ---- the search itself: A* with a Manhattan heuristic ---- */
    function heuristic(a, b) {
      return (
        Math.abs(Math.floor(a / cols) - Math.floor(b / cols)) +
        Math.abs((a % cols) - (b % cols))
      );
    }

    function solve() {
      var total = cols * rows;
      var g = new Float64Array(total).fill(Infinity);
      var f = new Float64Array(total).fill(Infinity);
      var cameFrom = new Int32Array(total).fill(-1);
      var inOpen = new Uint8Array(total);
      var closed = new Uint8Array(total);
      var open = [startIdx];

      g[startIdx] = 0;
      f[startIdx] = heuristic(startIdx, endIdx);
      inOpen[startIdx] = 1;

      var trace = [];   // every paint operation, in the order it happened
      var found = false;

      while (open.length) {
        // Cheapest f wins; a small linear scan is plenty at this board size.
        var best = 0;
        for (var i = 1; i < open.length; i++) if (f[open[i]] < f[open[best]]) best = i;
        var current = open.splice(best, 1)[0];
        inOpen[current] = 0;
        closed[current] = 1;

        if (current !== startIdx) trace.push([current, "is-closed"]);
        if (current === endIdx) { found = true; break; }

        var nb = neighbors(current);
        for (var n = 0; n < nb.length; n++) {
          var next = nb[n];
          if (walls[next] || closed[next]) continue;
          var tentative = g[current] + 1;
          if (tentative < g[next]) {
            cameFrom[next] = current;
            g[next] = tentative;
            f[next] = tentative + heuristic(next, endIdx);
            if (!inOpen[next]) {
              inOpen[next] = 1;
              open.push(next);
              if (next !== endIdx) trace.push([next, "is-open"]);
            }
          }
        }
      }

      // Walk the parents backwards, then paint the path start-to-end.
      var path = [];
      if (found) {
        var node = endIdx;
        while (node !== -1 && node !== startIdx) { path.push(node); node = cameFrom[node]; }
        path.reverse();
        path.forEach(function (idx) {
          if (idx !== endIdx) trace.push([idx, "is-path"]);
        });
      }

      return { trace: trace, pathLength: path.length, found: found };
    }

    /* ---- painting ---- */
    function paintStatic() {
      for (var i = 0; i < cells.length; i++) {
        cells[i].className = "cell" + (walls[i] ? " is-wall" : "");
      }
      cells[startIdx].className = "cell is-start";
      cells[endIdx].className = "cell is-end";
    }

    var result = null;

    function prepare() {
      buildMaze();
      paintStatic();
      result = solve();
      frames = result.trace;
      cursor = 0;
      visited = 0;
      if (statusEl) {
        statusEl.textContent = "searching…";
        statusEl.classList.remove("is-done");
      }
      if (visitedEl) visitedEl.textContent = "0";
      if (lengthEl) lengthEl.textContent = "0";
    }

    function finish() {
      if (statusEl) {
        statusEl.textContent = result.found ? "path found ✓" : "no path";
        statusEl.classList.add("is-done");
      }
      if (lengthEl) lengthEl.textContent = String(result.pathLength);
      holdUntil = performance.now() + 2200;
    }

    function tick(now) {
      rafId = null;
      if (!running) return;

      if (cursor < frames.length) {
        // Paint a handful of cells per frame so a full solve takes ~2-4s.
        var budget = Math.max(2, Math.round(frames.length / 190));
        for (var i = 0; i < budget && cursor < frames.length; i++, cursor++) {
          var op = frames[cursor];
          var cell = cells[op[0]];
          if (!cell) continue;
          cell.classList.remove("is-open", "is-closed");
          cell.classList.add(op[1]);
          if (op[1] === "is-closed") {
            visited++;
            if (visitedEl && visited % 3 === 0) visitedEl.textContent = String(visited);
          }
        }
        if (cursor >= frames.length) { if (visitedEl) visitedEl.textContent = String(visited); finish(); }
      } else if (now >= holdUntil) {
        prepare();   // re-roll the maze and go again
      }

      rafId = window.requestAnimationFrame(tick);
    }

    function start() {
      if (running || reduceMotion) return;
      running = true;
      rafId = window.requestAnimationFrame(tick);
    }

    function stop() {
      running = false;
      if (rafId) { window.cancelAnimationFrame(rafId); rafId = null; }
    }

    /* ---- boot ---- */
    function boot() {
      sizeBoard();
      prepare();

      if (reduceMotion) {
        // Show the finished solve instead of animating toward it.
        frames.forEach(function (op) {
          var cell = cells[op[0]];
          if (!cell) return;
          cell.classList.remove("is-open", "is-closed");
          cell.classList.add(op[1]);
        });
        if (visitedEl) {
          visitedEl.textContent = String(
            frames.filter(function (op) { return op[1] === "is-closed"; }).length
          );
        }
        if (lengthEl) lengthEl.textContent = String(result.pathLength);
        if (statusEl) { statusEl.textContent = "path found ✓"; statusEl.classList.add("is-done"); }
        return;
      }
      start();
    }

    boot();

    // Pause the loop whenever it is off-screen or the tab is hidden.
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting && !document.hidden) start();
          else stop();
        });
      }, { threshold: 0.05 }).observe(host);
    }
    document.addEventListener("visibilitychange", function () {
      if (document.hidden) stop(); else start();
    });

    // Re-fit (and re-roll) the board when the viewport changes size.
    var resizeTimer;
    window.addEventListener("resize", function () {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(function () {
        var wasRunning = running;
        stop();
        boot();
        if (!wasRunning && !reduceMotion) stop();
      }, 220);
    });
  })();

  /* ========================================================================
     4. Algorithm cards — mini grids that replay each search's own pattern
        Cells are given an --i order index; CSS turns that into a staggered
        transition-delay on hover/focus, so the reveal is pure CSS.
     ==================================================================== */
  (function algoIcons() {
    var grids = $$("[data-mini]");
    if (!grids.length) return;

    var N = 9;                       // 9 x 9 icon board
    var WALLS = [];                  // kept clear: the shape of the search is the point
    var START = 4 * N + 1;           // mid-left
    var END = 4 * N + 7;             // mid-right

    function rc(i) { return [Math.floor(i / N), i % N]; }
    function isWall(i) { return WALLS.indexOf(i) !== -1; }

    function neighbors(i) {
      var p = rc(i), r = p[0], c = p[1], out = [];
      if (r > 0) out.push(i - N);
      if (r < N - 1) out.push(i + N);
      if (c > 0) out.push(i - 1);
      if (c < N - 1) out.push(i + 1);
      return out.filter(function (n) { return !isWall(n); });
    }

    // Shortest route through the icon board, used as the yellow path.
    function shortestPath() {
      var prev = {}, seen = {}, queue = [START];
      seen[START] = true;
      while (queue.length) {
        var cur = queue.shift();
        if (cur === END) break;
        neighbors(cur).forEach(function (n) {
          if (seen[n]) return;
          seen[n] = true; prev[n] = cur; queue.push(n);
        });
      }
      var path = [], node = END;
      while (node !== undefined && node !== START) { path.push(node); node = prev[node]; }
      return path.reverse();
    }

    function dist(a, b) {
      var p = rc(a), q = rc(b);
      return { man: Math.abs(p[0] - q[0]) + Math.abs(p[1] - q[1]),
               euc: Math.hypot(p[0] - q[0], p[1] - q[1]) };
    }

    // One ordering function per algorithm — this is the whole personality.
    var patterns = {
      // Directed: a real best-first expansion with a weighted heuristic, so the
      // frontier stays a narrow beam pointed at the goal.
      astar: function () {
        var g = {}, seen = {}, open = [START], order = [];
        g[START] = 0; seen[START] = true;
        var f = function (i) { return g[i] + 1.15 * dist(i, END).man; };
        while (open.length && order.length < 26) {
          var best = 0;
          for (var i = 1; i < open.length; i++) if (f(open[i]) < f(open[best])) best = i;
          var cur = open.splice(best, 1)[0];
          if (cur !== START && cur !== END) order.push(cur);
          neighbors(cur).forEach(function (n) {
            if (seen[n]) return;
            seen[n] = true; g[n] = g[cur] + 1; open.push(n);
          });
        }
        return order;
      },
      // Uniform rings of Manhattan distance.
      bfs: function () {
        var scored = [];
        for (var i = 0; i < N * N; i++) {
          if (isWall(i) || i === START || i === END) continue;
          var d = dist(i, START).man;
          if (d <= 4) scored.push([i, d]);
        }
        return scored.sort(function (a, b) { return a[1] - b[1]; })
                     .map(function (s) { return s[0]; });
      },
      // Same idea, but circular: true distance rather than step count.
      dijkstra: function () {
        var scored = [];
        for (var i = 0; i < N * N; i++) {
          if (isWall(i) || i === START || i === END) continue;
          var d = dist(i, START).euc;
          if (d <= 3.9) scored.push([i, d]);
        }
        return scored.sort(function (a, b) { return a[1] - b[1]; })
                     .map(function (s) { return s[0]; });
      },
      // Organic: grow a tree by repeatedly attaching a random frontier cell.
      prim: function () {
        var rand = rng(20240924);
        var inTree = {}, frontier = [], order = [];
        inTree[START] = true;
        neighbors(START).forEach(function (n) { frontier.push(n); });
        while (frontier.length && order.length < 30) {
          var pick = Math.floor(rand() * frontier.length);
          var cell = frontier.splice(pick, 1)[0];
          if (inTree[cell]) continue;
          inTree[cell] = true;
          if (cell !== END) order.push(cell);
          neighbors(cell).forEach(function (n) { if (!inTree[n]) frontier.push(n); });
        }
        return order;
      }
    };

    var path = shortestPath();

    grids.forEach(function (grid) {
      var kind = grid.getAttribute("data-mini");
      var explored = (patterns[kind] || patterns.bfs)();
      var order = {};
      explored.forEach(function (idx, i) { order[idx] = i; });

      var frag = document.createDocumentFragment();
      for (var i = 0; i < N * N; i++) {
        var cell = document.createElement("i");
        var cls = "";
        if (i === START) cls = "m-start";
        else if (i === END) cls = "m-end";
        else if (isWall(i)) cls = "m-wall";
        else if (path.indexOf(i) !== -1) {
          // Path cells light up after the exploration has played out.
          cls = "m-path";
          cell.style.setProperty("--i", explored.length + path.indexOf(i));
        } else if (order[i] !== undefined) {
          cls = "m-ex";
          cell.style.setProperty("--i", order[i]);
        }
        cell.className = cls;
        frag.appendChild(cell);
      }
      grid.appendChild(frag);
    });

    // Touch devices never fire :hover — play each card's animation once as it
    // scrolls into view instead.
    var coarse = window.matchMedia("(hover: none)").matches;
    if (coarse && !reduceMotion && "IntersectionObserver" in window) {
      var io = new IntersectionObserver(function (entries, obs) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("is-live");
          obs.unobserve(entry.target);
        });
      }, { threshold: 0.4 });
      $$(".algo").forEach(function (card) { io.observe(card); });
    }
  })();

  /* ========================================================================
     5. Screenshot gallery — scroll-snap carousel with dots and autoplay
     ==================================================================== */
  (function gallery() {
    var root = $("#gallery");
    var track = $("#galleryTrack");
    if (!root || !track) return;

    var slides = $$(".slide", track);
    var dotsWrap = $("#galleryDots");
    var prev = $("#galleryPrev");
    var next = $("#galleryNext");
    var index = 0;
    var timer = null;
    if (slides.length < 2) return;

    // Distance between two slide origins, gap included.
    function stride() {
      if (slides.length < 2) return track.clientWidth;
      return slides[1].getBoundingClientRect().left - slides[0].getBoundingClientRect().left;
    }

    var dots = slides.map(function (slide, i) {
      var dot = document.createElement("button");
      dot.type = "button";
      dot.setAttribute("aria-label", "Show screenshot " + (i + 1) + " of " + slides.length);
      dot.addEventListener("click", function () { go(i, true); });
      if (dotsWrap) dotsWrap.appendChild(dot);
      return dot;
    });

    function sync(i) {
      index = i;
      dots.forEach(function (d, n) {
        d.classList.toggle("is-active", n === i);
        d.setAttribute("aria-current", n === i ? "true" : "false");
      });
    }

    function go(i, userDriven) {
      var target = (i + slides.length) % slides.length;
      track.scrollTo({
        left: target * stride(),
        behavior: reduceMotion ? "auto" : "smooth"
      });
      sync(target);
      if (userDriven) restart();
    }

    if (prev) prev.addEventListener("click", function () { go(index - 1, true); });
    if (next) next.addEventListener("click", function () { go(index + 1, true); });

    track.addEventListener("keydown", function (e) {
      if (e.key === "ArrowRight") { e.preventDefault(); go(index + 1, true); }
      if (e.key === "ArrowLeft") { e.preventDefault(); go(index - 1, true); }
    });

    // Keep the dots in step when the carousel is swiped or scrolled directly.
    var scrollTimer;
    track.addEventListener("scroll", function () {
      clearTimeout(scrollTimer);
      scrollTimer = setTimeout(function () {
        var s = stride() || 1;
        sync(Math.round(track.scrollLeft / s));
      }, 90);
    }, { passive: true });

    /* ---- autoplay, paused on interaction or when out of view ---- */
    function restart() { stopAuto(); startAuto(); }
    function startAuto() {
      if (reduceMotion || timer || document.hidden) return;
      timer = setInterval(function () { go(index + 1); }, 5200);
    }
    function stopAuto() { clearInterval(timer); timer = null; }

    ["mouseenter", "focusin", "touchstart", "pointerdown"].forEach(function (evt) {
      root.addEventListener(evt, stopAuto, { passive: true });
    });
    ["mouseleave", "focusout"].forEach(function (evt) {
      root.addEventListener(evt, startAuto);
    });
    document.addEventListener("visibilitychange", function () {
      if (document.hidden) stopAuto(); else startAuto();
    });

    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) startAuto(); else stopAuto();
        });
      }, { threshold: 0.25 }).observe(root);
    } else {
      startAuto();
    }

    sync(0);
    window.addEventListener("resize", function () {
      track.scrollLeft = index * stride();
    });
  })();

  /* ========================================================================
     6. Copy-to-clipboard for the install block
     ==================================================================== */
  (function copyBlock() {
    var btn = $("#copyBtn");
    if (!btn) return;
    var label = $(".copy__label", btn) || btn;
    var source = document.getElementById(btn.getAttribute("data-target"));
    if (!source) return;

    function flash(text) {
      label.textContent = text;
      btn.classList.add("is-done");
      setTimeout(function () {
        label.textContent = "Copy";
        btn.classList.remove("is-done");
      }, 1800);
    }

    // execCommand fallback: the async clipboard API is blocked on file:// in
    // several browsers, and this page is meant to open straight off disk.
    function legacyCopy(text) {
      var ta = document.createElement("textarea");
      ta.value = text;
      ta.setAttribute("readonly", "");
      ta.style.cssText = "position:fixed;top:0;left:-9999px;opacity:0";
      document.body.appendChild(ta);
      ta.select();
      var ok = false;
      try { ok = document.execCommand("copy"); } catch (err) { ok = false; }
      document.body.removeChild(ta);
      return ok;
    }

    btn.addEventListener("click", function () {
      var text = source.innerText.replace(/ /g, " ").trim();
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(
          function () { flash("Copied ✓"); },
          function () { flash(legacyCopy(text) ? "Copied ✓" : "Press Ctrl+C"); }
        );
      } else {
        flash(legacyCopy(text) ? "Copied ✓" : "Press Ctrl+C");
      }
    });
  })();

  /* ------------------------------ 7. Misc -------------------------------- */
  var year = $("#year");
  if (year) year.textContent = new Date().getFullYear();

  // Respond live if the visitor flips their reduced-motion setting.
  var onMotionChange = function (e) { reduceMotion = e.matches; };
  if (motionQuery.addEventListener) motionQuery.addEventListener("change", onMotionChange);
  else if (motionQuery.addListener) motionQuery.addListener(onMotionChange);
})();
