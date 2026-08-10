(() => {
  const key = "theme";
  const root = document.documentElement;
  const button = document.getElementById("theme-toggle");
  const label = button?.querySelector(".theme-toggle-label");

  const updateButton = (theme) => {
    if (!label) return;
    label.textContent = theme === "dark" ? "light" : "dark";
    button?.setAttribute(
      "aria-label",
      `Switch to ${theme === "dark" ? "light" : "dark"} mode`,
    );
  };

  const applyTheme = (theme) => {
    root.setAttribute("data-theme", theme);
    localStorage.setItem(key, theme);
    updateButton(theme);
  };

  const saved = localStorage.getItem(key);
  applyTheme(saved || "dark");

  button?.addEventListener("click", () => {
    const current = root.getAttribute("data-theme") || "dark";
    applyTheme(current === "dark" ? "light" : "dark");
  });
})();
