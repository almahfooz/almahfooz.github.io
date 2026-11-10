(() => {
  const button = document.querySelector(".nav-toggle");
  const menu = document.getElementById("mobile-menu");
  if (button && menu) {
    function setOpen(open) {
      menu.hidden = !open;
      button.setAttribute("aria-expanded", String(open));
      button.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    }
    button.addEventListener("click", () => setOpen(menu.hidden));
    document.addEventListener("keydown", e => {
      if (e.key === "Escape" && !menu.hidden) { setOpen(false); button.focus(); }
    });
    matchMedia("(min-width: 751px)").addEventListener("change", e => { if (e.matches) setOpen(false); });
  }
  const form = document.getElementById("email-enquiry");
  if (form) {
    const select = form.elements.namedItem("service");
    const selected = new URLSearchParams(location.search).get("service");
    if ([...select.options].some(option => option.value === selected)) select.value = selected;
    form.addEventListener("submit", event => {
      event.preventDefault();
      const fields = new FormData(form);
      const subject = "Research enquiry · " + select.selectedOptions[0].textContent.trim();
      const body = String(fields.get("message")).trim() + "\n\n" + String(fields.get("name")).trim()
        + (fields.get("email") ? "\n" + fields.get("email") : "");
      location.href = "mailto:get2almahfooz@gmail.com?subject=" + encodeURIComponent(subject)
        + "&body=" + encodeURIComponent(body);
    });
  }
})();
