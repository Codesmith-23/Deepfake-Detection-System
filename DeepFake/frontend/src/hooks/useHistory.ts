import { useState, useCallback } from "react";
import { HistoryEntry } from "@/types";
import { apiService } from "@/lib/api";

export function useHistory() {
  const [isLoading, setIsLoading] = useState(false);

  // 1. Fetch History (now uses JWT from localStorage)
  const getHistoryfromAPI = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await apiService.getHistory();
      return data as HistoryEntry[];
    } catch (error) {
      console.error("Failed to load detection history:", error);
      return [];
    } finally {
      setIsLoading(false);
    }
  }, []);

  // 2. Remove Entry (now requires JWT)
  const removeEntry = useCallback(async (id: string) => {
    try {
      await apiService.deleteHistoryEntry(id);
      return true;
    } catch (error) {
      console.error("Failed to delete entry:", error);
      throw error;
    }
  }, []);

  return {
    isLoading,
    getHistoryfromAPI,
    removeEntry,
  };
}
