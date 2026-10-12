import { API_URL } from "../config";
import React, { useEffect, useRef, useState } from 'react';

type Message = {
  from: 'user' | 'bot';
  text: string;
};

// The model sometimes adds Markdown anyway; strip markers as the text is shown
const plainText = (text: string) =>
  text.replace(/\*\*|__/g, '').replace(/^\s{0,3}#{1,6}\s*/gm, '');

// Typing speed: at least one character per tick, faster when far behind the stream
const TICK_MS = 20;
const CATCH_UP = 15;

const Chatbot: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  // The reply being typed: null when idle, '' while waiting for the first words
  const [typed, setTyped] = useState<string | null>(null);
  const [streamDone, setStreamDone] = useState(false);
  const received = useRef('');
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight });
  }, [messages, typed]);

  const typing = typed !== null;

  // Reveal the received text a few characters at a time, like someone typing
  useEffect(() => {
    if (!typing) return;
    const timer = setInterval(() => {
      setTyped((shown) => {
        if (shown === null) return shown;
        const behind = received.current.length - shown.length;
        if (behind <= 0) return shown;
        const step = Math.max(1, Math.ceil(behind / CATCH_UP));
        return received.current.slice(0, shown.length + step);
      });
    }, TICK_MS);
    return () => clearInterval(timer);
  }, [typing]);

  // When the stream has ended and everything is shown, keep it as a normal message
  useEffect(() => {
    if (!streamDone || typed === null || typed.length < received.current.length) return;
    const text = plainText(received.current).trim();
    setMessages((prev) => [
      ...prev,
      { from: 'bot', text: text || 'Sorry, I could not understand your question.' },
    ]);
    setTyped(null);
    setStreamDone(false);
    setSending(false);
  }, [streamDone, typed]);

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
    received.current = '';
    setTyped('');

    try {
      const res = await fetch(`${API_URL}/api/bot/ask/stream/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      });
      if (!res.ok || !res.body) throw new Error(`Status ${res.status}`);
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      for (;;) {
        const { done, value } = await reader.read();
        if (done) break;
        received.current += decoder.decode(value, { stream: true });
      }
      received.current += decoder.decode();
    } catch (error) {
      console.error('Error contacting backend:', error);
      if (!received.current) {
        received.current = 'Something went wrong. Please try again later.';
      }
    } finally {
      setStreamDone(true);
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

          <div
            ref={listRef}
            className="flex-1 space-y-2 overflow-y-auto bg-stone-50 p-4"
            aria-live="polite"
          >
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
            {typed !== null && (
              <div
                className="mr-auto max-w-[80%] whitespace-pre-line rounded-lg border border-stone-200 bg-white px-3 py-2 text-sm text-stone-800"
                // Screen readers hear the finished reply once, not every typing step
                aria-hidden
              >
                {typed === '' ? (
                  <span className="typing-dots">
                    <span />
                    <span />
                    <span />
                  </span>
                ) : (
                  <>
                    {plainText(typed)}
                    <span className="typing-cursor" aria-hidden />
                  </>
                )}
              </div>
            )}
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
