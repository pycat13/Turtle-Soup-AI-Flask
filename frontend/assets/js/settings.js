function initSettings() {
  const current = I18N.getLang();
  const zh = document.getElementById("lang-zh");
  const en = document.getElementById("lang-en");
  if (current === "en") en.checked = true;
  else zh.checked = true;

  document.getElementById("save-btn").addEventListener("click", () => {
    const lang = en.checked ? "en" : "zh";
    I18N.setLang(lang);
    const params = new URLSearchParams(window.location.search);
    const redirect = params.get("redirect") || "/";
    window.location.href = redirect;
  });
}

window.addEventListener("DOMContentLoaded", initSettings);

