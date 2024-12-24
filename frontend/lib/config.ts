// API configuration
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// API endpoints
export const ENDPOINTS = {
  // Legacy endpoints
  CONNECT_USER: `${API_BASE_URL}/api/v1/connect_user`,
  FETCH_DATA: `${API_BASE_URL}/api/v1/fetch_data`,
  GENERATE_CODE: `${API_BASE_URL}/api/v1/generate_code`,
  EXECUTE_CODE: `${API_BASE_URL}/api/v1/execute_code`,
  
  // Platform endpoints
  PLATFORMS: `${API_BASE_URL}/api/platforms`,
  PLATFORM_VERIFY: (platform: string) => `${API_BASE_URL}/api/platforms/${platform}/verify`,
  PLATFORM_CONNECT: (platform: string) => `${API_BASE_URL}/api/platforms/${platform}/connect`,
  PLATFORM_QUERIES: (platform: string) => `${API_BASE_URL}/api/platforms/${platform}/queries`,
  PLATFORM_ANALYZE: `${API_BASE_URL}/api/platforms/analyze`
}

// API types
export interface ApiResponse<T = any> {
  status: 'success' | 'error'
  data?: T
  detail?: string
}

export interface PlatformData {
  id: string
  name: string
  description: string
}

export interface TypeRacerStats {
  avgSpeed: number
  bestSpeed: number
  gamesPlayed: number
}

export interface F1Stats {
  givenName: string
  familyName: string
  Constructor: {
    name: string
  }
  position: number
  points: number
  wins: number
}

export interface UserData {
  typeracer?: TypeRacerStats
  f1?: F1Stats
}

export const EXAMPLE_QUERIES = {
  typeracer: [
    "Show my average WPM for the last 10 races",
    "Plot my WPM trend over time",
    "Calculate my accuracy trend",
    "Show my performance by time of day"
  ],
  f1: [
    "Compare my performance with teammate in last 5 races",
    "Show my qualifying positions vs race finishes",
    "Analyze my points progression this season",
    "Plot my fastest laps compared to race winners"
  ]
} 