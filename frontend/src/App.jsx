import React, { useState, useEffect, useRef } from 'react';
import {
  Plus, History, LogOut, Send,
  Image as ImageIcon, Mic, Video, User,
  Sparkles, ShieldCheck, ArrowUp,
  Menu, X, Lock, Fingerprint, Activity,
  Layers, Zap, Hash, AlertTriangle, CheckCircle2,
  ChevronRight, Search, Globe, MessageSquare, FileDown
} from 'lucide-react';
import { supabase } from './supabase';
import axios from 'axios';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { motion, AnimatePresence } from 'framer-motion';
import { jsPDF } from 'jspdf';
import QRCode from 'qrcode';

function cn(...inputs) {
  return twMerge(clsx(inputs));
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

export default function App() {
  const [user, setUser] = useState(null);
  const [isGuest, setIsGuest] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const chatEndRef = useRef(null);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null);
      if (session?.user) fetchHistory(session.user.id);
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
      if (session?.user) fetchHistory(session.user.id);
    });

    return () => subscription.unsubscribe();
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fetchHistory = async (uid) => {
    try {
      const { data, error } = await supabase
        .from('analysis')
        .select('*')
        .eq('user_id', uid)
        .order('created_at', { ascending: false })
        .limit(30);

      if (error) throw error;
      setHistory(data || []);
    } catch (e) {
      console.error("Error fetching history", e);
    }
  };

  const handleLogin = async () => {
    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: window.location.origin
        }
      });
      if (error) {
        console.warn("OAuth failed:", error.message);
        alert("Google Login failed. Please ensure you have configured Google OAuth in Supabase.");
      }
    } catch (error) {
      console.error("Login failed", error);
    }
  };

  const handleLogout = () => {
    supabase.auth.signOut();
    setIsGuest(false);
    setUser(null);
  };

  const handleAnalyze = async (type, content) => {
    if (!user && !isGuest) return;

    const currentUid = user?.id || "guest_session";

    const userMsg = {
      id: Date.now(),
      role: 'user',
      content: type === 'text' ? content : `SOURCE ANALYSIS: ${type.toUpperCase()}`,
      type,
      file: type !== 'text' ? URL.createObjectURL(content) : null
    };

    setMessages(prev => [...prev, userMsg]);
    setLoading(true);
    setInputValue("");

    try {
      let endpoint = `${API_BASE}/${type}/analyze`;
      let res;

      const config = {
        headers: { 'X-User-Id': currentUid }
      };

      if (type === 'text') {
        res = await axios.post(endpoint, { text: content, user_id: currentUid });
      } else {
        const formData = new FormData();
        formData.append('file', content);
        res = await axios.post(endpoint, formData, config);
      }

      const analysisResult = res.data;
      const mediaUrl = res.data?.media_url || null;
      const returnedInputContent = res.data?.input_content || null;
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        role: 'ai',
        content: analysisResult,
        mediaUrl,
        timestamp: new Date().toISOString(),
        inputType: type,
        inputContent: returnedInputContent || (type === 'text' ? content : null)
      }]);
      if (user) fetchHistory(user.id);
    } catch (error) {
      console.error("Analysis failed", error);
      const errorDetail = error.response?.data?.detail || error.message || "Unknown error";
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        role: 'ai',
        content: { explanation: `COMMUNICATION_LINK_ERROR: ${errorDetail}` },
        error: true
      }]);
    } finally {
      setLoading(false);
    }
  };

  if (!user && !isGuest) {
    return (
      <div className="min-h-screen bg-[#0d0d0d] flex flex-col items-center justify-center p-6 font-sans relative">
        <div className="bg-grain" />
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-md w-full text-center space-y-12 relative z-10"
        >
          <div className="space-y-4">
            <div className="w-16 h-16 bg-white rounded-2xl mx-auto flex items-center justify-center shadow-2xl">
              <ShieldCheck size={32} className="text-black" />
            </div>
            <h1 className="text-4xl font-display font-black text-white uppercase tracking-tighter">Fair Frame</h1>
            <p className="text-gray-400 text-lg">Your perspective, purified.</p>
          </div>

          <div className="space-y-4">
            <button
              onClick={handleLogin}
              className="w-full h-14 bg-white text-black rounded-2xl font-bold hover:bg-gray-100 transition-all flex items-center justify-center gap-3 text-lg"
            >
              <img src="https://www.google.com/favicon.ico" className="w-5 h-5 grayscale" alt="Google" />
              Sign in with Google
            </button>
            <div className="flex items-center gap-4 py-2">
              <div className="h-px bg-white/5 flex-1" />
              <span className="text-[10px] font-mono text-gray-600 uppercase tracking-widest">or</span>
              <div className="h-px bg-white/5 flex-1" />
            </div>
            <button
              onClick={() => setIsGuest(true)}
              className="w-full h-14 bg-white/5 border border-white/10 text-white rounded-2xl font-bold hover:bg-white/10 transition-all text-lg"
            >
              Continue as Guest
            </button>
          </div>

          <p className="text-[11px] text-gray-500 leading-relaxed px-8">
            Fair Frame utilizes Gemini 2.5 Flash for high-precision linguistic and visual bias detection.
            Google Login required for full history synchronization.
          </p>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-[#0d0d0d] text-[#ececec] overflow-hidden selection:bg-[#00F0FF] selection:text-black">
      <div className="bg-grain opacity-[0.03]" />

      {/* Sidebar - ChatGPT Style */}
      <AnimatePresence mode="wait">
        {sidebarOpen && (
          <motion.aside
            initial={{ x: -260 }}
            animate={{ x: 0 }}
            exit={{ x: -260 }}
            transition={{ type: 'tween', duration: 0.2 }}
            className="w-[260px] bg-[#000000] flex flex-col h-full z-20 relative border-r border-white-[0.02]"
          >
            <div className="p-3">
              <button
                onClick={() => setMessages([])}
                className="w-full h-11 flex items-center gap-3 hover:bg-white/5 rounded-lg px-3 transition-all text-sm group"
              >
                <div className="w-7 h-7 bg-white/10 rounded-full flex items-center justify-center">
                  <Plus size={16} />
                </div>
                <span className="font-semibold text-white/90">New Analysis</span>
              </button>
            </div>

            <div className="flex-1 overflow-y-auto custom-scrollbar px-3 space-y-6 pt-4">
              <div className="space-y-1">
                <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest px-3 mb-2 block">Recent</span>
                {history.length > 0 ? history.map(item => (
                  <div
                    key={item.id}
                    onClick={() => {
                      const restored = {
                        id: item.id,
                        role: 'ai',
                        content: {
                          overall_bias_score: item.overall_bias_score,
                          reasoning: item.reasoning,
                          visual_findings: item.visual_findings || [],
                          linguistic_findings: item.linguistic_findings || [],
                          rectification_plan: { text_fix: item.text_fix, visual_fix: item.visual_fix }
                        },
                        mediaUrl: item.media_url || null,
                        inputType: item.input_type || 'text',
                        inputContent: item.input_content || null,
                        timestamp: item.created_at || new Date().toISOString()
                      };
                      const userMsg = {
                        id: item.id + '_u',
                        role: 'user',
                        content: (item.input_type === 'text' && item.input_content) ? item.input_content : `SOURCE ANALYSIS: ${(item.input_type || 'TEXT').toUpperCase()}`,
                        type: item.input_type || 'text',
                        file: item.media_url || null
                      };
                      setMessages([userMsg, restored]);
                    }}
                    className="p-3 hover:bg-[#171717] rounded-lg cursor-pointer text-sm transition-all group"
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-[9px] font-mono font-bold text-gray-600 uppercase tracking-widest bg-white/5 px-1.5 py-0.5 rounded">
                        {item.input_type || 'text'}
                      </span>
                      {item.overall_bias_score != null && (
                        <span className="text-[9px] font-mono text-[#00F0FF] ml-auto">{item.overall_bias_score}%</span>
                      )}
                    </div>
                    <p className="text-[11px] text-gray-500 group-hover:text-gray-300 transition-colors truncate leading-relaxed">
                      {item.reasoning ? item.reasoning.slice(0, 60) + '…' : 'Media Analysis'}
                    </p>
                  </div>
                )) : (
                  <div className="px-3 py-4 text-[11px] text-gray-600 font-medium italic">Empty archive</div>
                )}
              </div>
            </div>

            <div className="p-3 mt-auto">
              <div className="flex items-center gap-3 p-3 hover:bg-[#171717] rounded-lg cursor-pointer transition-all">
                <div className="w-8 h-8 rounded-full overflow-hidden border border-white/10 mb-1">
                  <img src={user?.user_metadata?.avatar_url || `https://api.dicebear.com/7.x/avataaars/svg?seed=${user?.id || 'Guest'}`} alt="" />
                </div>
                <div className="flex-1 truncate">
                  <div className="text-xs font-bold text-white/90 truncate uppercase tracking-tight">{user?.user_metadata?.full_name || "GUEST_USER"}</div>
                </div>
              </div>
              <button
                onClick={handleLogout}
                className="w-full mt-2 flex items-center gap-3 p-3 text-[11px] text-red-400/60 hover:text-red-400 transition-colors uppercase font-black"
              >
                <LogOut size={14} />
                Exit Session
              </button>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <main className="flex-1 flex flex-col relative h-full bg-[#0d0d0d]">
        {/* Top Header */}
        <header className="h-14 flex items-center justify-between px-4 sticky top-0 z-10 bg-[#0d0d0d]/80 backdrop-blur-md">
          <div className="flex items-center gap-3">
            {!sidebarOpen && (
              <button onClick={() => setSidebarOpen(true)} className="p-2 hover:bg-white/5 rounded-lg text-gray-400">
                <Menu size={20} />
              </button>
            )}
            <div className="flex items-center gap-2 px-2">
              <span className="text-sm font-bold text-white/50">Fair Frame 2.5</span>
              <div className="px-1.5 py-0.5 rounded bg-white/5 text-[9px] font-mono font-bold text-gray-500">PRO</div>
            </div>
          </div>
          <div className="flex gap-2">
            <button className="p-2 hover:bg-white/5 rounded-lg text-gray-400"><Globe size={18} /></button>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto custom-scrollbar flex flex-col">
          <div className="max-w-3xl mx-auto w-full flex-1 flex flex-col px-4 sm:px-8">
            <AnimatePresence mode="popLayout">
              {messages.length === 0 ? (
                <motion.div
                  initial={{ opacity: 0, scale: 0.98 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="flex-1 flex flex-col items-center justify-center text-center py-20"
                >
                  <div className="w-14 h-14 bg-white/5 rounded-2xl flex items-center justify-center mb-10 border border-white/5">
                    <ShieldCheck size={28} className="text-white/40" />
                  </div>
                  <h2 className="text-4xl font-display font-black text-white/90 tracking-tighter uppercase mb-2">How can I assist?</h2>
                  <p className="text-gray-500 text-sm max-w-sm mb-12">Submit text or upload media to begin a deep-layer bias audit.</p>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-xl">
                    {[
                      { icon: <ImageIcon size={18} />, label: "VISUAL_AUDIT", desc: "Stereotype detection" },
                      { icon: <Mic size={18} />, label: "AUDIO_SYNTH", desc: "Speaker bias capture" },
                      { icon: <Video size={18} />, label: "FRAME_PARSING", desc: "Temporal bias scan" },
                      { icon: <MessageSquare size={18} />, label: "TEXT_DYNAMICS", desc: "Implicit bias audit" }
                    ].map((item, id) => (
                      <div key={id} className="p-4 bg-transparent border border-white/5 rounded-xl text-left hover:bg-white/5 cursor-pointer transition-all active:scale-[0.98]">
                        <div className="text-white/40 mb-3">{item.icon}</div>
                        <div className="font-bold text-xs text-white/80 tracking-widest uppercase">{item.label}</div>
                        <div className="text-[10px] text-gray-600 mt-1 uppercase font-medium">{item.desc}</div>
                      </div>
                    ))}
                  </div>
                </motion.div>
              ) : (
                <div className="space-y-12 pb-48 pt-6">
                  {messages.map((msg) => (
                    <motion.div
                      key={msg.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className={cn(
                        "flex gap-6 max-w-3xl w-full mx-auto",
                        msg.role === 'user' ? "flex-col items-end" : "items-start"
                      )}
                    >
                      {msg.role === 'user' ? (
                        <div className="bg-[#2f2f2f]/80 p-4 rounded-3xl rounded-tr-none text-[#ececec] text-sm leading-relaxed max-w-[85%]">
                          {msg.type === 'image' && msg.file && (
                            <img src={msg.file} className="max-w-xs rounded-xl mb-4 border border-white/10" alt="Upload" />
                          )}
                          {msg.type === 'video' && msg.file && (
                            <video src={msg.file} controls className="max-w-xs rounded-xl mb-4 border border-white/10 w-full" />
                          )}
                          {msg.type === 'audio' && msg.file && (
                            <audio src={msg.file} controls className="w-full mb-4 rounded-xl" />
                          )}
                          <p className="font-medium">{msg.content}</p>
                        </div>
                      ) : (
                        <div className="flex-1 flex gap-5">
                          <div className="w-8 h-8 rounded-full bg-white flex items-center justify-center flex-shrink-0 mt-1 shadow-lg">
                            <ShieldCheck size={18} className="text-black" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <AnalysisResultCard user={user} result={msg.content} mediaUrl={msg.mediaUrl} timestamp={msg.timestamp} inputType={msg.inputType} inputContent={msg.inputContent} />
                          </div>
                        </div>
                      )}
                    </motion.div>
                  ))}
                  {loading && (
                    <div className="flex gap-5 max-w-3xl w-full mx-auto">
                      <div className="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center animate-pulse">
                        <Activity size={16} className="text-white/20" />
                      </div>
                      <div className="flex-1 space-y-3 pt-2">
                        <div className="h-3 bg-white/5 rounded-full w-3/4 animate-pulse"></div>
                        <div className="h-3 bg-white/5 rounded-full w-1/2 animate-pulse"></div>
                      </div>
                    </div>
                  )}
                  <div ref={chatEndRef} />
                </div>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* Input Bar - ChatGPT Style */}
        <div className="w-full flex justify-center pb-8 pt-2 bg-gradient-to-t from-[#0d0d0d] via-[#0d0d0d]/90 to-transparent sticky bottom-0 z-10 px-4">
          <div className="max-w-3xl mx-auto w-full relative">
            <div className="relative bg-[#171717]/80 backdrop-blur-xl rounded-[2.5rem] border border-white/10 p-2 transition-all shadow-2xl flex items-end gap-2">
              <div className="flex gap-0.5 pb-1 pl-1">
                <input type="file" id="img-up" hidden onChange={(e) => handleAnalyze('image', e.target.files[0])} accept="image/*" />
                <label htmlFor="img-up" className="w-10 h-10 flex items-center justify-center rounded-full text-gray-400 hover:text-white hover:bg-white/5 cursor-pointer transition-all"><ImageIcon size={20} /></label>

                <input type="file" id="aud-up" hidden onChange={(e) => handleAnalyze('audio', e.target.files[0])} accept="audio/*" />
                <label htmlFor="aud-up" className="w-10 h-10 flex items-center justify-center rounded-full text-gray-400 hover:text-white hover:bg-white/5 cursor-pointer transition-all"><Mic size={20} /></label>

                <input type="file" id="vid-up" hidden onChange={(e) => handleAnalyze('video', e.target.files[0])} accept="video/*" />
                <label htmlFor="vid-up" className="w-10 h-10 flex items-center justify-center rounded-full text-gray-400 hover:text-white hover:bg-white/5 cursor-pointer transition-all"><Video size={20} /></label>
              </div>

              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Message Fair Frame..."
                className="flex-1 bg-transparent border-none focus:ring-0 focus:outline-none px-1 py-3 resize-none h-[52px] max-h-60 text-[15px] text-white/90 placeholder-gray-500 overflow-hidden leading-relaxed"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    if (inputValue.trim()) handleAnalyze('text', inputValue);
                  }
                }}
              />

              <div className="pb-1 pr-1">
                <button
                  onClick={() => handleAnalyze('text', inputValue)}
                  disabled={!inputValue.trim() || loading}
                  className={cn(
                    "w-10 h-10 rounded-full flex items-center justify-center transition-all",
                    inputValue.trim() ? "bg-white text-black hover:scale-105" : "bg-white/5 text-gray-700 cursor-not-allowed"
                  )}
                >
                  <ArrowUp size={20} strokeWidth={3} />
                </button>
              </div>
            </div>
            <p className="text-[10px] text-center mt-3 text-gray-600 font-medium">Fair Frame uses AI to identify implicit biases in data synthesis.</p>
          </div>
        </div>
      </main>
    </div>
  );
}

function AnalysisResultCard({ user, result, mediaUrl, timestamp, inputType, inputContent }) {
  if (!result || result.error) return <div className="p-6 bg-red-500/5 rounded-3xl border border-red-500/10 text-red-300 text-xs font-mono">{result?.explanation || "INTERNAL_SYNC_ERROR"}</div>;

  const score = result.overall_bias_score ?? result.bias_score ?? 0;
  const explanation = result.reasoning || result.explanation || "";
  const categories = [
    ...(result.visual_findings || []),
    ...(result.linguistic_findings || []),
    ...(result.bias_type || [])
  ];
  const rootTrace = result.cause_of_bias || "";
  const _textFix = result.rectification_plan?.text_fix || result.suggestion_to_fix || "";
  const _visualFix = result.rectification_plan?.visual_fix || "";
  const isPlaceholder = (v) => !v || ["n/a", "none", "null", "-"].includes(v.toLowerCase().trim());
  const textFix = isPlaceholder(_textFix) ? "" : _textFix;
  const visualFix = isPlaceholder(_visualFix) ? "" : _visualFix;

  const generateReport = async () => {
    const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });
    const W = 210;
    const M = 20; // margin
    const LINE = W - M * 2;
    let y = 0;
    const NAVY = [15, 23, 58];
    const ACCENT = [99, 102, 241]; // indigo
    const TEXT = [30, 30, 40];
    const MUTED = [110, 110, 130];
    const LIGHT_BG = [248, 249, 252];

    const ts = timestamp ? new Date(timestamp).toLocaleString() : new Date().toLocaleString();

    // ── Page white background ──
    const paintWhite = () => {
      doc.setFillColor(255, 255, 255);
      doc.rect(0, 0, W, 297, 'F');
    };
    paintWhite();

    // ── Generate QR code data URL ─────────────────────────────
    const qrTarget = inputType === 'text'
      ? (inputContent || 'https://fairframe.app')
      : (mediaUrl || 'https://fairframe.app');
    let qrDataUrl = null;
    try {
      qrDataUrl = await QRCode.toDataURL(qrTarget, {
        width: 120,
        margin: 1,
        color: { dark: '#0f1173', light: '#ffffff' }
      });
    } catch (e) {
      console.warn('QR generation failed', e);
    }

    // ── Header strip ──────────────────────────────────────────
    doc.setFillColor(...NAVY);
    doc.rect(0, 0, W, 44, 'F');
    // Brand name
    doc.setFontSize(15);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(255, 255, 255);
    doc.text('FairFrame', M, 16);
    // Tagline
    doc.setFontSize(7);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(180, 189, 220);
    doc.text('AI Bias Audit Report', M, 22);
    // Report metadata on the right
    doc.setFontSize(6.5);
    doc.setTextColor(150, 163, 200);

    const userName = user?.user_metadata?.full_name || 'Guest User';
    const userEmail = user?.email || 'N/A';

    doc.text(userName.toUpperCase(), W - M, 14, { align: 'right' });
    doc.text(userEmail, W - M, 20, { align: 'right' });
    doc.text(`Generated: ${ts}`, W - M, 26, { align: 'right' });
    doc.text(`Analysis Type: ${(inputType || 'Content').toUpperCase()}`, W - M, 32, { align: 'right' });

    // Bottom accent line on header
    doc.setDrawColor(...ACCENT);
    doc.setLineWidth(0.8);
    doc.line(0, 44, W, 44);
    y = 56;

    // ── QR Code block (top-left, below header, before score) ──
    if (qrDataUrl) {
      const qrSize = 28;  // mm
      const qrX = M;
      const qrY = y;
      // White card background for QR
      doc.setFillColor(...LIGHT_BG);
      doc.roundedRect(qrX - 2, qrY - 2, qrSize + 4, qrSize + 8, 2, 2, 'F');
      doc.addImage(qrDataUrl, 'PNG', qrX, qrY, qrSize, qrSize);
      // Label under QR
      doc.setFontSize(5.5);
      doc.setFont('helvetica', 'normal');
      doc.setTextColor(...MUTED);
      doc.text('Scan to view source', qrX + qrSize / 2, qrY + qrSize + 4, { align: 'center' });
      y += qrSize + 12;
    }

    // ── Helpers ───────────────────────────────────────────────
    const checkPage = (needed = 40) => {
      if (y + needed > 280) {
        doc.addPage();
        paintWhite();
        // mini header on continuation pages
        doc.setFillColor(...NAVY);
        doc.rect(0, 0, W, 12, 'F');
        doc.setFontSize(6.5);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(255, 255, 255);
        doc.text('FairFrame  ·  Bias Audit Report', M, 8);
        y = 22;
      }
    };

    const sectionLabel = (title, color = ACCENT) => {
      checkPage(20);
      doc.setFontSize(7.5);
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(...color);
      doc.text(title.toUpperCase(), M, y);
      doc.setDrawColor(...color);
      doc.setLineWidth(0.3);
      doc.line(M, y + 2, M + LINE, y + 2);
      y += 9;
    };

    const paragraph = (text, size = 9.5, color = TEXT) => {
      doc.setFontSize(size);
      doc.setFont('helvetica', 'normal');
      doc.setTextColor(...color);
      const lines = doc.splitTextToSize(text, LINE);
      doc.text(lines, M, y);
      y += lines.length * size * 0.42 + 5;
    };

    const infoCard = (label, value, accentRGB = ACCENT) => {
      checkPage(30);
      const safeValue = typeof value === 'string' ? value.replace(/([^\s]{80})/g, '$1 ') : (value || '—');
      const textLines = doc.splitTextToSize(safeValue, LINE - 14);
      const cardH = textLines.length * 5 + 16;
      // card bg
      doc.setFillColor(...LIGHT_BG);
      doc.roundedRect(M, y, LINE, cardH, 3, 3, 'F');
      // left accent bar
      doc.setFillColor(...accentRGB);
      doc.roundedRect(M, y, 3, cardH, 1.5, 1.5, 'F');
      // label
      doc.setFontSize(6.5);
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(...accentRGB);
      doc.text(label.toUpperCase(), M + 7, y + 7);
      // value text
      doc.setFontSize(9);
      doc.setFont('helvetica', 'normal');
      doc.setTextColor(...TEXT);
      doc.text(textLines, M + 7, y + 13);
      y += cardH + 6;
    };

    // ── Score Banner ─────────────────────────────────────────
    const scoreRGB = score >= 70 ? [220, 38, 38] : score >= 40 ? [217, 119, 6] : [22, 163, 74];
    // score box
    doc.setFillColor(...LIGHT_BG);
    doc.roundedRect(M, y, LINE, 28, 4, 4, 'F');
    doc.setFillColor(...scoreRGB);
    doc.roundedRect(M, y, 3, 28, 2, 2, 'F');
    // label
    doc.setFontSize(7);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...MUTED);
    doc.text('OVERALL BIAS INTENSITY SCORE', M + 8, y + 7);
    // big number
    doc.setFontSize(26);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...scoreRGB);
    doc.text(`${score}%`, M + 8, y + 22);
    // bar track
    const barX = M + 38;
    const barW = LINE - 42;
    doc.setFillColor(220, 220, 230);
    doc.roundedRect(barX, y + 15, barW, 5, 2.5, 2.5, 'F');
    doc.setFillColor(...scoreRGB);
    doc.roundedRect(barX, y + 15, barW * score / 100, 5, 2.5, 2.5, 'F');
    // risk label
    const riskLabel = score >= 70 ? 'HIGH RISK' : score >= 40 ? 'MODERATE RISK' : 'LOW RISK';
    doc.setFontSize(7);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...scoreRGB);
    doc.text(riskLabel, barX + barW, y + 22, { align: 'right' });
    y += 36;

    // ── Analysis Summary ─────────────────────────────────────
    if (explanation) {
      sectionLabel('Analysis Summary');
      paragraph(explanation);
    }

    // ── Cause of Bias ────────────────────────────────────────
    if (rootTrace) {
      sectionLabel('Cause of Bias', [185, 28, 28]);
      infoCard('Root Cause', rootTrace, [220, 38, 38]);
    }

    // ── Categories ──────────────────────────────────────────
    if (categories.length > 0) {
      checkPage(30);
      sectionLabel('Bias Categories');
      const colW = (LINE - 6) / 3;
      categories.forEach((cat, i) => {
        const col = i % 3;
        const rowIdx = Math.floor(i / 3);
        const cx = M + col * (colW + 3);
        const cy = y + rowIdx * 10;
        doc.setFillColor(...LIGHT_BG);
        doc.roundedRect(cx, cy, colW, 8, 2, 2, 'F');
        doc.setDrawColor(...ACCENT);
        doc.setLineWidth(0.2);
        doc.roundedRect(cx, cy, colW, 8, 2, 2, 'S');
        doc.setFontSize(6.5);
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(...TEXT);
        const catTxt = doc.splitTextToSize(cat, colW - 4);
        doc.text(catTxt[0], cx + 3, cy + 5.3);
      });
      y += Math.ceil(categories.length / 3) * 10 + 8;
    }

    // ── Rectified Output ─────────────────────────────────────
    if (textFix || visualFix) {
      sectionLabel('Rectified Output', [21, 128, 61]);
      if (textFix) infoCard('Text Fix', textFix, [22, 163, 74]);
      if (visualFix) infoCard('Visual Fix', visualFix, [22, 163, 74]);
    }

    // ── Source Media ─────────────────────────────────────────
    if (mediaUrl) {
      sectionLabel('Source Media', [109, 40, 217]);
      infoCard(`${(inputType || 'Media').toUpperCase()} Input · Supabase URL`, mediaUrl, [124, 58, 237]);
    }

    // ── Footer on every page ─────────────────────────────────
    const totalPages = doc.internal.getNumberOfPages();
    for (let p = 1; p <= totalPages; p++) {
      doc.setPage(p);
      doc.setFillColor(...NAVY);
      doc.rect(0, 284, W, 13, 'F');
      doc.setFontSize(6.5);
      doc.setFont('helvetica', 'normal');
      doc.setTextColor(150, 163, 200);
      doc.text('FairFrame  ·  AI Bias Audit System  ·  Confidential', M, 292);
      doc.text(`Page ${p} of ${totalPages}`, W - M, 292, { align: 'right' });
    }

    doc.save(`FairFrame_Bias_Report_${Date.now()}.pdf`);
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-2 duration-500">
      <div className="space-y-3">
        <h4 className="text-[10px] font-mono font-black text-gray-500 uppercase tracking-[0.2em] flex items-center gap-2">
          <Zap size={10} /> Bias Synth Analysis
        </h4>
        <p className="text-lg font-medium text-white/90 leading-relaxed font-display uppercase tracking-tight">
          {explanation}
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="p-5 bg-white/[0.02] border border-white/5 rounded-2xl space-y-4">
          <div className="flex justify-between items-center">
            <span className="text-[10px] font-mono font-black text-gray-600 uppercase tracking-widest">Intensity Score</span>
            <span className="text-xl font-display font-black text-[#00F0FF] underline decoration-[#00F0FF]/20 underline-offset-4">{score}%</span>
          </div>
          <div className="h-1 bg-white/5 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${score}%` }}
              className="h-full bg-[#00F0FF] shadow-[0_0_10px_#00F0FF44]"
            />
          </div>
        </div>

        <div className="p-5 bg-white/[0.02] border border-white/5 rounded-2xl space-y-4">
          <span className="text-[10px] font-mono font-black text-gray-600 uppercase tracking-widest block">Categories Alpha</span>
          <div className="flex flex-wrap gap-1.5">
            {categories.length > 0 ? categories.map((t, i) => (
              <span key={i} className="px-2 py-1 bg-white/5 border border-white/5 rounded text-[8px] font-mono text-gray-300 uppercase tracking-widest">{t}</span>
            )) : <span className="text-[10px] text-gray-600 italic">Nil</span>}
          </div>
        </div>
      </div>

      {rootTrace && (
        <div className="p-5 border-l-2 border-red-500/30 bg-red-500/5 rounded-r-2xl">
          <span className="text-[9px] font-mono font-black text-red-500/60 uppercase tracking-widest block mb-2">Root Trace</span>
          <p className="text-xs text-red-100/70 font-mono italic">"{rootTrace}"</p>
        </div>
      )}

      {(textFix || visualFix) && (
        <div className="p-6 bg-[#CFFF04]/5 border border-[#CFFF04]/10 rounded-2xl group overflow-hidden space-y-3">
          <h4 className="text-[10px] font-mono font-black text-[#CFFF04] uppercase tracking-widest flex items-center gap-2">
            <CheckCircle2 size={12} /> Refined Output
          </h4>
          {textFix && (
            <div className="text-sm text-[#CFFF04] font-display font-black uppercase leading-relaxed tracking-tight">{textFix}</div>
          )}
          {visualFix && (
            <div className="text-xs text-[#CFFF04]/70 font-mono leading-relaxed">VISUAL: {visualFix}</div>
          )}
        </div>
      )}

      {/* Generate Report Button */}
      <button
        onClick={generateReport}
        className="w-full flex items-center justify-center gap-2.5 py-3 px-5 rounded-2xl border border-white/10 bg-white/[0.03] hover:bg-white/[0.07] hover:border-[#00F0FF]/30 text-white/60 hover:text-[#00F0FF] transition-all duration-200 text-[11px] font-mono font-bold uppercase tracking-widest group"
      >
        <FileDown size={14} className="group-hover:animate-bounce" />
        Generate Report
      </button>
    </div>
  );
}
