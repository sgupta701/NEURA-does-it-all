// GENAI_ASSISTANT/genai-ui/src/Sidebar.jsx

function Sidebar({ conversations = [], onSelect, onNew }) {
  return (
    <div className="sidebar">
      <button className="new-chat-btn" onClick={onNew}>+ New Chat</button>
      {conversations.map((conv, idx) => (
        <div 
          key={idx}
          className="chat-item"
          onClick={() => onSelect(conv)}
        >
          {conv.title || `Conversation ${idx + 1}`}
        </div>
      ))}
    </div>
  );
}

export default Sidebar;
