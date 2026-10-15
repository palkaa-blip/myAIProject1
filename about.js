const chatPanel = document.querySelector("#chat-panel");
const chatLauncher = document.querySelector("#chat-launcher");
const chatClose = document.querySelector("#chat-close");
const chatForm = document.querySelector("#chat-form");
const chatInput = document.querySelector("#chat-input");
const chatMessages = document.querySelector("#chat-messages");
const sendButton = chatForm.querySelector('button[type="submit"]');

function setChatOpen(isOpen) {
  chatPanel.hidden = !isOpen;
  chatPanel.setAttribute("aria-hidden", String(!isOpen));
  chatLauncher.setAttribute("aria-expanded", String(isOpen));

  if (isOpen) {
    chatInput.focus();
  } else {
    chatLauncher.focus();
  }
}

function addMessage(message, sender) {
  const messageElement = document.createElement("p");
  messageElement.className = `chat-message chat-message-${sender}`;
  messageElement.textContent = message;
  chatMessages.append(messageElement);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function sendMessage(message) {
  const cleanedMessage = message.trim();

  if (!cleanedMessage) {
    return;
  }

  addMessage(cleanedMessage, "user");
  sendButton.disabled = true;

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: cleanedMessage })
    });
    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.error || `Chat request failed (${response.status}).`);
    }

    if (typeof result.reply !== "string" || !result.reply) {
      throw new Error("The chat server returned an invalid reply.");
    }

    addMessage(result.reply, "bot");
  } catch (error) {
    const reason = error instanceof TypeError
      ? "Can't reach the Python chat server. Start it with python app.py and try again."
      : `Chat error: ${error.message}`;
    addMessage(reason, "bot");
  } finally {
    sendButton.disabled = false;
  }
}

chatLauncher.addEventListener("click", () => {
  setChatOpen(chatPanel.hidden);
});

chatClose.addEventListener("click", () => {
  setChatOpen(false);
});

chatForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const message = chatInput.value;
  chatForm.reset();
  chatInput.focus();
  sendMessage(message);
});

document.querySelectorAll(".chat-suggestions [data-question]").forEach((button) => {
  button.addEventListener("click", () => {
    sendMessage(button.dataset.question);
    chatInput.focus();
  });
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !chatPanel.hidden) {
    setChatOpen(false);
  }
});
