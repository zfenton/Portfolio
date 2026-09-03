import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface User {
  id: number;
  name: string;
  created_at: string;
}

export interface ActivityOption {
  id: number;
  option_text: string;
  order: number;
}

export interface Activity {
  id: number;
  question: string;
  order: number;
  options: ActivityOption[];
}

export interface Vote {
  activity_id: number;
  option_id: number;
}

export interface Message {
  message_text: string;
}

export interface VoteCount {
  option_id: number;
  option_text: string;
  vote_count: number;
}

export interface ActivityResult {
  activity_id: number;
  question: string;
  order: number;
  vote_counts: VoteCount[];
  total_votes: number;
}

export interface MessageResponse {
  id: number;
  user_id: number;
  message_text: string;
  created_at: string;
}

export const userApi = {
  register: async (name: string): Promise<User> => {
    const response = await api.post('/api/users/register', { name });
    return response.data;
  },
  getUser: async (userId: number): Promise<User> => {
    const response = await api.get(`/api/users/${userId}`);
    return response.data;
  },
};

export const votingApi = {
  getActivities: async (): Promise<Activity[]> => {
    const response = await api.get('/api/voting/activities');
    return response.data;
  },
  submitVote: async (userId: number, vote: Vote): Promise<void> => {
    await api.post(`/api/voting/vote/${userId}`, vote);
  },
  getUserVotes: async (userId: number): Promise<any[]> => {
    const response = await api.get(`/api/voting/user-votes/${userId}`);
    return response.data;
  },
};

export const messageApi = {
  submitMessage: async (userId: number, message: Message): Promise<void> => {
    await api.post(`/api/messages/${userId}`, message);
  },
};

export const adminApi = {
  getResults: async (): Promise<ActivityResult[]> => {
    const response = await api.get('/api/anniversary-celebration-results/activities');
    return response.data;
  },
  getMessages: async (): Promise<MessageResponse[]> => {
    const response = await api.get('/api/anniversary-celebration-results/messages');
    return response.data;
  },
};

export default api;
