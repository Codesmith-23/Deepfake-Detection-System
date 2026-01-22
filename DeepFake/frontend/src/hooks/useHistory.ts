import { useState, useCallback } from 'react';
import axios from 'axios';
import { HistoryEntry } from '@/types';

// ✅ POINT TO YOUR FLASK BACKEND
const API_URL = 'http://127.0.0.1:5000'; 

export function useHistory() {
  const [isLoading, setIsLoading] = useState(false); // Start false so we don't block UI immediately

  // 1. Fetch History
  // Your app.py expects POST to /history with a JSON body {"user_id": "..."}
  const getHistoryfromAPI = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await axios.post(`${API_URL}/history`, {
        user_id: 'guest' // Matches the default in your app.py
      });
      return response.data as HistoryEntry[];
    } catch (error) {
      console.error('Failed to load detection history:', error);
      return [];
    } finally {
      setIsLoading(false);
    }
  }, []);

  // 2. Remove Entry
  // Your app.py expects DELETE to /history/delete/<int:id>
  const removeEntry = useCallback(async (id: string) => {
    try {
      await axios.delete(`${API_URL}/history/delete/${id}`);
      return true;
    } catch (error) {
      console.error('Failed to delete entry:', error);
      throw error;
    }
  }, []);

  return {
    isLoading,
    getHistoryfromAPI,
    removeEntry
  };
}