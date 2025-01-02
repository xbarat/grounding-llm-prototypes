'use client'

import { useState } from 'react'
import { ArrowRight } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'
import { QueryResults } from '@/components/query-results'
import { ENDPOINTS } from '@/lib/config'

// Example queries that worked well in our testing
const EXAMPLE_QUERIES = [
  "Show my average WPM for the last 10 races",
  "Plot my WPM trend over time",
  "Calculate my accuracy trend",
  "Show my performance by time of day"
]

export default function Page() {
  const [query, setQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return

    setIsLoading(true)
    setError(null)
    setResults(null)

    try {
      // First, generate code
      const generateResponse = await fetch(ENDPOINTS.GENERATE_CODE, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      })

      const generateData = await generateResponse.json()
      if (generateData.status !== 'success') {
        throw new Error(generateData.detail || 'Failed to generate code')
      }

      // Then execute the generated code
      const executeResponse = await fetch(ENDPOINTS.EXECUTE_CODE, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: generateData.data.code })
      })

      const executeData = await executeResponse.json()
      if (executeData.status !== 'success') {
        throw new Error(executeData.detail || 'Failed to execute code')
      }

      setResults({
        result: executeData.data.result,
        figure: executeData.data.figure,
        code: generateData.data.code
      })
    } catch (err) {
      console.error('Analysis error:', err)
      setError(err instanceof Error ? err.message : 'Failed to analyze data')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col min-h-screen bg-[#1C1C1C] text-white">
      <div className="flex-1 flex flex-col items-center justify-center px-4 py-12">
        <h1 className="text-4xl font-semibold mb-8 text-white/90">
          What graphs do you want to visualize?
        </h1>

        <form onSubmit={handleSubmit} className="w-full max-w-[600px] mb-8">
          <div className="relative">
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask anything..."
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
            </div>
          </Card>
        )}

        {error && (
          <Card className="w-full max-w-[600px] bg-[#2C2C2C] border-0 p-4">
            <p className="text-red-400">{error}</p>
          </Card>
        )}

        {results && <QueryResults results={results} />}

        <div className="w-full max-w-[600px] bg-transparent border border-white/10 rounded-xl p-2">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {EXAMPLE_QUERIES.map((example, index) => (
              <Button 
                key={index}
                variant="ghost" 
                className="w-full justify-start gap-2 text-white/60 hover:text-white"
                onClick={() => setQuery(example)}
              >
                {example}
              </Button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

