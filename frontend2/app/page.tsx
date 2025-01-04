'use client'

import { useState } from 'react'
import { ArrowRight, Share2, RefreshCw, ThumbsUp, ThumbsDown, Copy, MoreHorizontal, 
  Image, FileText, Code, PenTool, BarChart2, MoreHorizontal as More, Plus } from 'lucide-react'
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

interface QueryThread {
  id: string;
  query: string;
  result: AnalysisResult;
  isFollowUp: boolean;
}

interface ActionToolbarProps {
  onShare: () => void
  onRewrite: () => void
  onLike: () => void
  onDislike: () => void
  onCopy: () => void
  onMore: () => void
}

const ActionToolbar = ({ onShare, onRewrite, onLike, onDislike, onCopy, onMore }: ActionToolbarProps) => {
  return (
    <div className="flex items-center gap-2 mt-4 border-t border-white/10 pt-4">
      <Button
        variant="ghost"
        size="sm"
        className="text-white/60 hover:text-white hover:bg-white/10"
        onClick={onShare}
      >
        <Share2 className="h-4 w-4 mr-2" />
        Share
      </Button>
      <Button
        variant="ghost"
        size="sm"
        className="text-white/60 hover:text-white hover:bg-white/10"
        onClick={onRewrite}
      >
        <RefreshCw className="h-4 w-4 mr-2" />
        Rewrite
      </Button>
      <div className="flex-1" />
      <Button
        variant="ghost"
        size="icon"
        className="text-white/60 hover:text-white hover:bg-white/10"
        onClick={onLike}
      >
        <ThumbsUp className="h-4 w-4" />
      </Button>
      <Button
        variant="ghost"
        size="icon"
        className="text-white/60 hover:text-white hover:bg-white/10"
        onClick={onDislike}
      >
        <ThumbsDown className="h-4 w-4" />
      </Button>
      <Button
        variant="ghost"
        size="icon"
        className="text-white/60 hover:text-white hover:bg-white/10"
        onClick={onCopy}
      >
        <Copy className="h-4 w-4" />
      </Button>
      <Button
        variant="ghost"
        size="icon"
        className="text-white/60 hover:text-white hover:bg-white/10"
        onClick={onMore}
      >
        <More className="h-4 w-4" />
      </Button>
    </div>
  )
}

interface SuggestionBoxProps {
  onSuggestionClick: (suggestion: string) => void
}

const SuggestionBox = ({ onSuggestionClick }: SuggestionBoxProps) => {
  // Example follow-up suggestions
  const FOLLOW_UP_SUGGESTIONS = [
    "Add a trend line to the visualization",
    "Compare with teammate's performance",
    "Show race-by-race breakdown",
    "Analyze qualifying vs race performance"
  ]

  return (
    <div className="w-full mt-4">
      <h3 className="text-sm text-white/60 mb-2 px-2">Try these follow-ups:</h3>
      <div className="bg-transparent border border-white/10 rounded-xl p-2">
        <div className="grid grid-cols-1 gap-2">
          {FOLLOW_UP_SUGGESTIONS.map((suggestion, index) => (
            <Button 
              key={index}
              variant="ghost" 
              className="w-full justify-start gap-2 text-white/60 hover:text-white text-sm"
              onClick={() => onSuggestionClick(suggestion)}
            >
              {suggestion}
            </Button>
          ))}
        </div>
      </div>
    </div>
  )
}

