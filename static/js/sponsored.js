/* Sponsored deals strip (homepage).
   Drifts left at ~40 px/s with the GSAP ticker; the items are cloned once so the loop is seamless.
   Pauses on hover, keyboard focus, an open quick view, the pause button, or when off-screen.
   Prev / Next glide one card (420 ms). Under prefers-reduced-motion (or without GSAP) it is a
   plain scrollable rail and the same buttons scroll it. */
(function () {
  "use strict";
  const root = document.querySelector("[data-sponsored]");
  if (!root) return;

  const viewport = root.querySelector("[data-sp-viewport]");
  const track = root.querySelector("[data-sp-track]");
  const prev = root.querySelector("[data-sp-prev]");
  const next = root.querySelector("[data-sp-next]");
  const toggle = root.querySelector("[data-sp-toggle]");
  const SPEED = 40; // px per second
  const GLIDE = 0.42; // seconds
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const items = Array.from(track.children);

  function step() {
    const first = items[0];
    const gap = parseFloat(getComputedStyle(track).columnGap) || 0;
    return first ? first.getBoundingClientRect().width + gap : 240;
  }

  // ---------- few deals: they all fit, so nothing moves and the controls are not needed ----------
  if (track.scrollWidth <= viewport.clientWidth) {
    root.classList.add("is-static");
    [toggle, prev, next].forEach((button) => { button.hidden = true; });
    return;
  }

  // ---------- manual rail (reduced motion / no GSAP) ----------
  if (reduceMotion || typeof window.gsap === "undefined") {
    root.classList.add("is-manual");
    toggle.hidden = true;
    prev.addEventListener("click", () => viewport.scrollBy({ left: -step(), behavior: "auto" }));
    next.addEventListener("click", () => viewport.scrollBy({ left: step(), behavior: "auto" }));
    return;
  }

  // ---------- drifting loop ----------
  root.classList.add("is-drifting");
  items.forEach((item) => {
    const clone = item.cloneNode(true);
    clone.setAttribute("aria-hidden", "true");
    clone.inert = true; // copies are for the loop only: not focusable, not read out
    clone.removeAttribute("data-testid");
    clone.querySelectorAll("[data-testid]").forEach((el) => el.removeAttribute("data-testid"));
    track.append(clone);
  });

  let x = 0;
  let glide = null;
  const reasons = new Set(); // why the strip is paused: user, hover, focus, quickview, offscreen

  function loopWidth() { return track.scrollWidth / 2; }
  function wrap(value) {
    const w = loopWidth();
    if (w <= 0) return value;
    while (value <= -w) value += w;
    while (value > 0) value -= w;
    return value;
  }
  function render() { gsap.set(track, { x }); }

  gsap.ticker.add((time, deltaMs) => {
    if (reasons.size || glide) return;
    x = wrap(x - (SPEED * deltaMs) / 1000);
    render();
  });

  function pause(reason) { reasons.add(reason); }
  function resume(reason) { reasons.delete(reason); }

  function glideBy(dx) {
    if (glide) glide.progress(1); // finish the previous glide at once
    const state = { value: x };
    glide = gsap.to(state, {
      value: x + dx, duration: GLIDE, ease: "power2.inOut",
      onUpdate: () => { x = wrap(state.value); render(); },
      onComplete: () => { glide = null; },
    });
  }
  prev.addEventListener("click", () => glideBy(step()));
  next.addEventListener("click", () => glideBy(-step()));

  function setUserPaused(paused) {
    if (paused) pause("user"); else resume("user");
    toggle.setAttribute("aria-pressed", String(paused));
    toggle.setAttribute("aria-label", paused ? "Play the moving deals" : "Pause the moving deals");
    toggle.querySelector("i").className = paused ? "bi bi-play-fill" : "bi bi-pause-fill";
  }
  toggle.addEventListener("click", () => setUserPaused(!reasons.has("user")));

  viewport.addEventListener("pointerenter", (e) => { if (e.pointerType === "mouse") pause("hover"); });
  viewport.addEventListener("pointerleave", (e) => { if (e.pointerType === "mouse") resume("hover"); });
  viewport.addEventListener("touchstart", () => pause("hover"), { passive: true });
  viewport.addEventListener("touchend", () => window.setTimeout(() => resume("hover"), 2500), { passive: true });

  // keyboard: pause and bring the focused card fully into view
  viewport.addEventListener("focusin", (e) => {
    pause("focus");
    viewport.scrollLeft = 0; // the browser may try to scroll the clipped viewport; we move the track instead
    const item = e.target.closest("li");
    if (!item) return;
    const left = item.offsetLeft + x;
    const right = left + item.offsetWidth;
    if (left < 0) { x = wrap(x - left); render(); }
    else if (right > viewport.clientWidth) { x = wrap(x - (right - viewport.clientWidth)); render(); }
  });
  viewport.addEventListener("focusout", (e) => { if (!viewport.contains(e.relatedTarget)) resume("focus"); });

  document.addEventListener("qv:open", () => pause("quickview"));
  document.addEventListener("qv:close", () => resume("quickview"));

  if ("IntersectionObserver" in window) {
    new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) resume("offscreen"); else pause("offscreen");
    }).observe(root);
  }
  document.addEventListener("visibilitychange", () => (document.hidden ? pause("hidden") : resume("hidden")));
})();
