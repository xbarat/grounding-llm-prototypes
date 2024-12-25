"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

interface User {
  platform: string;
  identifier: string;
  data: any;
}

interface AuthState {
  user: User | null;
  connect: (platform: string, identifier: string) => Promise<void>;
  disconnect: () => void;
}

export const useAuth = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      connect: async (platform: string, identifier: string) => {
        try {
          // First verify the connection
          const response = await fetch("/api/v1/platforms/connect", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ platform, identifier }),
          });

          if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || "Failed to connect");
          }

          const { data } = await response.json();

          // Store the connection
          set({
            user: {
              platform,
              identifier,
              data,
            },
          });
        } catch (error) {
          console.error("Connection error:", error);
          throw error;
        }
      },
      disconnect: () => {
        set({ user: null });
      },
    }),
    {
      name: "auth-storage",
    }
  )
);

// Helper hook to get platform-specific data
export const usePlatformData = () => {
  const user = useAuth((state) => state.user);

  const fetchPlatformData = async (query: string, params?: any) => {
    if (!user) {
      throw new Error("Not connected to any platform");
    }

    const response = await fetch("/api/v1/platforms/analyze", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        platform: user.platform,
        identifier: user.identifier,
        query,
        params,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Failed to fetch data");
    }

    return response.json();
  };

  return {
    platform: user?.platform,
    identifier: user?.identifier,
    data: user?.data,
    fetchPlatformData,
  };
}; 