/* Chowk shared UI behaviour (store + admin). Vanilla JS, no framework.
   - toasts: auto-dismiss after 4s, paused while hovered/focused, closable
   - header: gains a hairline shadow once the page scrolls
   - forms: one submit only (button shows a spinner), password show/hide
   - cart badge: bump animation + count update (used by the cart scripts) */
(function () {
  "use strict";

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const Chowk = (window.Chowk = window.Chowk || {});
  Chowk.reduceMotion = reduceMotion;

  /* ---------- Toasts ---------- */
  function stack() {
    let el = document.querySelector("[data-toast-stack]");
    if (!el) {
      el = document.createElement("div");
      el.className = "toast-stack";
      el.setAttribute("data-toast-stack", "");
      el.setAttribute("aria-live", "polite");
      document.body.appendChild(el);
    }
    return el;
  }

  function dismiss(toast) {
    if (!toast || toast.classList.contains("is-leaving")) return;
    toast.classList.add("is-leaving");
    const remove = () => toast.remove();
    if (reduceMotion) remove();
    else toast.addEventListener("animationend", remove, { once: true });
  }

  function arm(toast) {
    let timer = null;
    const start = () => { timer = window.setTimeout(() => dismiss(toast), 4000); };
    const stop = () => window.clearTimeout(timer);
    toast.addEventListener("mouseenter", stop);
    toast.addEventListener("mouseleave", start);
    toast.addEventListener("focusin", stop);
    toast.addEventListener("focusout", start);
    toast.querySelector(".toast-close")?.addEventListener("click", () => dismiss(toast));
    if (toast.dataset.sticky === undefined) start();
  }

  const ICONS = { success: "bi-check-circle", danger: "bi-exclamation-octagon", error: "bi-exclamation-octagon", warning: "bi-exclamation-triangle", info: "bi-info-circle" };

  /** Show a toast. level: success | danger | warning | info */
  Chowk.toast = function (message, level = "info") {
    const toast = document.createElement("div");
    toast.className = `toast-item toast-${level}`;
    toast.setAttribute("role", level === "danger" ? "alert" : "status");
    toast.dataset.testid = "toast";
    toast.innerHTML = `<i class="bi ${ICONS[level] || ICONS.info}" aria-hidden="true"></i><p></p>
      <button type="button" class="toast-close" aria-label="Dismiss message"><i class="bi bi-x-lg" aria-hidden="true"></i></button>`;
    toast.querySelector("p").textContent = message;
    stack().appendChild(toast);
    arm(toast);
    return toast;
  };

  /* ---------- Cart badge ---------- */
  Chowk.setCartCount = function (count) {
    document.querySelectorAll("[data-cart-count]").forEach((badge) => {
      badge.textContent = count;
      badge.classList.toggle("is-empty", Number(count) === 0);
      badge.classList.remove("bump");
      void badge.offsetWidth; // restart the animation
      if (!reduceMotion) badge.classList.add("bump");
    });
  };

  /* ---------- Forms: one submit, spinner, password toggle ---------- */
  function guardSubmit(form) {
    form.addEventListener("submit", (event) => {
      if (form.dataset.submitting === "true") { event.preventDefault(); return; }
      form.dataset.submitting = "true";
      const button = event.submitter || form.querySelector('[type="submit"]');
      if (button && !button.hasAttribute("data-no-spinner")) {
        button.setAttribute("aria-busy", "true");
        const label = button.dataset.loadingLabel;
        if (label) button.innerHTML = `<span class="spinner-border" aria-hidden="true"></span> ${label}`;
        // keep the button's own name/value in the POST, then disable after this tick
        window.setTimeout(() => { button.disabled = true; }, 0);
      }
    });
  }

  function passwordToggles(root) {
    root.querySelectorAll("[data-password-toggle]").forEach((btn) => {
      const input = document.getElementById(btn.getAttribute("aria-controls"));
      if (!input) return;
      btn.addEventListener("click", () => {
        const show = input.type === "password";
        input.type = show ? "text" : "password";
        btn.textContent = show ? "Hide" : "Show";
        btn.setAttribute("aria-pressed", String(show));
      });
    });
  }

  /* ---------- Header scroll state ---------- */
  function headerShadow() {
    const header = document.querySelector(".site-header, .admin-topbar");
    if (!header) return;
    let ticking = false;
    const update = () => { header.classList.toggle("is-scrolled", window.scrollY > 4); ticking = false; };
    window.addEventListener("scroll", () => { if (!ticking) { ticking = true; window.requestAnimationFrame(update); } }, { passive: true });
    update();
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".toast-item").forEach(arm);
    document.querySelectorAll("form[data-guard], form[method='post']:not([data-no-guard])").forEach(guardSubmit);
    passwordToggles(document);
    headerShadow();
  });
})();
