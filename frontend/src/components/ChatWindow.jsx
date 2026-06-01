import React, { useState, useRef, useEffect } from 'react';
import { 
  Send, 
  Bot, 
  User, 
  Loader2, 
  MessageSquare,
  Sparkles,
  Info
} from 'lucide-react';

const ChatWindow = ({ selectedDoc, messages, onSendMessage, isLoading }) => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || !selectedDoc || isLoading) return;
    onSendMessage(input);
    setInput('');
  };

  if (!selectedDoc) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center bg-slate-900/50">
        <div className="flex h-20 w-20 items-center justify-center rounded-3xl bg-slate-800 text-slate-600 mb-6 shadow-xl">
          <MessageSquare size={40} />
        </div>
        <h3 className="text-xl font-bold text-white mb-2">Select a document to start chatting</h3>
        <p className="text-slate-500 max-w-xs text-center">
          Choose a PDF from the sidebar to ask questions and get instant insights.
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-1 flex-col bg-slate-950">
      {/* Header */}
      <div className="flex h-16 items-center justify-between px-8 border-b border-slate-800 bg-slate-950/50 backdrop-blur-xl">
        <div className="flex items-center gap-3 overflow-hidden">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary-500/10 text-primary-400 border border-primary-500/20">
            <Sparkles size={16} />
          </div>
          <div className="overflow-hidden">
            <h3 className="text-sm font-semibold text-white truncate">{selectedDoc.file_name}</h3>
            <div className="flex items-center gap-1.5">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
              <span className="text-[10px] text-slate-500 uppercase tracking-wider font-bold">Assistant Ready</span>
            </div>
          </div>
        </div>
        <button className="p-2 text-slate-500 hover:text-slate-300 transition-colors">
          <Info size={20} />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-8 space-y-6 scrollbar-hide">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center opacity-50">
            <div className="h-16 w-16 rounded-full bg-slate-900 flex items-center justify-center mb-4">
              <Bot size={32} className="text-slate-700" />
            </div>
            <p className="text-slate-500 italic">No messages yet. Try asking: "What is this document about?"</p>
          </div>
        ) : (
          messages.map((msg, index) => (
            <div
              key={index}
              className={`flex items-start gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
            >
              <div className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-xl shadow-lg ${
                msg.role === 'user' 
                  ? 'bg-primary-600 text-white shadow-primary-500/10' 
                  : 'bg-slate-800 text-slate-300 shadow-black/20'
              }`}>
                {msg.role === 'user' ? <User size={20} /> : <Bot size={20} />}
              </div>
              
              <div className={`flex max-w-[80%] flex-col gap-2 ${msg.role === 'user' ? 'items-end' : ''}`}>
                <div className={`rounded-2xl px-5 py-3 text-sm leading-relaxed shadow-sm ${
                  msg.role === 'user'
                    ? 'bg-primary-600 text-white rounded-tr-none'
                    : 'bg-slate-900 border border-slate-800 text-slate-200 rounded-tl-none'
                }`}>
                  {msg.content}
                </div>
                <span className="text-[10px] text-slate-600 font-medium px-1 uppercase tracking-tighter">
                  {msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
                </span>
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="flex items-start gap-4">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-slate-800 text-slate-300 shadow-lg shadow-black/20">
              <Bot size={20} />
            </div>
            <div className="bg-slate-900 border border-slate-800 rounded-2xl rounded-tl-none px-5 py-3 shadow-sm">
              <div className="flex gap-1.5 py-1">
                <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-600"></span>
                <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-600 [animation-delay:0.2s]"></span>
                <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-600 [animation-delay:0.4s]"></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-8 bg-slate-950">
        <form 
          onSubmit={handleSubmit}
          className="relative group max-w-4xl mx-auto"
        >
          <input
            type="text"
            className="w-full bg-slate-900 border border-slate-800 text-white rounded-2xl py-4 pl-6 pr-14 text-sm focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500 transition-all shadow-xl placeholder-slate-600"
            placeholder="Ask anything about the document..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-xl bg-primary-600 text-white hover:bg-primary-500 disabled:opacity-30 disabled:hover:bg-primary-600 transition-all shadow-lg shadow-primary-500/20"
          >
            {isLoading ? <Loader2 size={20} className="animate-spin" /> : <Send size={20} />}
          </button>
        </form>
        <p className="text-[10px] text-slate-600 text-center mt-4 uppercase tracking-[0.2em] font-bold">
          Powered by Pinecone Assistant API
        </p>
      </div>
    </div>
  );
};

export default ChatWindow;
