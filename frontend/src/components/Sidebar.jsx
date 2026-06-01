import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { 
  FileText, 
  Plus, 
  Trash2, 
  LogOut, 
  Search, 
  Loader2, 
  Cpu,
  User as UserIcon
} from 'lucide-react';

const Sidebar = ({ 
  documents, 
  selectedDoc, 
  onSelect, 
  onUpload, 
  onDelete, 
  isUploading 
}) => {
  const { user, logout } = useAuth();
  const [searchTerm, setSearchTerm] = useState('');

  const filteredDocs = documents.filter(doc => 
    doc.file_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="flex h-screen w-80 flex-col bg-slate-900 border-r border-slate-800 shrink-0">
      {/* App Header */}
      <div className="flex h-16 items-center px-6 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary-500 text-white shadow-lg shadow-primary-500/20">
            <Cpu size={20} />
          </div>
          <span className="text-lg font-bold text-white tracking-tight">RAG Assistant</span>
        </div>
      </div>

      {/* Action Section */}
      <div className="p-6 space-y-4">
        <button
          onClick={() => document.getElementById('file-upload').click()}
          disabled={isUploading}
          className="flex w-full items-center justify-center gap-2 bg-primary-600 hover:bg-primary-500 disabled:opacity-50 text-white rounded-xl py-3 text-sm font-bold transition-all shadow-lg shadow-primary-500/20"
        >
          {isUploading ? <Loader2 className="animate-spin" size={18} /> : <Plus size={18} />}
          {isUploading ? 'Uploading...' : 'Upload PDF'}
        </button>
        <input
          id="file-upload"
          type="file"
          accept=".pdf"
          className="hidden"
          onChange={onUpload}
        />

        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={16} />
          <input
            type="text"
            placeholder="Search documents..."
            className="w-full bg-slate-800/50 border border-slate-700/50 rounded-xl py-2.5 pl-10 pr-4 text-sm text-slate-300 focus:outline-none focus:border-primary-500 transition-all placeholder-slate-500"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      {/* Document List Section */}
      <div className="flex-1 overflow-y-auto px-4 pb-6 space-y-2 scrollbar-hide">
        <div className="px-2 mb-2">
          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Your Documents</span>
        </div>
        
        {filteredDocs.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-center px-4 bg-slate-800/20 rounded-2xl border border-dashed border-slate-800">
            <div className="h-10 w-10 rounded-full bg-slate-800/50 flex items-center justify-center text-slate-600 mb-3">
              <FileText size={20} />
            </div>
            <p className="text-xs text-slate-500">No documents found</p>
          </div>
        ) : (
          filteredDocs.map((doc) => (
            <div
              key={doc.id}
              onClick={() => onSelect(doc)}
              className={`group relative flex items-center gap-3 p-3 rounded-xl cursor-pointer border transition-all ${
                selectedDoc?.id === doc.id
                  ? 'bg-primary-500/10 border-primary-500/30'
                  : 'bg-transparent border-transparent hover:bg-slate-800/50 hover:border-slate-700/50'
              }`}
            >
              <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-lg ${
                selectedDoc?.id === doc.id ? 'bg-primary-500 text-white' : 'bg-slate-800 text-slate-400'
              }`}>
                <FileText size={20} />
              </div>
              
              <div className="flex-1 min-w-0">
                <p className={`text-sm font-semibold truncate ${
                  selectedDoc?.id === doc.id ? 'text-primary-400' : 'text-slate-200'
                }`}>
                  {doc.file_name}
                </p>
                <p className="text-[10px] text-slate-500 mt-0.5 font-medium uppercase tracking-tighter">
                  {new Date(doc.created_at).toLocaleDateString()}
                </p>
              </div>

              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete(doc.id);
                }}
                className="opacity-0 group-hover:opacity-100 p-1.5 text-slate-500 hover:text-red-400 hover:bg-red-500/10 rounded-md transition-all"
              >
                <Trash2 size={16} />
              </button>
            </div>
          ))
        )}
      </div>

      {/* User & Logout Section */}
      <div className="p-4 border-t border-slate-800">
        <div className="flex items-center gap-3 px-3 py-3 rounded-xl bg-slate-800/30 mb-4 border border-slate-800/50">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary-500/10 text-primary-400 border border-primary-500/20 shadow-sm">
            <UserIcon size={20} />
          </div>
          <div className="flex-1 overflow-hidden">
            <p className="text-sm font-bold text-white truncate">{user?.name || 'User'}</p>
            <p className="text-[10px] text-slate-500 truncate font-medium">{user?.email}</p>
          </div>
        </div>
        
        <button
          onClick={logout}
          className="flex w-full items-center justify-center gap-2 px-3 py-2.5 rounded-xl text-sm font-bold text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition-all border border-transparent hover:border-red-500/20"
        >
          <LogOut size={18} />
          Logout
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
