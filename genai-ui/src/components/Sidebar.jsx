// GENAI_ASSISTANT/genai_ui/src/components/Sidebar.jsx

import React, { useState, useEffect } from "react";
import {
  saveConversation,
  loadConversation,
  getAllConversationTitles,
} from "../utils/storage";
import "./Sidebar.css";
import { deleteConversation } from "../utils/storage"; 

function Sidebar({
  conversations,
  messages,
  setMessages,
  conversationSaved,
  setConversationSaved,
  setInput,
}) {
  const [menuOpenId, setMenuOpenId] = useState(null);
  const [localConversations, setLocalConversations] = useState(conversations || []);

  useEffect(() => {
    refreshConversations();
  }, [conversations]);

  const refreshConversations = () => {
    const titles = getAllConversationTitles();
    setLocalConversations(titles);
  };

  const handleSaveConversation = () => {
    if (!messages || messages.length === 0) return;

    const title = prompt("Enter a title for this conversation:");
    if (!title) return;

    saveConversation(title, messages);
    refreshConversations();
    setConversationSaved(true);
    alert(`Conversation saved as "${title}"`);
  };

  const handleLoadConversation = (title) => {
    const loadedMessages = loadConversation(title);
    if (loadedMessages) {
      setMessages(loadedMessages);
    } else {
      alert("Failed to load conversation.");
    }
  };

  const handleNewChat = () => {
    if (!conversationSaved && messages.length > 1) {
      const save = window.confirm("Save current conversation before starting a new chat?");
      if (save) {
        const title = prompt("Enter a title for this conversation:");
        if (title) {
          saveConversation(title, messages);
          refreshConversations();
          alert(`Conversation saved as "${title}"`);
        }
      }
    }

    setMessages([
      {
        id: 1,
        role: "assistant",
        text: "Hi! I’m your GenAI assistant. How can I help you today?",
        timestamp: new Date().toLocaleTimeString(),
      },
    ]);
    if (setInput) setInput("");
    setConversationSaved(false);
  };

    const handleDeleteConversation = (title) => {
    const confirmDelete = window.confirm(`Are you sure you want to delete "${title}"?`);
    if (!confirmDelete) return;

    deleteConversation(title);  
    refreshConversations();
    };


  const handleRenameConversation = (oldTitle) => {
  const newTitle = prompt("Enter a new name for this conversation:", oldTitle);
  if (!newTitle || newTitle.trim() === "" || newTitle === oldTitle) return;

  const allTitles = getAllConversationTitles();
  if (allTitles.includes(newTitle)) {
    alert("A conversation with this name already exists.");
    return;
  }

  const oldData = loadConversation(oldTitle);
  if (!oldData) {
    alert("Could not load conversation for renaming.");
    return;
  }

  saveConversation(newTitle, oldData);
  deleteConversation(oldTitle);  
  refreshConversations();

  if (
    messages.length > 0 &&
    JSON.stringify(messages) === JSON.stringify(oldData)
  ) {
    alert(`Conversation renamed to "${newTitle}"`);
  }
};

  return (
    <div className="sidebar">
      <div className="sidebar-buttons">
        <button className="sidebar-btn" onClick={handleSaveConversation}>
          Save Conversation
        </button>
        <button className="sidebar-btn" onClick={handleNewChat}>
          ➕ New Chat
        </button>
      </div>

      <hr className="sidebar-divider" />

      <div className="conversation-list">
        {localConversations.map((title) => (
          <div
            key={title}
            className="conversation-bubble-wrapper"
          >
            <div className="conversation-bubble" onClick={() => handleLoadConversation(title)}>
              {title}
              <span
                className="three-dots"
                onClick={(e) => {
                  e.stopPropagation();
                  setMenuOpenId(title);
                }}
              >
                ⋮
              </span>
            </div>

            {menuOpenId === title && (
              <div className="conversation-menu">
                <div
                  onClick={() => {
                    handleRenameConversation(title);
                    setMenuOpenId(null);
                  }}
                >
                  📝 Rename
                </div>
                <div
                  onClick={() => {
                    handleDeleteConversation(title);
                    setMenuOpenId(null);
                  }}
                >
                  🗑️ Delete
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default Sidebar;
