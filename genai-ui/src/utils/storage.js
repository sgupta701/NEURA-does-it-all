// GENAI_ASSISTANT/genai-ui/src/utils/storage.js

export const saveConversation = (title, messages) => {
  const history = JSON.parse(localStorage.getItem("chatHistory") || "{}");
  history[title] = messages;
  localStorage.setItem("chatHistory", JSON.stringify(history));
};

export const loadConversation = (title) => {
  const history = JSON.parse(localStorage.getItem("chatHistory") || "{}");
  return history[title] || [];
};

export const getAllConversationTitles = () => {
  const history = JSON.parse(localStorage.getItem("chatHistory") || "{}");
  return Object.keys(history);
};

export const deleteConversation = (title) => {
  const history = JSON.parse(localStorage.getItem("chatHistory") || "{}");
  delete history[title];
  localStorage.setItem("chatHistory", JSON.stringify(history));
};
