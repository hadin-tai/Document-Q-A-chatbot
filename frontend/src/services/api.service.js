import api from '../api/axios';

export const documentService = {
  getAll: () => api.get('/documents'),
  upload: (formData) => api.post('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  delete: (id) => api.delete(`/documents/${id}`),
};

export const chatService = {
  send: (document_id, question) => api.post('/chat', { document_id, question }),
  getHistory: (document_id) => api.get(`/chat/${document_id}`),
};
