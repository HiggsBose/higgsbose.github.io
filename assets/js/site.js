"use strict";
// Navigation is fully visible without JS. Enhancement adds a compact mobile menu.
document.documentElement.classList.add("js");
const menu = document.querySelector(".menu-toggle");
const nav = document.querySelector(".primary-nav");
function closeMenu() {
  menu.setAttribute("aria-expanded", "false");
  nav.classList.remove("is-open");
  menu.querySelector("span").textContent = "+";
}
menu?.addEventListener("click", () => {
  const expanded = menu.getAttribute("aria-expanded") !== "true";
  menu.setAttribute("aria-expanded", String(expanded));
  nav.classList.toggle("is-open", expanded);
  menu.querySelector("span").textContent = expanded ? "−" : "+";
});
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && menu?.getAttribute("aria-expanded") === "true") {
    closeMenu();
    menu.focus();
  }
});
nav?.addEventListener("click", (event) => {
  if (event.target.closest("a")) closeMenu();
});
// Keep old bookmarks useful after migrating the former single-page site.
const legacySections = {
  "#-educations": "cv/", "#-honors-and-awards": "cv/", "#cv": "cv/",
  "#-news": "news/", "#-main-publications": "publications/",
  "#-collaborative-publications": "publications/", "#-oral-presentations": "talks/",
  "#-projects": "projects/", "#-internships": "cv/", "#-services": "cv/"
};
if (document.body.dataset.page === "about" && legacySections[location.hash]) {
  location.replace(new URL(legacySections[location.hash], document.querySelector(".wordmark").href));
}
// Native dialog provides keyboard focus handling and Escape-to-close.
const figures = document.querySelectorAll(".paper-box-image img");
if (figures.length && typeof HTMLDialogElement !== "undefined") {
  const dialog = document.createElement("dialog");
  dialog.className = "image-dialog";
  dialog.setAttribute("aria-label", "Research figure preview");
  const close = document.createElement("button");
  close.type = "button";
  close.className = "dialog-close";
  close.textContent = "Close ×";
  const preview = document.createElement("img");
  dialog.append(close, preview);
  document.body.append(dialog);
  close.addEventListener("click", () => dialog.close());
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) {
      const box = dialog.getBoundingClientRect();
      if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) dialog.close();
    }
  });
  figures.forEach((figure) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "figure-button";
    button.setAttribute("aria-label", `Enlarge ${figure.alt}`);
    figure.replaceWith(button);
    button.append(figure);
    button.addEventListener("click", () => {
      preview.src = figure.src;
      preview.alt = figure.alt;
      dialog.showModal();
    });
  });
}
