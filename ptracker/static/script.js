const app = {
  initTheme: () => {
    const html = document.documentElement;
    const themeToggle = document.querySelector(".header__theme");

    if (themeToggle) {
      themeToggle.addEventListener("click", () => {
        const isDark = html.classList.toggle("dark-theme");
        localStorage.setItem("theme", isDark ? "dark" : "light");
      });
    }
  },

  initSidebar: () => {
    const menu = document.querySelector(".header__menu-toggle");
    const sidebar = document.querySelector(".sidebar");

    if (!menu || !sidebar) return;

    menu.addEventListener("click", () => {
      sidebar.classList.toggle("open");
      menu.classList.toggle("open");
      menu.setAttribute("aria-expanded", menu.classList.contains("open"));
    });
  },

  initDemo: () => {
    const demoBtn = document.querySelector(".auth__demo__button");

    if (!demoBtn) return;

    demoBtn.addEventListener("click", async () => {
      try {
        const res = await fetch("/auth/demo", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
        });

        if (!res.ok) {
          const errorData = await res.json();
          console.error("Demo failed:", errorData.message || "Unknown error");
          return;
        }

        const data = await res.json();
        if (data.success && data.redirect) {
          window.location.href = data.redirect;
        }
      } catch (err) {
        console.error("Demo request failed:", err);
      }
    });
  },
};

document.addEventListener("DOMContentLoaded", () => {
  app.initTheme();
  app.initSidebar();
  app.initDemo();

  document.querySelectorAll(".alert").forEach((alert) => {
    setTimeout(() => {
      alert.classList.add("alert-fade");

      alert.addEventListener(
        "transitionend",
        () => {
          alert.remove();
        },
        { once: true },
      );
    }, 4000);
  });

  document
    .getElementById("slider-toggle-email")
    ?.addEventListener("change", async (e) => {
      const enabled = e.target.checked;
      console.log("Toggleing notifications");
      await fetch("/api/user/notifications", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ enabled }),
      });
    });

  document.querySelectorAll("[data-item-toggle]").forEach((toggle) => {
    toggle.addEventListener("change", async (e) => {
      const itemId = e.target.dataset.itemId;
      const enabled = e.target.checked;
      console.log(`Toggling notifications for item ${itemId} to ${enabled}`);
      await fetch(`/api/items/${itemId}/notifications`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ enabled }),
      });
    });
  });
});
