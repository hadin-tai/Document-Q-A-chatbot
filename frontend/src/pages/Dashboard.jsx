import React, { useState, useEffect } from 'react';
import Sidebar from '../components/Sidebar';
import ChatWindow from '../components/ChatWindow';
import { documentService, chatService } from '../services/api.service';

const Dashboard = () => {
  const [documents, setDocuments] = useState([]);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isLoadingChat, setIsLoadingChat] = useState(false);

  // Fetch documents on mount
  useEffect(() => {
    fetchDocuments();
  }, []);

  // Persist selected document after refresh
  useEffect(() => {
    const savedDocId = localStorage.getItem('selectedDocId');
    if (savedDocId && documents.length > 0) {
      const doc = documents.find(d => d.id === savedDocId);
      if (doc) setSelectedDoc(doc);
    }
  }, [documents]);

  // Update localStorage when selectedDoc changes
  useEffect(() => {
    if (selectedDoc) {
      localStorage.setItem('selectedDocId', selectedDoc.id);
      fetchChatHistory(selectedDoc.id);
    } else {
      localStorage.removeItem('selectedDocId');
      setMessages([]);
    }
  }, [selectedDoc]);

  const fetchDocuments = async () => {
    try {
      const response = await documentService.getAll();
      setDocuments(response.data);
    } catch (error) {
      console.error('Error fetching documents:', error);
    }
  };

  const fetchChatHistory = async (docId) => {
    try {
      setIsLoadingChat(true);
      const response = await chatService.getHistory(docId);
      const history = response.data.map(msg => ({
        role: msg.role,
        content: msg.message,
        timestamp: msg.created_at
      }));
      setMessages(history);
    } catch (error) {
      console.error('Error fetching chat history:', error);
    } finally {
      setIsLoadingChat(false);
    }
  };

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setIsUploading(true);
    try {
      const response = await documentService.upload(formData);
      
      const newDoc = response.data;
      setDocuments(prev => [newDoc, ...prev]);
      setSelectedDoc(newDoc);
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to upload document');
    } finally {
      setIsUploading(false);
      e.target.value = ''; // Reset input
    }
  };

  const handleDelete = async (docId) => {
    if (!window.confirm('Are you sure you want to delete this document?')) return;

    try {
      await documentService.delete(docId);
      setDocuments(prev => prev.filter(doc => doc.id !== docId));
      if (selectedDoc?.id === docId) {
        setSelectedDoc(null);
      }
    } catch (error) {
      alert('Failed to delete document');
    }
  };

  const handleSendMessage = async (question) => {
    if (!selectedDoc) return;

    const userMsg = { 
      role: 'user', 
      content: question, 
      timestamp: new Date().toISOString() 
    };
    
    setMessages(prev => [...prev, userMsg]);
    setIsLoadingChat(true);

    try {
      const response = await chatService.send(selectedDoc.id, question);

      const aiMsg = { 
        role: 'assistant', 
        content: response.data.answer, 
        timestamp: new Date().toISOString() 
      };
      setMessages(prev => [...prev, aiMsg]);
    } catch (error) {
      const errorMsg = { 
        role: 'assistant', 
        content: 'Sorry, I encountered an error processing your request.', 
        timestamp: new Date().toISOString() 
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoadingChat(false);
    }
  };

  return (
    <div className="flex h-screen w-full bg-slate-950 overflow-hidden">
      <Sidebar 
        documents={documents}
        selectedDoc={selectedDoc}
        onSelect={setSelectedDoc}
        onUpload={handleUpload}
        onDelete={handleDelete}
        isUploading={isUploading}
      />
      <ChatWindow 
        selectedDoc={selectedDoc}
        messages={messages}
        onSendMessage={handleSendMessage}
        isLoading={isLoadingChat}
      />
    </div>
  );
};

export default Dashboard;