export default function Page() {
  const [query, setQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [queryThread, setQueryThread] = useState<QueryThread[]>([])
  const [error, setError] = useState<string | null>(null)
  const [followUpQuery, setFollowUpQuery] = useState('')
  const [isSubmittingFollowUp, setIsSubmittingFollowUp] = useState(false)

  const handleHistoryItemClick = (thread: any[]) => {
    if (thread && thread.length > 0) {
      setQueryThread(thread as QueryThread[]);
    }
  };

  const handleAnalysis = async (queryText: string, isFollowUp: boolean = false) => {
    if (!queryText.trim()) return

    setIsLoading(true)
    setError(null)

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

        setQueryThread([{
          id: Date.now().toString(),
          query: queryText,
          result: analyzeData.data,
          isFollowUp: false
        }])

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
            data: queryThread[queryThread.length - 1].result.rawData,
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

        setQueryThread(prev => [...prev, {
          id: Date.now().toString(),
          query: queryText,
          result: analyzeData.data,
          isFollowUp: true
        } as QueryThread])
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

  const handleFollowUpSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!followUpQuery.trim()) return
    setIsSubmittingFollowUp(true)
    await handleAnalysis(followUpQuery, true)
    setFollowUpQuery('')
    setIsSubmittingFollowUp(false)
  }

  return (
    <div className="flex flex-col min-h-screen bg-[#1C1C1C] text-white">
      <div className="flex h-screen">
        <Sidebar onHistoryItemClick={handleHistoryItemClick} />
        <main className="flex-1 relative w-full">
          <div className="flex flex-col px-4 md:px-8 py-6 md:py-12 h-full overflow-y-auto">
            <div className="w-full max-w-[800px] mx-auto mb-24">
              {queryThread.length === 0 && (
                <>
                  <h1 className="text-4xl font-semibold mb-8 text-white/90 text-center">
                    Ask anything, See the answer
                  </h1>

                  <form onSubmit={handleSubmit} className="w-full max-w-[600px] mx-auto mb-8">
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

                  <div className="w-full max-w-[600px] mx-auto mt-8">
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
                </>
              )}

              {queryThread.map((item, index) => (
                <div key={item.id} className="mb-8">
                  <div className="mb-2 flex items-center gap-2">
                    <div className="text-sm text-white/60">
                      {item.isFollowUp ? 'Follow-up Query:' : 'Initial Query:'}
                    </div>
                    <div className="text-sm font-medium">{item.query}</div>
                  </div>
                  <QueryResults results={item.result} />
                  <ActionToolbar
                    onShare={() => {
                      navigator.clipboard.writeText(item.query)
                    }}
                    onRewrite={() => {
                      setFollowUpQuery(item.query)
                    }}
                    onLike={() => {
                      console.log('Liked:', item.id)
                    }}
                    onDislike={() => {
                      console.log('Disliked:', item.id)
                    }}
                    onCopy={() => {
                      const resultText = item.result.summary || 'No analysis available'
                      navigator.clipboard.writeText(`${item.query}\n\n${resultText}`)
                    }}
                    onMore={() => {
                      console.log('More options:', item.id)
                    }}
                  />
                  <SuggestionBox 
                    onSuggestionClick={(suggestion) => {
                      // For now, set as follow-up query with the suggestion
                      setFollowUpQuery(`${suggestion}: ${item.query}`)
                    }}
                  />
                </div>
              ))}

              {isLoading && (
                <Card className="w-full bg-[#2C2C2C] border-0 mb-8">
                  <div className="animate-pulse space-y-4 p-4">
                    <div className="h-4 bg-white/10 rounded w-3/4" />
                    <div className="h-4 bg-white/10 rounded w-1/2" />
                    <div className="h-32 bg-white/10 rounded" />
                  </div>
                </Card>
              )}

              {error && (
                <Card className="w-full bg-[#2C2C2C] border-0 p-4 mb-8">
                  <p className="text-red-400">{error}</p>
                </Card>
              )}
            </div>

            {queryThread.length > 0 && (
              <div className="fixed bottom-8 w-full md:w-[800px] left-1/2 -translate-x-1/2 px-4 md:px-0 md:ml-[130px]">
                <div className="bg-[#2C2C2C]/80 backdrop-blur-sm rounded-2xl p-1.5 shadow-lg">
                  <form onSubmit={handleFollowUpSubmit}>
                    <div className="relative flex items-center">
                      <div className="absolute left-4">
                        <div className="flex items-center justify-center w-6 h-6 rounded-full bg-white/5">
                          <Plus className="h-4 w-4 text-white/60" />
                        </div>
                      </div>
                      <Input
                        value={followUpQuery}
                        onChange={(e) => setFollowUpQuery(e.target.value)}
                        placeholder="Ask follow-up..."
                        className="w-full bg-transparent border-0 h-12 pl-14 pr-12 placeholder:text-white/40 focus-visible:ring-0 focus:outline-none text-base"
                        disabled={isSubmittingFollowUp}
                      />
                      <div className="absolute right-2 flex items-center gap-2">
                        <Button 
                          size="icon" 
                          type="submit"
                          disabled={isSubmittingFollowUp || !followUpQuery.trim()}
                          className="bg-white/5 hover:bg-white/10 rounded-lg w-8 h-8 flex items-center justify-center"
                        >
                          <ArrowRight className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </form>
                </div>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}

