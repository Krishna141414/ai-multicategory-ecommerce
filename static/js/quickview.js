/* Quick view: one floating card shared by the whole store.
   - Hover a card marked [data-qv-hover] for 150 ms (mouse only) and it opens next to the card.
   - Click / tap / Enter on any [data-quick-view="<url>"] button opens it and moves focus inside.
   - Esc, a click outside, or leaving the card and panel closes it (focus returns to the button).
   The card HTML comes from /product/<id>/quick-view/ and is cached per product.
   Fires "qv:open" / "qv:close" on document so the sponsored strip can pause. */
(function () {
  "use strict";
  const Chowk = window.Chowk || {};
  const HOVER_INTENT_MS = 150;
  const CLOSE_DELAY_MS = 220;
  const GAP = 10;
  const cache = new Map();
  const sheet = window.matchMedia("(max-width: 575.98px)"); // phones: bottom sheet, no anchoring
  let panel, content, trigger = null, openTimer = 0, closeTimer = 0, openedByHover = false;

  function build() {
    panel = document.createElement("div");
    panel.className = "qv-panel";
    panel.setAttribute("role", "dialog");
    panel.setAttribute("aria-modal", "false");
    panel.setAttribute("data-testid", "quick-view-panel");
    panel.hidden = true;
    panel.innerHTML = '<button type="button" class="qv-close" aria-label="Close quick view" data-testid="quick-view-close"><i class="bi bi-x-lg" aria-hidden="true"></i></button><div class="qv-content"></div>';
    content = panel.querySelector(".qv-content");
    document.body.append(panel);
    panel.querySelector(".qv-close").addEventListener("click", () => close({ restoreFocus: true }));
    panel.addEventListener("pointerenter", () => window.clearTimeout(closeTimer));
    panel.addEventListener("pointerleave", (e) => { if (e.pointerType === "mouse" && openedByHover) scheduleClose(); });
  }

  function load(url) {
    if (!cache.has(url)) {
      cache.set(url, fetch(url, { credentials: "same-origin" }).then((r) => {
        if (!r.ok) throw new Error(String(r.status));
        return r.text();
      }).catch((err) => { cache.delete(url); throw err; }));
    }
    return cache.get(url);
  }

  function position() {
    if (!trigger || panel.hidden || sheet.matches) { panel.style.removeProperty("top"); panel.style.removeProperty("left"); return; }
    const anchor = trigger.closest("[data-qv-anchor]") || trigger;
    const r = anchor.getBoundingClientRect();
    if (r.bottom < 0 || r.top > window.innerHeight) { close(); return; }
    const w = panel.offsetWidth, h = panel.offsetHeight;
    const header = document.querySelector(".site-header");
    const minTop = (header ? header.getBoundingClientRect().bottom : 0) + GAP; // never cover the sticky header
    const maxTop = window.innerHeight - h - GAP;
    const clampLeft = (v) => Math.min(Math.max(GAP, v), window.innerWidth - w - GAP);
    const clampTop = (v) => Math.min(Math.max(minTop, v), Math.max(minTop, maxTop));
    let top, left;
    if (r.bottom + GAP <= maxTop) { top = r.bottom + GAP; left = clampLeft(r.left + r.width / 2 - w / 2); }              // below
    else if (r.top - h - GAP >= minTop) { top = r.top - h - GAP; left = clampLeft(r.left + r.width / 2 - w / 2); }       // above
    else if (r.right + GAP + w <= window.innerWidth - GAP) { top = clampTop(r.top); left = r.right + GAP; }               // right of the card
    else if (r.left - GAP - w >= GAP) { top = clampTop(r.top); left = r.left - GAP - w; }                                 // left of the card
    else { top = clampTop(r.bottom + GAP); left = clampLeft(r.left + r.width / 2 - w / 2); }
    panel.style.top = `${Math.round(top)}px`;
    panel.style.left = `${Math.round(left)}px`;
  }

  async function open(button, { hover = false } = {}) {
    window.clearTimeout(closeTimer);
    if (trigger === button && !panel.hidden) return;
    if (trigger && trigger !== button) trigger.setAttribute("aria-expanded", "false");
    trigger = button;
    openedByHover = hover;
    button.setAttribute("aria-expanded", "true");
    content.innerHTML = '<div class="qv qv--loading" aria-hidden="true"><span class="skeleton qv-media"></span><span class="qv-body"><span class="skeleton skeleton-line"></span><span class="skeleton skeleton-line"></span><span class="skeleton skeleton-line short"></span></span></div>';
    panel.hidden = false;
    panel.classList.remove("is-open");
    void panel.offsetWidth; // restart the enter transition
    panel.classList.add("is-open");
    position();
    document.dispatchEvent(new CustomEvent("qv:open"));
    let html;
    try {
      html = await load(button.dataset.quickView);
    } catch (err) {
      if (trigger !== button) return;
      content.innerHTML = '<p class="qv-error">Couldn’t load this product. <a href="' + (button.dataset.href || "#") + '">Open the product page</a>.</p>';
      return;
    }
    if (trigger !== button || panel.hidden) return; // the user moved on while it loaded
    content.innerHTML = html;
    const title = content.querySelector(".qv-name");
    if (title) panel.setAttribute("aria-labelledby", title.id);
    content.querySelectorAll("form[data-add-to-cart]").forEach((f) => Chowk.bindAddToCart && Chowk.bindAddToCart(f));
    position();
    if (!hover) (content.querySelector(".qv-actions .btn") || panel.querySelector(".qv-close")).focus();
  }

  function close({ restoreFocus = false } = {}) {
    window.clearTimeout(openTimer);
    window.clearTimeout(closeTimer);
    if (!panel || panel.hidden) return;
    panel.hidden = true;
    panel.classList.remove("is-open");
    const last = trigger;
    trigger = null;
    if (last) {
      last.setAttribute("aria-expanded", "false");
      if (restoreFocus) last.focus();
    }
    document.dispatchEvent(new CustomEvent("qv:close"));
  }

  function scheduleClose() {
    window.clearTimeout(closeTimer);
    closeTimer = window.setTimeout(() => close(), CLOSE_DELAY_MS);
  }

  document.addEventListener("DOMContentLoaded", () => {
    build();

    document.addEventListener("click", (e) => {
      const button = e.target.closest("[data-quick-view]");
      if (button) { e.preventDefault(); open(button); return; }
      if (!panel.hidden && !panel.contains(e.target)) close();
    });

    // hover intent, mouse only (touch and pen use the button)
    document.addEventListener("pointerover", (e) => {
      if (e.pointerType !== "mouse") return;
      const card = e.target.closest("[data-qv-hover]");
      if (!card || card.contains(e.relatedTarget)) return;
      const button = card.querySelector("[data-quick-view]");
      if (!button) return;
      window.clearTimeout(closeTimer);
      window.clearTimeout(openTimer);
      openTimer = window.setTimeout(() => open(button, { hover: true }), HOVER_INTENT_MS);
    });
    document.addEventListener("pointerout", (e) => {
      if (e.pointerType !== "mouse") return;
      const card = e.target.closest("[data-qv-hover]");
      if (!card || card.contains(e.relatedTarget)) return;
      window.clearTimeout(openTimer);
      if (openedByHover && !panel.contains(e.relatedTarget)) scheduleClose();
    });

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && !panel.hidden) { e.preventDefault(); close({ restoreFocus: true }); }
    });
    panel.addEventListener("focusout", (e) => {
      if (e.relatedTarget && !panel.contains(e.relatedTarget) && e.relatedTarget !== trigger) close();
    });
    window.addEventListener("scroll", () => window.requestAnimationFrame(position), { passive: true });
    window.addEventListener("resize", () => window.requestAnimationFrame(position));
  });

  Chowk.closeQuickView = close;
})();
