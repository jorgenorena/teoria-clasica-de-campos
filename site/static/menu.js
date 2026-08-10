(() => {
  const button = document.getElementById("menu-toggle");
  const sidebar = document.getElementById("site-sidebar");
  const layout = document.querySelector(".layout");

  if (!button || !sidebar || !layout) return;

  const openMenu = () => {
    document.body.classList.add("menu-open");
    button.setAttribute("aria-expanded", "true");
  };

  const closeMenu = () => {
    document.body.classList.remove("menu-open");
    button.setAttribute("aria-expanded", "false");
  };

  const toggleMenu = () => {
    if (document.body.classList.contains("menu-open")) {
      closeMenu();
    } else {
      openMenu();
    }
  };

  button.addEventListener("click", (event) => {
    event.stopPropagation();
    toggleMenu();
  });

  sidebar.addEventListener("click", (event) => {
    const target = event.target;

    if (target instanceof HTMLAnchorElement) {
      closeMenu();
    }
  });

  document.addEventListener("click", (event) => {
    if (!document.body.classList.contains("menu-open")) return;

    const target = event.target;

    if (!(target instanceof Node)) return;
    if (sidebar.contains(target) || button.contains(target)) return;

    closeMenu();
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeMenu();
    }
  });

  const measureLength = (value) => {
    const probe = document.createElement("div");
    probe.style.position = "absolute";
    probe.style.visibility = "hidden";
    probe.style.pointerEvents = "none";
    probe.style.boxSizing = "border-box";
    probe.style.width = value;
    document.body.appendChild(probe);
    const width = probe.getBoundingClientRect().width;
    probe.remove();
    return width;
  };

  const updateLayout = () => {
    const rootStyle = getComputedStyle(document.documentElement);
    const layoutStyle = getComputedStyle(layout);
    const navWidth = measureLength(rootStyle.getPropertyValue("--nav-width"));
    const pageWidth = measureLength(rootStyle.getPropertyValue("--page-width"));
    const gap = parseFloat(layoutStyle.columnGap) || 0;
    const requiredWidth = Math.ceil(navWidth + gap + pageWidth);
    const availableWidth = document.documentElement.clientWidth;
    const shouldCollapse = availableWidth < requiredWidth;

    document.body.classList.toggle("layout-collapsed", shouldCollapse);
    document.body.classList.add("layout-measured");

    if (!shouldCollapse) {
      closeMenu();
    }
  };

  window.addEventListener("resize", updateLayout);
  updateLayout();

  if (document.fonts) {
    document.fonts.ready.then(updateLayout);
  }
})();
