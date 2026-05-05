import axios from 'axios';

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
});

export const setupSSE = (onMessage) => {
  const url = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/stream`;
  const eventSource = new EventSource(url);
  eventSource.onmessage = (event) => {
    try {
        const data = JSON.parse(event.data);
        onMessage(data);
    } catch (e) {
        console.error("SSE parse error", e);
    }
  };
  return eventSource;
};
