import request from './index';

export const getAgentList = () => request.get('api/chat/agent_list');
export const createAgent = (data) => request.post('api/chat/create_agent', data).then(res => res.data);
export const updateAgent = (agentId, data) => request.put(`api/chat/update_agent/${agentId}`, data).then(res => res.data);
export const deleteAgent = (agentId) => request.delete(`api/chat/delete_agent/${agentId}`);
export const getAgentDetail = (agentId) => request.get(`api/chat/agent_detail/${agentId}`);
export const chatWithAgent = (agentId, content) => request.post(`api/chat/chat_with_agent/${agentId}`, { content });
export const getChatHistory = (agentId) => request.get(`api/chat/chat_history/${agentId}`);
export const clearChatHistory = (agentId) => request.delete(`api/chat/chat_history/${agentId}`);
export const uploadKnowledgeFiles = (formData) => request.post('api/upload_files', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
export const uploadAgentPhoto = (formData) => request.post('api/chat/upload_photo', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
}).then(res => res.data);

// 添加网页URL到知识库
export function addUrlToKnowledge(url) {
  const formData = new FormData();
  formData.append('url', url);
  return request.post('api/add_urls', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
}