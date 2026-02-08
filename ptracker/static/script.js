const html = document.documentElement;
const sun = document.querySelector(".fa-sun");
const moon = document.querySelector(".fa-moon");
const sidebar = document.querySelector(".sidebar");
const menu = document.querySelector(".header__menu-toggle");

const storedTheme = localStorage.getItem("theme");
// const prefersDark = false;
const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;

if (storedTheme === "dark" || (!storedTheme && prefersDark)) {
  html.classList.add("dark-theme");
  sun.style.display = "block";
  moon.style.display = "none";
} else {
  sun.style.display = "none";
  moon.style.display = "block";
}

sun.addEventListener("click", () => {
  html.classList.remove("dark-theme");
  //   localStorage.setItem("theme", "light");
  sun.style.display = "none";
  moon.style.display = "block";
});

moon.addEventListener("click", () => {
  html.classList.add("dark-theme");
  //   localStorage.setItem("theme", "dark");
  sun.style.display = "block";
  moon.style.display = "none";
});

menu.addEventListener("click", () => {
  sidebar.classList.toggle("open");
  menu.classList.toggle("open");
  menu.setAttribute("aria-expanded", menu.classList.contains("open"));
});
