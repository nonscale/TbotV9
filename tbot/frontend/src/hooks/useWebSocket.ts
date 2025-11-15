// tbot/frontend/src/hooks/useWebSocket.ts
import { useState, useEffect, useRef } from 'react';

interface WebSocketMessage {
  event: string;
  payload: any;
}

export function useWebSocket(url: string) {
  const [messages, setMessages] = useState<WebSocketMessage[]>([]);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    const connect = () => {
      ws.current = new WebSocket(url);

      ws.current.onopen = () => {
        console.log('WebSocket connected');
      };

      ws.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          setMessages((prevMessages) => [...prevMessages, message]);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.current.onclose = () => {
        console.log('WebSocket disconnected. Trying to reconnect...');
        // Simple reconnect logic
        setTimeout(connect, 5000);
      };

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        ws.current?.close();
      };
    };

    connect();

    return () => {
      ws.current?.close();
    };
  }, [url]);

  return messages;
}
