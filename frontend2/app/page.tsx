'use client'

import { useState } from 'react'
import { ArrowRight } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'
import { QueryResults } from '@/components/query-results'
import { ENDPOINTS, type ApiResponse, type QueryRequirements, type AnalysisResult } from '@/lib/config'
import { Sidebar } from '@/components/sidebar'

// Example F1 queries that showcase our analysis capabilities
const EXAMPLE_QUERIES = [
  "Show Max Verstappen's performance trend from 2021 to 2023",
  "Compare Lewis Hamilton's points progression across 2021-2023 seasons",
  "How has Fernando Alonso's average finishing position changed from 2021 to 2023?",
  "Show Charles Leclerc's qualifying performance trend from 2021 to 2023"
]

export default function Page() {
  const [query, setQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState<AnalysisResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleAnalysis = async (queryText: string, isFollowUp: boolean = false) => {
    if (!queryText.trim()) return

    setIsLoading(true)
    setError(null)
    if (!isFollowUp) setResults(null)

    try {
      if (!isFollowUp) {
        // Step 1: Process the natural language query
        const processResponse = await fetch(ENDPOINTS.PROCESS_QUERY, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: queryText })
        })

        const processData: ApiResponse<QueryRequirements> = await processResponse.json()
        if (processData.status !== 'success' || !processData.data) {
          throw new Error(processData.detail || 'Failed to process query')
        }

        // Step 2: Fetch F1 data based on requirements
        const fetchResponse = await fetch(ENDPOINTS.FETCH_DATA, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(processData.data)
        })

        const fetchData: ApiResponse<any> = await fetchResponse.json()
        if (fetchData.status !== 'success' || !fetchData.data) {
          throw new Error(fetchData.detail || 'Failed to fetch data')
        }

        // Step 3: Generate analysis and visualization
        const analyzeResponse = await fetch(ENDPOINTS.ANALYZE_DATA, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            query: queryText,
            data: fetchData.data,
            requirements: processData.data
          })
        })

        const analyzeData: ApiResponse<AnalysisResult> = await analyzeResponse.json()
        if (analyzeData.status !== 'success' || !analyzeData.data) {
          throw new Error(analyzeData.detail || 'Failed to analyze data')
        }

        setResults(analyzeData.data)

        // Step 4: Save to query history (optional)
        fetch(ENDPOINTS.QUERY_HISTORY, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            query: queryText,
            requirements: processData.data,
            result: analyzeData.data
          })
        }).catch(console.error) // Non-blocking
      } else {
        // For follow-up queries, use the existing data
        const analyzeResponse = await fetch(ENDPOINTS.ANALYZE_DATA, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            query: queryText,
            data: results?.rawData,
            requirements: {
              endpoint: '/api/f1/follow-up',
              params: {}
            }
          })
        })

        const analyzeData: ApiResponse<AnalysisResult> = await analyzeResponse.json()
        if (analyzeData.status !== 'success' || !analyzeData.data) {
          throw new Error(analyzeData.detail || 'Failed to analyze data')
        }

        setResults(analyzeData.data)
      }
    } catch (err) {
      console.error('Analysis error:', err)
      setError(err instanceof Error ? err.message : 'Failed to analyze data')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    await handleAnalysis(query)
  }

  const handleFollowUpQuery = async (followUpQuery: string) => {
    await handleAnalysis(followUpQuery, true)
  }

  return (
    <div className="flex flex-col min-h-screen bg-[#1C1C1C] text-white">
      <div className="flex h-screen">
        <Sidebar currentResults={results} onFollowUpQuery={handleFollowUpQuery} />
        <div className="flex-1 flex flex-col items-center justify-center px-4 py-12">
          <h1 className="text-4xl font-semibold mb-8 text-white/90">
            Ask anything, See the answer
          </h1>

          <form onSubmit={handleSubmit} className="w-full max-w-[600px] mb-8">
            <div className="relative">
              <Input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask about F1 performance, trends, and statistics..."
                className="w-full bg-[#2C2C2C] border-0 h-12 pl-4 pr-12 rounded-xl placeholder:text-white/40 focus-visible:ring-1 focus-visible:ring-white/20"
              />
              <Button 
                size="icon" 
                type="submit" 
                disabled={isLoading}
                className="absolute right-2 top-1/2 -translate-y-1/2 bg-white/10 hover:bg-white/20 rounded-full w-8 h-8 flex items-center justify-center"
              >
                <ArrowRight className="h-4 w-4" />
              </Button>
            </div>
          </form>

          {isLoading && (
            <Card className="w-full max-w-[600px] bg-[#2C2C2C] border-0">
              <div className="animate-pulse space-y-4 p-4">
                <div className="h-4 bg-white/10 rounded w-3/4" />
                <div className="h-4 bg-white/10 rounded w-1/2" />
                <div className="h-32 bg-white/10 rounded" />
              </div>
            </Card>
          )}

          {error && (
            <Card className="w-full max-w-[600px] bg-[#2C2C2C] border-0 p-4">
              <p className="text-red-400">{error}</p>
            </Card>
          )}

          {results && <QueryResults results={results} />}

          <div className="w-full max-w-[600px] mt-8">
            <h3 className="text-sm text-white/60 mb-2 px-2">Try these examples:</h3>
            <div className="bg-transparent border border-white/10 rounded-xl p-2">
              <div className="grid grid-cols-1 gap-2">
                {EXAMPLE_QUERIES.map((example, index) => (
                  <Button 
                    key={index}
                    variant="ghost" 
                    className="w-full justify-start gap-2 text-white/60 hover:text-white text-sm"
                    onClick={() => setQuery(example)}
                  >
                    {example}
                  </Button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

