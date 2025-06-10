// GENAI_ASSISTANT/genai_ui/src/components/ChatBubble.jsx

import { BotIcon } from "lucide-react";

function ChatBubble({ role, text }) {
  const isUser = role === "user";

  const stripEmojis = (str) =>
    str.replace(/[\p{Emoji_Presentation}\p{Extended_Pictographic}]/gu, "");

  const speak = () => {
    const cleanText = stripEmojis(text);
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = "en-US";

    const voices = speechSynthesis.getVoices();
    const femaleVoices = voices.filter((voice) =>
      ["female", "zira", "samantha", "google uk english female"].some((name) =>
        voice.name.toLowerCase().includes(name)
      )
    );

    utterance.voice = femaleVoices[0] || voices[0];
    speechSynthesis.speak(utterance);
  };

  const stop = () => {
    window.speechSynthesis.cancel();
  };

  const tags = (text.match(/#\w+/g) || []).map((tag, i) => (
    <span
      key={i}
      style={{
        fontSize: "0.7rem",
        marginRight: "0.4rem",
        marginBottom: "0.3rem",
        padding: "0.2rem 0.5rem",
        borderRadius: "9999px",
        backgroundColor: "#e5e7eb",
        color: "#374151",
        display: "inline-block",
      }}
    >
      {tag}
    </span>
  ));

  return (
    <div
      style={{
        display: "flex",
        justifyContent: isUser ? "flex-end" : "flex-start",
        padding: "0.5rem",
      }}
    >
      <div
        className={`chat-bubble ${isUser ? "user" : "assistant"}`}
        style={{
          position: "relative",
          maxWidth: "80%",
          backgroundColor: isUser ? "#dcfce7" : "#f3f4f6",
          color: "#111827",
          padding: "0.8rem 1rem",
          borderRadius: "1rem",
          borderTopRightRadius: isUser ? "0" : "1rem",
          borderTopLeftRadius: isUser ? "1rem" : "0",
          wordBreak: "break-word",
          whiteSpace: "pre-wrap",
          paddingRight: !isUser ? "2.5rem" : "1rem", 
        }}
      >
        {!isUser && (
          <div
            style={{
              position: "absolute",
              top: "8px",
              left: "-28px",
              display: "flex",
              alignItems: "center",
            }}
          >
            <BotIcon size={16} />
          </div>
        )}

        <div>{tags}</div>
        <div style={{ paddingRight: !isUser ? "2rem" : "0" }}>{text}</div>

        {!isUser && (
          <div
            style={{
              position: "absolute",
              top: "8px",
              right: "10px",
              display: "flex",
              gap: "6px",
              fontSize: "0.8rem",
              color: "#00aced",
              zIndex: 10,
              background: "#f3f4f6",
              borderRadius: "8px",
              padding: "2px 4px",
            }}
          >
            <button
              onClick={speak}
              style={{
                background: "transparent",
                border: "none",
                padding: 0,
                cursor: "pointer",
              }}
              aria-label="Play message"
            >
              🔊
            </button>
            <button
              onClick={stop}
              style={{
                background: "transparent",
                border: "none",
                padding: 0,
                cursor: "pointer",
              }}
              aria-label="Stop speech"
            >
              ⏹️
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default ChatBubble;
