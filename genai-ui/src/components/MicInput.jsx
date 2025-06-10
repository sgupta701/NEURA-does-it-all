// GENAI_ASSISTANT/genai_ui/src/components/MicInput.jsx

import { useState, useRef } from "react";

export default function MicInput({ onTranscript }) {
  const recognitionRef = useRef(null);
  const [isListening, setIsListening] = useState(false);

  const handleMicClick = () => {
    if (!isListening) {
      const recognition = new window.webkitSpeechRecognition();
      recognition.lang = "en-US";
      recognition.continuous = true;
      recognition.interimResults = true;

      recognition.onresult = (event) => {
        let finalTranscript = "";
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          const result = event.results[i];
          if (result.isFinal) {
            finalTranscript += result[0].transcript;
          }
        }

        if (finalTranscript) {
          onTranscript(finalTranscript.trim()); 
        }
      };

      recognition.onerror = (e) => console.error("Speech error", e);
      recognition.onend = () => setIsListening(false); 

      recognition.start();
      recognitionRef.current = recognition;
      setIsListening(true);
    } else {
      recognitionRef.current?.stop();
      setIsListening(false);
    }
  };

  return (
    <button onClick={handleMicClick} className="mic-button">
      {isListening ? "🛑 Stop" : "🎙️"}
    </button>
  );
}
