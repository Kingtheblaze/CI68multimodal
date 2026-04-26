'use client';

import React, { useState } from 'react';
import {
  ArrowRight,
  Cpu,
  FileText,
  Image as ImageIcon,
  MessageSquare,
  Network,
  Search,
  ShoppingBag,
  Upload,
  X,
} from 'lucide-react';

type GraphContext = {
  brand?: string | null;
  category?: string | null;
  reviews?: string[] | null;
};

type SearchResult = {
  product_id: string;
  name: string;
  description: string;
  result_type?: 'product' | 'document';
  graph_context?: GraphContext | null;
};

type ChatMessage = {
  role: 'user' | 'assistant';
  content: string;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Home() {
  const [query, setQuery] = useState('');
  const [selectedImagePreview, setSelectedImagePreview] = useState<string | null>(null);
  const [selectedImageFile, setSelectedImageFile] = useState<File | null>(null);
  const [selectedDocumentFile, setSelectedDocumentFile] = useState<File | null>(null);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [chatMessage, setChatMessage] = useState('');
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [isChatting, setIsChatting] = useState(false);

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onloadend = () => {
      setSelectedImagePreview(reader.result as string);
      setSelectedImageFile(file);
    };
    reader.readAsDataURL(file);
  };

  const handleDocumentUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setSelectedDocumentFile(file);
  };

  const clearImage = () => {
    setSelectedImagePreview(null);
    setSelectedImageFile(null);
  };

  const clearDocument = () => {
    setSelectedDocumentFile(null);
  };

  const executeSearch = async () => {
    setIsSearching(true);
    try {
      const formData = new FormData();
      formData.append('query', query);

      if (selectedImageFile) {
        formData.append('image', selectedImageFile);
      }
      if (selectedDocumentFile) {
        formData.append('document', selectedDocumentFile);
      }

      const response = await fetch(`${API_URL}/search-multimodal`, {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      setResults(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error(err);
      setResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const sendChat = async () => {
    if (!chatMessage.trim()) return;

    const userMsg: ChatMessage = { role: 'user', content: chatMessage };
    setChatHistory((prev) => [...prev, userMsg]);
    setChatMessage('');
    setIsChatting(true);

    const firstProduct = results.find((item) => item.result_type !== 'document');
    const firstDocument = results.find((item) => item.result_type === 'document');

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMsg.content,
          product_id: firstProduct?.product_id || null,
          document_context: firstDocument?.description || null,
        }),
      });
      const data = await response.json();
      setChatHistory((prev) => [...prev, { role: 'assistant', content: data.response || data.detail || 'No response generated.' }]);
    } catch (err) {
      console.error(err);
      setChatHistory((prev) => [...prev, { role: 'assistant', content: 'Unable to reach the backend chat service.' }]);
    } finally {
      setIsChatting(false);
    }
  };

  const productCount = results.filter((item) => item.result_type !== 'document').length;
  const documentCount = results.filter((item) => item.result_type === 'document').length;

  return (
    <div className="min-h-screen bg-[#05070A] text-white font-sans">
      <nav className="border-b border-white/5 bg-black/40 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center shadow-[0_0_20px_rgba(79,70,229,0.4)]">
              <Network size={24} />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight">GraphRAG Intelligence</h1>
              <p className="text-[10px] uppercase tracking-[0.35em] text-indigo-400 font-bold">Text • Image • PDF</p>
            </div>
          </div>
          <div className="flex items-center gap-6 text-sm font-medium text-gray-400">
            <span className="hover:text-white transition-colors">Catalog</span>
            <span className="hover:text-white transition-colors">Insights</span>
            <button className="bg-white/5 hover:bg-white/10 px-4 py-2 rounded-lg border border-white/10 transition-all">
              API Settings
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6 py-12 grid lg:grid-cols-12 gap-12">
        <div className="lg:col-span-4 space-y-8">
          <div className="bg-[#0C0F16] border border-white/5 rounded-3xl p-8 shadow-2xl relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-600/10 blur-[60px] rounded-full -mr-16 -mt-16" />

            <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
              <Search className="text-indigo-400" />
              Smart Search
            </h2>

            <div className="space-y-6">
              <div className="space-y-2">
                <label className="text-xs font-bold text-gray-500 uppercase tracking-widest ml-1">Text Modality</label>
                <input
                  type="text"
                  placeholder="Try running shoes, watch, laptop, premium accessory..."
                  className="w-full bg-black/40 border border-white/10 rounded-2xl p-4 focus:ring-2 focus:ring-indigo-500 outline-none transition-all"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold text-gray-500 uppercase tracking-widest ml-1">Image Modality</label>
                <div className="relative border-2 border-dashed border-white/10 rounded-2xl p-6 flex flex-col items-center justify-center gap-3 hover:border-indigo-500/50 transition-colors cursor-pointer min-h-[190px]">
                  {selectedImagePreview ? (
                    <div className="relative w-full aspect-video rounded-lg overflow-hidden">
                      <img src={selectedImagePreview} alt="Selected product" className="w-full h-full object-cover" />
                      <button
                        onClick={clearImage}
                        className="absolute top-2 right-2 bg-black/60 p-1 rounded-full text-white hover:bg-red-500 transition-colors"
                      >
                        <X size={16} />
                      </button>
                    </div>
                  ) : (
                    <>
                      <div className="w-12 h-12 bg-white/5 rounded-full flex items-center justify-center text-gray-400">
                        <Upload size={24} />
                      </div>
                      <p className="text-sm text-gray-400 text-center">Upload a product image to search visually</p>
                      <input
                        type="file"
                        className="absolute inset-0 opacity-0 cursor-pointer"
                        onChange={handleImageUpload}
                        accept="image/*"
                      />
                    </>
                  )}
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold text-gray-500 uppercase tracking-widest ml-1">Document Modality</label>
                <div className="border border-white/10 rounded-2xl p-4 bg-black/30">
                  {selectedDocumentFile ? (
                    <div className="flex items-center justify-between gap-4">
                      <div className="flex items-center gap-3 min-w-0">
                        <div className="w-11 h-11 rounded-xl bg-amber-500/10 text-amber-300 flex items-center justify-center">
                          <FileText size={20} />
                        </div>
                        <div className="min-w-0">
                          <p className="font-medium truncate">{selectedDocumentFile.name}</p>
                          <p className="text-xs text-gray-500">PDF, DOCX, TXT, or MD context is ready</p>
                        </div>
                      </div>
                      <button onClick={clearDocument} className="text-gray-400 hover:text-white transition-colors">
                        <X size={18} />
                      </button>
                    </div>
                  ) : (
                    <label className="flex items-center gap-3 cursor-pointer">
                      <div className="w-11 h-11 rounded-xl bg-white/5 text-gray-300 flex items-center justify-center">
                        <FileText size={20} />
                      </div>
                      <div>
                        <p className="font-medium">Upload PDF or document</p>
                        <p className="text-xs text-gray-500">Extract text and retrieve relevant chunks</p>
                      </div>
                      <input
                        type="file"
                        className="hidden"
                        onChange={handleDocumentUpload}
                        accept=".pdf,.docx,.txt,.md"
                      />
                    </label>
                  )}
                </div>
              </div>

              <button
                onClick={executeSearch}
                disabled={isSearching}
                className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-bold py-4 rounded-2xl flex items-center justify-center gap-3 shadow-lg shadow-indigo-600/20 transition-all"
              >
                {isSearching ? <Cpu className="animate-spin" /> : <ShoppingBag />}
                Process 3-Modal Intelligence
              </button>
            </div>
          </div>

          <div className="bg-indigo-600/5 border border-indigo-500/20 rounded-3xl p-8">
            <h3 className="text-sm font-bold text-indigo-400 uppercase tracking-widest mb-4 flex items-center gap-2">
              <Cpu size={16} />
              Reasoning Engine
            </h3>
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <div className="w-1 h-1 bg-indigo-500 rounded-full mt-2" />
                <p className="text-xs text-gray-400">Text query flows through retrieval, graph enrichment, and LLM response generation.</p>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-1 h-1 bg-indigo-500 rounded-full mt-2" />
                <p className="text-xs text-gray-400">Image uploads trigger visual retrieval when the vector service is available.</p>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-1 h-1 bg-indigo-500 rounded-full mt-2" />
                <p className="text-xs text-gray-400">Document uploads extract chunks from PDFs and docs for contextual search and chat.</p>
              </div>
            </div>
          </div>
        </div>

        <div className="lg:col-span-8 flex flex-col gap-12">
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold flex items-center gap-3">
                <ShoppingBag className="text-indigo-400" />
                Intelligent Matches
              </h2>
              <span className="text-xs font-bold text-gray-500">{results.length} items found</span>
            </div>

            <div className="grid sm:grid-cols-3 gap-4">
              <div className="bg-[#0C0F16] border border-white/5 rounded-2xl p-5">
                <p className="text-[11px] uppercase tracking-widest text-gray-500 mb-2">Product Results</p>
                <p className="text-3xl font-bold">{productCount}</p>
              </div>
              <div className="bg-[#0C0F16] border border-white/5 rounded-2xl p-5">
                <p className="text-[11px] uppercase tracking-widest text-gray-500 mb-2">Document Chunks</p>
                <p className="text-3xl font-bold">{documentCount}</p>
              </div>
              <div className="bg-[#0C0F16] border border-white/5 rounded-2xl p-5">
                <p className="text-[11px] uppercase tracking-widest text-gray-500 mb-2">Modalities Active</p>
                <p className="text-3xl font-bold">3</p>
              </div>
            </div>

            {results.length === 0 && !isSearching && (
              <div className="bg-[#0C0F16] border border-white/5 rounded-3xl p-20 flex flex-col items-center justify-center text-center opacity-60">
                <ImageIcon size={48} className="mb-4 text-gray-700" />
                <h3 className="text-lg font-bold">No Intelligence Results</h3>
                <p className="text-sm text-gray-500">Use text, image, or PDF input to start retrieval.</p>
              </div>
            )}

            <div className="grid md:grid-cols-2 gap-6 h-fit max-h-[520px] overflow-y-auto pr-2 custom-scrollbar">
              {results.map((item, idx) => {
                const isDocument = item.result_type === 'document';
                return (
                  <div
                    key={`${item.product_id}-${idx}`}
                    className="bg-[#0C0F16] border border-white/5 rounded-2xl p-6 hover:border-indigo-500/30 transition-all group animate-fade-in"
                    style={{ animationDelay: `${idx * 0.08}s` }}
                  >
                    <div className="flex items-start justify-between mb-4 gap-4">
                      <div>
                        <div className="flex items-center gap-2 mb-2">
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-tighter ${isDocument ? 'bg-amber-500/10 text-amber-300' : 'bg-indigo-500/10 text-indigo-400'}`}>
                            {isDocument ? 'Document' : 'Product'}
                          </span>
                          {!isDocument && (
                            <span className="text-[10px] font-bold bg-white/5 text-gray-400 px-2 py-0.5 rounded-full uppercase tracking-tighter">
                              {item.graph_context?.category || 'Retail'}
                            </span>
                          )}
                        </div>
                        <h4 className="font-bold text-lg">{item.name}</h4>
                        {!isDocument && (
                          <p className="text-[11px] uppercase tracking-widest text-gray-500 mt-1">
                            {item.graph_context?.brand || 'Brand context available'}
                          </p>
                        )}
                      </div>
                      <ArrowRight className="text-gray-700 group-hover:text-indigo-400 transition-colors shrink-0" size={20} />
                    </div>

                    <p className="text-sm text-gray-400 mb-6 whitespace-pre-wrap">
                      {item.description}
                    </p>

                    <div className="bg-black/40 rounded-xl p-4 border border-white/5">
                      {isDocument ? (
                        <>
                          <p className="text-[10px] uppercase font-bold text-gray-500 mb-2 tracking-widest">Document Retrieval</p>
                          <p className="text-[11px] italic text-amber-300">Relevant chunk extracted from the uploaded file for downstream reasoning.</p>
                        </>
                      ) : (
                        <>
                          <p className="text-[10px] uppercase font-bold text-gray-500 mb-2 tracking-widest">Graph Context</p>
                          <p className="text-[11px] italic text-indigo-300">
                            "{item.graph_context?.reviews?.[0] || 'Brand and category context ready for the LLM layer.'}"
                          </p>
                        </>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="bg-[#0C0F16] border border-white/5 rounded-3xl flex flex-col h-[500px] overflow-hidden shadow-2xl">
            <div className="p-6 border-b border-white/5 bg-white/[0.02] flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-indigo-600/20 rounded-lg flex items-center justify-center text-indigo-400">
                  <MessageSquare size={18} />
                </div>
                <h3 className="font-bold">Product Intelligence Q&amp;A</h3>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Gemini Context-Aware Layer</span>
              </div>
            </div>

            <div className="flex-1 overflow-y-auto p-8 space-y-6 custom-scrollbar">
              {chatHistory.length === 0 && (
                <div className="h-full flex flex-col items-center justify-center text-center opacity-30">
                  <MessageSquare size={40} className="mb-4" />
                  <p className="text-sm">Ask about products, compare results, or summarize the uploaded PDF.</p>
                </div>
              )}
              {chatHistory.map((msg, i) => (
                <div key={`${msg.role}-${i}`} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] rounded-2xl p-4 text-sm leading-relaxed ${msg.role === 'user' ? 'bg-indigo-600 text-white' : 'bg-white/5 border border-white/5 text-gray-300'}`}>
                    {msg.content}
                  </div>
                </div>
              ))}
              {isChatting && (
                <div className="flex justify-start">
                  <div className="bg-white/5 border border-white/5 rounded-2xl p-4 flex gap-2">
                    <div className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce" />
                    <div className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce [animation-delay:0.2s]" />
                    <div className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce [animation-delay:0.4s]" />
                  </div>
                </div>
              )}
            </div>

            <div className="p-6 bg-black/20 border-t border-white/5">
              <div className="flex gap-4">
                <input
                  type="text"
                  placeholder="Ask about the product catalog or the uploaded document..."
                  className="flex-1 bg-white/5 border border-white/10 rounded-xl p-4 outline-none focus:border-indigo-500 transition-all font-medium"
                  value={chatMessage}
                  onChange={(e) => setChatMessage(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && sendChat()}
                />
                <button
                  onClick={sendChat}
                  className="bg-indigo-600 hover:bg-indigo-500 p-4 rounded-xl transition-all"
                >
                  <ArrowRight size={20} />
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>

      <style jsx global>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(255, 255, 255, 0.1);
          border-radius: 10px;
        }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in {
          animation: fadeIn 0.4s ease-out forwards;
        }
      `}</style>
    </div>
  );
}
