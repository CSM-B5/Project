import React from 'react';
import { MessageSquare, Send } from 'lucide-react';

export default function ChatAssistant({ messages, inputMessage, setInputMessage, onSendMessage }) {
  return (
    <div className="flex flex-col h-full bg-slate-900/50">
      <div className="p-4 border-b border-slate-800 bg-slate-950/20 flex items-center gap-2">
        <MessageSquare className="h-4 w-4 text-emerald-400" />
        <h2 className="text-sm font-semibold text-slate-200">Multimodal Report Generator</h2>
      </div>

      {/* Message Stream */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, index) => (
          <div key={index} className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}>
            <div className={`max-w-[85%] rounded-lg p-3 text-sm leading-relaxed ${
              msg.sender === 'user' 
                ? 'bg-emerald-600 text-white rounded-br-none shadow-md' 
                : 'bg-slate-800 text-slate-100 rounded-bl-none border border-slate-700 shadow-sm'
            }`}>
              {msg.text}
            </div>
            <span className="text-[9px] text-slate-500 font-mono mt-1 uppercase tracking-wider px-1">
              {msg.sender === 'user' ? 'Operator' : 'Clinical LLM Engine'}
            </span>
          </div>
        ))}
      </div>

      {/* Input Tray */}
      <form onSubmit={onSendMessage} className="p-4 border-t border-slate-800 bg-slate-950/40 flex gap-2">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Ask LLM to draft medical report..."
          className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-emerald-500 transition-colors placeholder-slate-500"
        />
        <button type="submit" className="p-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg transition-colors">
          <Send className="h-4 w-4" />
        </button>
      </form>
    </div>
  );
}
