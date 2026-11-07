import React, { useState } from 'react';
import { Upload, Activity, ShieldAlert, Sliders } from 'lucide-react';
// IMPORT CHAT COMPONENT: This hooks your new component file into the layout
import ChatAssistant from './ChatAssistant'; 

function App() {
  const [imagePreview, setImagePreview] = useState(null);
  const [showSegmentation, setShowSegmentation] = useState(false);
  const [messages, setMessages] = useState([
    { sender: 'ai', text: 'Hello, Doctor. Upload a patient scan to analyze classification parameters, toggle segmentation layers, and generate clinical reports.' }
  ]);
  const [inputMessage, setInputMessage] = useState('');

  const handleImageChange = (e) => {
    const file = e.target.files[0]; // Targeted single file selector
    if (file) {
      setImagePreview(URL.createObjectURL(file));
    }
  };

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    const userMsg = { sender: 'user', text: inputMessage };
    setMessages(prev => [...prev, userMsg]);
    setInputMessage('');

    setTimeout(() => {
      setMessages(prev => [...prev, { 
        sender: 'ai', 
        text: `[Mock LLM Engine]: Analyzing regional data properties relative to the active viewport scan. Your backend teammate will connect this interface window directly to the live Python API.` 
      }]);
    }, 1000);
  };

  return (
    <div className="flex flex-col h-screen max-h-screen bg-slate-900 overflow-hidden text-slate-100 font-sans">
      {/* Top Navbar */}
      <header className="flex items-center justify-between px-6 py-4 bg-slate-950 border-b border-slate-800">
        <div className="flex items-center space-x-3">
          <Activity className="h-6 w-6 text-emerald-500 animate-pulse" />
          <h1 className="text-xl font-bold tracking-tight text-white">
            MedVision AI 
            <span className="text-xs bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded border border-emerald-500/20 ml-2 font-mono">
              V1.0 - Frontend Prototype
            </span>
          </h1>
        </div>
        <div className="text-slate-400 text-sm font-medium">Radiology Suite Workspace</div>
      </header>

      {/* Main Structuring Area */}
      <main className="flex flex-1 overflow-hidden">
        
        {/* PANEL 1: Control & Data Configuration (Left Side) */}
        <section className="w-1/4 p-4 border-r border-slate-800 bg-slate-900/50 flex flex-col justify-between overflow-y-auto">
          <div className="space-y-6">
            <div>
              <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">1. Upload Patient Scan</h2>
              <label className="flex flex-col items-center justify-center border-2 border-dashed border-slate-700 hover:border-emerald-500 rounded-lg p-6 cursor-pointer bg-slate-950/40 transition-colors group">
                <Upload className="h-8 w-8 text-slate-500 group-hover:text-emerald-400 mb-2 transition-colors" />
                <span className="text-sm font-medium text-slate-300">Choose Scan (PNG, JPG)</span>
                <input type="file" accept="image/*" className="hidden" onChange={handleImageChange} />
              </label>
            </div>

            <div>
              <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">2. Classification Outputs</h2>
              <div className="bg-slate-950/50 border border-slate-800 rounded-lg p-4 space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-300">Target Abnormality Detection</span>
                  <span className="text-sm font-bold text-emerald-400">89.4% Confidence</span>
                </div>
                <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                  <div className="bg-emerald-500 h-full w-[89.4%] rounded-full"></div>
                </div>
              </div>
            </div>

            <div>
              <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">3. Segmentation Overlay Control</h2>
              <div className="bg-slate-950/50 border border-slate-800 rounded-lg p-4 space-y-4">
                <div className="flex items-center justify-between">
                  <label htmlFor="segToggle" className="text-sm text-slate-300 cursor-pointer">Activate Segmentation Mask</label>
                  <input 
                    id="segToggle"
                    type="checkbox" 
                    checked={showSegmentation} 
                    onChange={(e) => setShowSegmentation(e.target.checked)}
                    className="w-4 h-4 text-emerald-600 bg-slate-700 rounded border-slate-600 focus:ring-emerald-500 cursor-pointer"
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="p-3 bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs rounded-lg flex gap-2 items-start mt-4">
            <ShieldAlert className="h-4 w-4 shrink-0 mt-0.5" />
            <span><strong>Teammate Notice:</strong> Component states are fully responsive and mapped to frontend variables. Ready for state API integration.</span>
          </div>
        </section>

        {/* PANEL 2: Interactive Diagnostic Viewport (Center) */}
        <section className="w-2/4 bg-slate-950 flex flex-col items-center justify-center p-6 relative">
          {imagePreview ? (
            <div className="relative max-w-full max-h-[75vh] border border-slate-800 rounded-lg overflow-hidden bg-black flex items-center justify-center shadow-2xl">
              <img src={imagePreview} alt="Patient Medical Scan" className="max-h-[70vh] object-contain block" />
              {showSegmentation && (
                <div className="absolute inset-0 bg-gradient-to-tr from-rose-500/40 via-transparent to-cyan-500/30 mix-blend-color-dodge animate-pulse pointer-events-none flex items-center justify-center">
                  <span className="text-xs font-mono uppercase bg-slate-950/90 px-3 py-1.5 border border-rose-500/30 text-rose-400 rounded tracking-widest shadow-lg">
                    Segmented AI Mask Layer Active
                  </span>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center space-y-3">
              <div className="inline-block p-4 bg-slate-900/60 rounded-full border border-slate-800 text-slate-500 mb-1">
                <Sliders className="h-10 w-10" />
              </div>
              <p className="text-slate-300 text-sm font-medium">No clinical scan loaded.</p>
            </div>
          )}
        </section>

        {/* PANEL 3: Cleaned Chat Assistant (Right Side) */}
        <section className="w-1/4 border-l border-slate-800 bg-slate-900/50 h-full">
          {/* We insert the component here and pass variables down as props */}
          <ChatAssistant 
            messages={messages} 
            inputMessage={inputMessage}
            setInputMessage={setInputMessage}
            onSendMessage={handleSendMessage}
          />
        </section>

      </main>
    </div>
  );
}

export default App;
