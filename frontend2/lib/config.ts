// API configuration
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

// API endpoints
export const ENDPOINTS = {
  PROCESS_QUERY: `${API_BASE_URL}/process_query`,
  FETCH_DATA: `${API_BASE_URL}/fetch_data`,
  ANALYZE_DATA: `${API_BASE_URL}/analyze_data`,
  QUERY_HISTORY: `${API_BASE_URL}/query_history`,
}

// API types
export interface ApiResponse<T = any> {
  status: 'success' | 'error'
  data?: T
  detail?: string
}

export interface QueryRequirements {
  endpoint: string
  params: {
    season?: string | string[]
    driver?: string | string[]
    constructor?: string
  }
}

export interface DriverData {
  driverId: string
  givenName: string
  familyName: string
  points: number
  position: number
  wins: number
  podiums: number
}

export interface QualifyingData {
  driverId: string
  position: number
  q1?: string
  q2?: string
  q3?: string
}

export interface LapTimeData {
  driverId: string
  lap: number
  position: number
  time: string
}

export interface AnalysisResult {
  summary?: string
  data?: any
  visualization?: string
  rawData?: any
} 