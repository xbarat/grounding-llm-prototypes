// API configuration
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

// API endpoints
export const ENDPOINTS = {
  CONNECT_USER: `${API_BASE_URL}/connect_user`,
  FETCH_DATA: `${API_BASE_URL}/fetch_data`,
  LOAD_DATA: `${API_BASE_URL}/load_data`,
  GENERATE_CODE: `${API_BASE_URL}/generate_code`,
  EXECUTE_CODE: `${API_BASE_URL}/execute_code`,
  QUERY_GUIDANCE: `${API_BASE_URL}/query_guidance`,
  PLAYER_DASHBOARD: `${API_BASE_URL}/player_dashboard`,
}

// API types
export interface ApiResponse<T = any> {
  status: 'success' | 'error'
  data?: T
  detail?: string
}

export interface UserStats {
  username: string
  // Add other user stats fields from the backend response
}

export interface TypeRacerData {
  // Add fields from the backend response for race data
  speed: number
  accuracy: number
  time: number
  rank?: number
  game_entry: number
  text_id?: number
  skill_level?: string
  num_players?: number
} 