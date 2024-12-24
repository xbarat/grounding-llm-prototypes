import { create } from 'zustand';

interface User {
  platform: string;
  identifier: string;
  data?: any;
}

interface AuthState {
  user: User | null;
  isConnecting: boolean;
  error: string | null;
  connect: (platform: string, identifier: string) => Promise<void>;
  disconnect: () => void;
}

export const useAuth = create<AuthState>((set) => ({
  user: null,
  isConnecting: false,
  error: null,

  connect: async (platform: string, identifier: string) => {
    set({ isConnecting: true, error: null });

    try {
      // First verify the platform and identifier
      const verifyResponse = await fetch(`/api/platforms/${platform}/verify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ identifier }),
      });

      if (!verifyResponse.ok) {
        const error = await verifyResponse.json();
        throw new Error(error.detail || 'Failed to verify user');
      }

      // Then fetch initial data
      const dataResponse = await fetch(`/api/platforms/${platform}/connect`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ identifier }),
      });

      if (!dataResponse.ok) {
        const error = await dataResponse.json();
        throw new Error(error.detail || 'Failed to fetch user data');
      }

      const data = await dataResponse.json();

      // Store the connection in localStorage
      localStorage.setItem('giraffe_connection', JSON.stringify({
        platform,
        identifier,
        timestamp: new Date().toISOString(),
      }));

      set({
        user: {
          platform,
          identifier,
          data: data.data,
        },
        isConnecting: false,
        error: null,
      });
    } catch (error) {
      set({
        user: null,
        isConnecting: false,
        error: error instanceof Error ? error.message : 'Failed to connect',
      });
      throw error;
    }
  },

  disconnect: () => {
    localStorage.removeItem('giraffe_connection');
    set({ user: null, error: null });
  },
}));

// Hook to restore connection on page load
export const useRestoreConnection = () => {
  const { connect } = useAuth();

  const restore = async () => {
    const saved = localStorage.getItem('giraffe_connection');
    if (saved) {
      try {
        const { platform, identifier } = JSON.parse(saved);
        await connect(platform, identifier);
      } catch (error) {
        console.error('Failed to restore connection:', error);
        localStorage.removeItem('giraffe_connection');
      }
    }
  };

  return restore;
}; 