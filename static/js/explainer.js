/* AI Explainer: turns the five stacked steps into a stepper with Back / Next, step buttons,
   arrow keys and an optional autoplay. Without JavaScript every step stays visible. */
(function () {
  "use strict";
  const root = document.querySelector("[data-explainer]");
  if (!root) return;

  const steps = Array.from(root.querySelectorAll("[data-step]"));
  const nav = root.querySelector("[data-xp-nav]");
  const navButtons = Array.from(nav.querySelectorAll("[data-goto]"));
  const controls = root.querySelector("[data-xp-controls]");
  const prev = root.querySelector("[data-xp-prev]");
  const next = root.querySelector("[data-xp-next]");
  const play = root.querySelector("[data-xp-play]");
  const status = root.querySelector("[data-xp-status]");
  const titles = steps.map((s) => s.querySelector("h2").textContent.trim());
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const hasGsap = typeof window.gsap !== "undefined" && !reduceMotion;
  const AUTOPLAY_MS = 4500;
  let current = 0;
  let timer = null;

  root.classList.add("xp-enhanced");
  nav.hidden = false;
  controls.hidden = false;

  function growBars(step) {
    const bars = step.querySelectorAll("[data-bar]");
    if (!bars.length) return;
    if (hasGsap) {
      gsap.fromTo(bars, { scaleX: 0 }, { scaleX: 1, duration: 0.6, ease: "power2.out", stagger: 0.04, overwrite: true });
    }
  }

  function show(index, { focus = false } = {}) {
    index = Math.max(0, Math.min(steps.length - 1, index));
    const leaving = steps[current];
    const entering = steps[index];
    const direction = index >= current ? 1 : -1;
    steps.forEach((s, i) => { s.hidden = i !== index; });
    navButtons.forEach((b, i) => {
      if (i === index) b.setAttribute("aria-current", "step"); else b.removeAttribute("aria-current");
      b.classList.toggle("is-done", i < index);
    });
    if (hasGsap && leaving !== entering) {
      gsap.fromTo(entering, { autoAlpha: 0, y: 16 * direction }, { autoAlpha: 1, y: 0, duration: 0.4, ease: "power2.out", clearProps: "transform,visibility,opacity" });
    }
    growBars(entering);
    current = index;
    prev.disabled = index === 0;
    next.disabled = index === steps.length - 1;
    status.textContent = `Step ${index + 1} of ${steps.length}: ${titles[index]}`;
    if (focus) entering.querySelector("h2").focus({ preventScroll: true });
    if (index === steps.length - 1) stop();
  }

  function stop() {
    window.clearInterval(timer);
    timer = null;
    play.setAttribute("aria-pressed", "false");
    play.querySelector("span").textContent = "Play";
    play.querySelector("i").className = "bi bi-play-fill";
  }

  function start() {
    if (current === steps.length - 1) show(0);
    play.setAttribute("aria-pressed", "true");
    play.querySelector("span").textContent = "Pause";
    play.querySelector("i").className = "bi bi-pause-fill";
    timer = window.setInterval(() => show(current + 1), AUTOPLAY_MS);
  }

  steps.forEach((s) => s.querySelector("h2").setAttribute("tabindex", "-1"));
  prev.addEventListener("click", () => { stop(); show(current - 1, { focus: true }); });
  next.addEventListener("click", () => { stop(); show(current + 1, { focus: true }); });
  play.addEventListener("click", () => (timer ? stop() : start()));
  navButtons.forEach((b, i) => b.addEventListener("click", () => { stop(); show(i, { focus: true }); }));
  root.addEventListener("keydown", (event) => {
    if (event.target.closest("select, input, textarea")) return;
    if (event.key === "ArrowRight") { stop(); show(current + 1); }
    if (event.key === "ArrowLeft") { stop(); show(current - 1); }
  });
  show(0);
})();
