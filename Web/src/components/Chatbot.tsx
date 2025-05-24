import React, { useState } from 'react';
import { motion } from 'framer-motion';

type Message = {
  from: 'user' | 'bot';
  text: string;
};

const Chatbot: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');

  const BOT_RESPONSE: Message = {
    from: 'bot',
    text: "Hello, I am your AI assistant for Agro Smart. How can I help you today?",
  };

  const toggleChat = () => {
    setIsOpen(!isOpen);
    if (!isOpen) {
      setMessages([BOT_RESPONSE]);
    }
  };

  const sendMessage = () => {
    if (input.trim() !== '') {
      const userMessage: Message = { from: 'user', text: input };
      setMessages((prev) => [...prev, userMessage]);
      setInput('');

      // Simulate 2-second delay for bot response
      setTimeout(() => {
        setMessages((prev) => [...prev, BOT_RESPONSE]);
      }, 2000);
    }
  };

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {isOpen ? (
        <motion.div
          initial={{ opacity: 0, scale: 0.8, y: 50 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.8, y: 50 }}
          className="w-80 h-96 bg-white rounded-2xl shadow-xl flex flex-col overflow-hidden"
        >
          <div className="bg-green-600 text-white px-4 py-3 flex justify-between items-center rounded-t-2xl shadow">
            <span className="font-bold text-lg">
              <span className="text-black">Agro</span>
              <span className="text-white">Chat</span>
            </span>
            <button onClick={toggleChat} className="text-xl font-bold hover:text-gray-300">&times;</button>
          </div>

          <div className="flex-1 bg-gray-50 p-4 space-y-2 overflow-y-auto">
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`max-w-[75%] p-2 rounded-lg text-sm ${
                  msg.from === 'user'
                    ? 'ml-auto bg-green-100 text-green-800'
                    : 'mr-auto bg-gray-200 text-black'
                }`}
              >
                {msg.text}
              </div>
            ))}
          </div>

          <div className="p-3 border-t bg-white flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Type a message..."
              className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-xl outline-none focus:ring-2 focus:ring-green-500"
            />
            <button
              onClick={sendMessage}
              className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 text-sm rounded-xl transition"
            >
              Send
            </button>
          </div>
        </motion.div>
      ) : (
        <motion.button
          initial={{ scale: 0.2 }}
          animate={{ scale: 1 }}
          whileHover={{ scale: 1.1 }}
          onClick={toggleChat}
          className="bg-green-600 text-white p-3 rounded-full shadow-lg hover:bg-green-700"
        >
          💬
        </motion.button>
      )}
    </div>
  );
};

export default Chatbot;
