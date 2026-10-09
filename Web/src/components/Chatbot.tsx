import { API_URL } from "../config";
import React, { useEffect, useRef, useState } from 'react';

type Message = {
  from: 'user' | 'bot';
  text: string;
};

const Chatbot: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight });
  }, [messages]);

  const toggleChat = () => {
    setIsOpen(!isOpen);
    if (!isOpen) {
      setMessages([
        {
          from: 'bot',
          text: 'Hello, I am the AgroSmart assistant. Ask me anything about farming.',
        },
      ]);
    }
  };

  const sendMessage = async () => {
    if (input.trim() === '' || sending) return;
    const question = input;
    setMessages((prev) => [...prev, { from: 'user', text: question }]);
    setInput('');
    setSending(true);

    try {
      const res = await fetch(`${API_URL}/api/bot/ask/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        { from: 'bot', text: data.answer || 'Sorry, I could not understand your question.' },
      ]);
    } catch (error) {
      console.error('Error contacting backend:', error);
      setMessages((prev) => [
        ...prev,
        { from: 'bot', text: 'Something went wrong. Please try again later.' },
      ]);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {isOpen ? (
        <div className="card flex h-[28rem] w-[22rem] max-w-[calc(100vw-2rem)] flex-col overflow-hidden shadow-xl">
          <div className="flex items-center justify-between border-b border-stone-200 px-4 py-3">
            <div>
              <p className="text-sm font-semibold text-stone-900">Ask AgroSmart</p>
              <p className="text-xs text-stone-500">Farming questions and advice</p>
            </div>
            <button onClick={toggleChat} className="btn-ghost px-2 py-1 text-xs">
              Close
            </button>
          </div>

          <div ref={listRef} className="flex-1 space-y-2 overflow-y-auto bg-stone-50 p-4">
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`max-w-[80%] whitespace-pre-line rounded-lg px-3 py-2 text-sm ${
                  msg.from === 'user'
                    ? 'ml-auto bg-primary text-white'
                    : 'mr-auto border border-stone-200 bg-white text-stone-800'
                }`}
              >
                {msg.text}
              </div>
            ))}
            {sending && <p className="muted">Replying…</p>}
          </div>

          <div className="flex gap-2 border-t border-stone-200 bg-white p-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Type your question"
              className="input"
            />
            <button onClick={sendMessage} disabled={sending} className="btn-primary">
              Send
            </button>
          </div>
        </div>
      ) : (
        <button onClick={toggleChat} className="btn-primary rounded-full px-5 py-3 shadow-lg">
          Ask a question
        </button>
      )}
    </div>
  );
};

export default Chatbot;
