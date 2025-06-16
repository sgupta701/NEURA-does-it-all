// GENAI_ASSISTANT/genai-ui/src/App.jsx 

import { useState, useEffect, useRef } from "react";
import "./App.css";
import TextareaAutosize from "react-textarea-autosize";
import EmojiPicker from "emoji-picker-react";
import "prismjs/themes/prism.css";
import { getAuthHeaders } from "./utils/auth";

import Sidebar from "./components/Sidebar";
import ChatBubble from "./components/ChatBubble";
import MicInput from "./components/MicInput";

import logo from "./assets/logo.png";
import neuraText from "./assets/neura-text.png";

function App() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: "assistant",
      text: "Hi! I’m Neura, your GenAI assistant. How can I help you today?",
      timestamp: new Date().toLocaleTimeString(),
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [darkMode, setDarkMode] = useState(true);
  const [showEmoji, setShowEmoji] = useState(false);
  const [conversationSaved, setConversationSaved] = useState(false);

  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

    if (speechSynthesis.onvoiceschanged !== undefined) {
      speechSynthesis.onvoiceschanged = () => {
        speechSynthesis.getVoices();
      };
    } else {
      speechSynthesis.getVoices();
    }

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = {
      id: Date.now(),
      role: "user",
      text: input,
      timestamp: new Date().toLocaleTimeString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({ text: input }),
      });

      const data = await response.json();
      const assistantReply = data.answers.join("\n") || "Sorry, no response.";

      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: "assistant",
          text: assistantReply,
          timestamp: new Date().toLocaleTimeString(),
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: "assistant",
          text: "❌ Error contacting server.",
          timestamp: new Date().toLocaleTimeString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const onKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const exportChat = () => {
    const data = JSON.stringify(messages, null, 2);
    const blob = new Blob([data], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "chat-history.json";
    link.click();
  };

  return (
    <div className={`app-container ${darkMode ? "dark" : ""}`}>
      <Sidebar
        messages={messages}
        setMessages={setMessages}
        conversationSaved={conversationSaved}
        setConversationSaved={setConversationSaved}
        setInput={setInput}
      />
      <div className="chat-area">
        <div className="flex flex-col h-full w-full p-4">
          <header
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "25px",
              marginTop: "15px",
              padding: "0 10px",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <img src={logo} alt="Neura Logo" style={{ height: "60px", objectFit: "contain" }} />
              <img src={neuraText} alt="Neura Text" style={{ height: "40px", objectFit: "contain" }} />
            </div>

            <div>
              <button onClick={exportChat} style={{ marginLeft: "10px" }}>
                Export Chat
              </button>
            </div>
          </header>

          <main className="chat-window">
            {messages.map(({ id, role, text, timestamp }) => (
              <ChatBubble key={id} role={role} text={text} timestamp={timestamp} />
            ))}

            {loading && (
              <ChatBubble
                role="assistant"
                text="Typing..."
                timestamp={new Date().toLocaleTimeString()}
              />
            )}
            
            <div ref={messagesEndRef} />
          </main>

          <footer className="footer-container">
            <div className="footer-input-area">
              <MicInput
                onTranscript={(text) => setInput((prev) => prev + " " + text)}
              />

              <button onClick={() => setShowEmoji(!showEmoji)}>😊</button>
              {showEmoji && (
                <div className="emoji-picker-wrapper">
                  <EmojiPicker
                    onEmojiClick={(emojiObject) =>
                      setInput((prev) => prev + emojiObject.emoji)
                    }
                  />
                </div>
              )}

              <TextareaAutosize
                rows={1}
                placeholder="Type your message..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={onKeyDown}
                className="input-box"
              />

              <button className="send-button" onClick={sendMessage} >
                {loading ? "Sending..." : "Send"}
              </button>
            </div>
          </footer>
        </div>
      </div>
    </div>
  );
}

export default App;
