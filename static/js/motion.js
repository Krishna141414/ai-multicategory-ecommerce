/* Subtle scroll reveals for storefront sections ([data-reveal]): fade + 12 px rise, 600 ms,
   40 ms between cards, once. Content is fully visible without JavaScript and under
   prefers-reduced-motion. Opacity (not visibility) is used so nothing is ever hidden from
   screen readers, find-in-page or keyboard focus. */
(function () {
  "use strict";
  if (typeof window.gsap === "undefined" || typeof window.ScrollTrigger === "undefined") return;
  const targets = document.querySelectorAll("[data-reveal]");
  if (!targets.length) return;
  gsap.registerPlugin(ScrollTrigger);

  const mm = gsap.matchMedia();
  mm.add("(prefers-reduced-motion: no-preference)", () => {
    gsap.set(targets, { opacity: 0, y: 12 });
    ScrollTrigger.batch(targets, {
      start: "top 92%",
      once: true,
      onEnter: (batch) => gsap.to(batch, { opacity: 1, y: 0, duration: 0.6, ease: "power2.out", stagger: 0.04, overwrite: true, clearProps: "transform,opacity" }),
    });
    // anything already above the fold when the page opens shows at once
    ScrollTrigger.refresh();
    return () => gsap.set(targets, { clearProps: "transform,opacity" });
  });
})();
