/**
 * Rule-based assistant client — POSTs to /chatbot/message/
 */
(function () {
  const toggle = document.getElementById("chatbot-toggle");
  const panel = document.getElementById("chatbot-panel");
  const form = document.getElementById("chatbot-form");
  const input = document.getElementById("chatbot-input");
  const messages = document.getElementById("chatbot-messages");

  function getCookie(name) {
    const v = document.cookie.match("(^|;) ?" + name + "=([^;]*)(;|$)");
    return v ? decodeURIComponent(v[2]) : null;
  }

  function appendBubble(text, who) {
    const div = document.createElement("div");
    div.className =
      who === "user"
        ? "ml-8 rounded-lg bg-teal-50 px-3 py-2 text-right text-slate-800"
        : "mr-8 rounded-lg bg-slate-100 px-3 py-2 text-slate-800";
    div.textContent = text;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
  }

  if (!toggle || !panel || !form) return;

  toggle.addEventListener("click", function () {
    panel.classList.toggle("hidden");
  });

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    const text = (input.value || "").trim();
    if (!text) return;
    appendBubble(text, "user");
    input.value = "";

    const headers = { "Content-Type": "application/json" };
    const csrftoken = getCookie("csrftoken");
    if (csrftoken) headers["X-CSRFToken"] = csrftoken;

    fetch("/chatbot/message/", {
      method: "POST",
      headers: headers,
      credentials: "same-origin",
      body: JSON.stringify({ message: text }),
    })
      .then(function (r) {
        return r.json();
      })
      .then(function (data) {
        if (data.reply) appendBubble(data.reply, "bot");
        if (data.actions && data.actions.length) {
          const wrap = document.createElement("div");
          wrap.className = "mr-8 flex flex-wrap gap-2";
          data.actions.forEach(function (a) {
            const link = document.createElement("a");
            link.href = a.url;
            link.textContent = a.label;
            link.className =
              "rounded-md border border-teal-200 bg-white px-2 py-1 text-xs font-medium text-teal-900 hover:bg-teal-50";
            wrap.appendChild(link);
          });
          messages.appendChild(wrap);
        }
      })
      .catch(function () {
        appendBubble("Sorry, something went wrong. Try again.", "bot");
      });
  });
})();
