import React, { useState } from 'react';
import { 
  FileText, 
  Upload, 
  Trash2, 
  Search, 
  Loader2, 
  Plus,
  AlertCircle
} from 'lucide-react';

const DocumentPanel = ({ 
  documents, 
  selectedDoc, 
  onSelect, 
  onUpload, 
  onDelete, 
  isUploading 
}) => {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredDocs = documents.filter(doc => 
    doc.file_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="flex h-screen w-80 flex-col bg-slate-950 border-r border-slate-800">
      <div className="p-6">
        <h2 className="text-xl font-bold text-white mb-6">Documents</h2>
        
        <div className="relative mb-6">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={16} />
          <input
            type="text"
            placeholder="Search documents..."
            className="w-full bg-slate-900 border border-slate-800 rounded-lg py-2 pl-10 pr-4 text-sm text-slate-300 focus:outline-none focus:border-primary-500 transition-all"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <button
          onClick={() => document.getElementById('file-upload').click()}
          disabled={isUploading}
          className="flex w-full items-center justify-center gap-2 bg-primary-600 hover:bg-primary-500 disabled:opacity-50 text-white rounded-lg py-2.5 text-sm font-semibold transition-all shadow-lg shadow-primary-500/20"
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
      </div>

      <div className="flex-1 overflow-y-auto px-4 pb-6 space-y-2 scrollbar-hide">
        {filteredDocs.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-center px-4">
            <div className="h-12 w-12 rounded-full bg-slate-900 flex items-center justify-center text-slate-600 mb-4">
              <FileText size={24} />
            </div>
            <p className="text-sm text-slate-500">No documents found</p>
          </div>
        ) : (
          filteredDocs.map((doc) => (
            <div
              key={doc.id}
              onClick={() => onSelect(doc)}
              className={`group relative flex items-center gap-3 p-3 rounded-xl cursor-pointer border transition-all ${
                selectedDoc?.id === doc.id
                  ? 'bg-primary-500/10 border-primary-500/30'
                  : 'bg-slate-900/50 border-slate-800/50 hover:bg-slate-900 hover:border-slate-700'
              }`}
            >
              <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-lg ${
                selectedDoc?.id === doc.id ? 'bg-primary-500 text-white' : 'bg-slate-800 text-slate-400'
              }`}>
                <FileText size={20} />
              </div>
              
              <div className="flex-1 min-w-0">
                <p className={`text-sm font-medium truncate ${
                  selectedDoc?.id === doc.id ? 'text-primary-400' : 'text-slate-200'
                }`}>
                  {doc.file_name}
                </p>
                <p className="text-xs text-slate-500 mt-0.5">
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
    </div>
  );
};

export default DocumentPanel;
