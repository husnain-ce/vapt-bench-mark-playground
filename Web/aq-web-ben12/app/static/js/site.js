const wirePreviewForms = () => {
  document.querySelectorAll("[data-async-target]").forEach((form) => {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const target = document.querySelector(form.dataset.asyncTarget);
      const response = await fetch(form.action, {
        method: form.method || "POST",
        body: new FormData(form),
        credentials: "same-origin",
      });
      target.innerHTML = await response.text();
    });
  });
};

const wireSearchHints = () => {
  const search = document.querySelector('.search-bar input[name="q"]');
  if (!search) {
    return;
  }
  let hint;
  search.addEventListener("input", async () => {
    const value = search.value.trim();
    if (value.length < 2) {
      if (hint) {
        hint.remove();
        hint = null;
      }
      return;
    }
    const response = await fetch(`/api/search?q=${encodeURIComponent(value)}`);
    const items = await response.json();
    if (!hint) {
      hint = document.createElement("div");
      hint.className = "search-hint";
      search.parentNode.appendChild(hint);
    }
    hint.innerHTML = items.map((item) => `<span>${item.title}</span>`).join("");
    if (!items.length) {
      hint.innerHTML = "<span>No public hits</span>";
    }
  });
};

document.addEventListener("DOMContentLoaded", () => {
  wirePreviewForms();
  wireSearchHints();
});
