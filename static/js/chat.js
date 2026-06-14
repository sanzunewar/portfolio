(function () {
  const launcher = document.getElementById("chat-launcher");
  const panel = document.getElementById("chat-panel");
  const closeBtn = document.getElementById("chat-close");
  const form = document.getElementById("chat-form");
  const input = document.getElementById("chat-input");
  const log = document.getElementById("chat-log");
  const sendBtn = form.querySelector("button");

  const csrfToken = document
    .querySelector('meta[name="csrf-token"]')
    .getAttribute("content");

  function openPanel() {
    panel.hidden = false;
    launcher.hidden = true;
    input.focus();
  }
  function closePanel() {
    panel.hidden = true;
    launcher.hidden = false;
  }

  launcher.addEventListener("click", openPanel);
  closeBtn.addEventListener("click", closePanel);
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !panel.hidden) closePanel();
  });

  function addMessage(text, kind) {
    const el = document.createElement("div");
    el.className = "msg " + kind;
    el.textContent = text;
    log.appendChild(el);
    log.scrollTop = log.scrollHeight;
    return el;
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const message = input.value.trim();
    if (!message) return;

    addMessage(message, "user");
    input.value = "";
    input.disabled = true;
    sendBtn.disabled = true;

    const typing = addMessage("…", "typing");

    try {
      const res = await fetch("/api/chat/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({ message }),
      });
      const data = await res.json();
      typing.remove();

      if (res.ok && data.reply) {
        addMessage(data.reply, "bot");
      } else {
        addMessage(data.error || "Something went wrong.", "error");
      }
    } catch (err) {
      typing.remove();
      addMessage("Couldn't reach the assistant. Check your connection.", "error");
    } finally {
      input.disabled = false;
      sendBtn.disabled = false;
      input.focus();
    }
  });
})();
