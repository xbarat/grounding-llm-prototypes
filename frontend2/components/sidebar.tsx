'use client'

import { useState } from 'react'
import { Home, Compass, Layers, Library, Plus, Download, Trophy, Activity } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import { ENDPOINTS, type UserStats, type ApiResponse, type AnalysisResult } from '@/lib/config'

interface NavItem {
  icon: React.ComponentType
  label: string
  href: string
}

interface SidebarProps {
  currentResults?: AnalysisResult | null;
  onFollowUpQuery?: (query: string) => void;
}

const navItems: NavItem[] = [
  { icon: Home, label: 'Home', href: '/' },
  { icon: Activity, label: 'Analysis', href: '/analysis' },
  { icon: Trophy, label: 'Stats', href: '/stats' },
  { icon: Library, label: 'History', href: '/history' },
]

export function Sidebar({ currentResults, onFollowUpQuery }: SidebarProps) {
  const [username, setUsername] = useState('')
  const [isConnected, setIsConnected] = useState(false)
  const [isConnecting, setIsConnecting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [userStats, setUserStats] = useState<UserStats | null>(null)
  const [followUpQuery, setFollowUpQuery] = useState('')
  const [isSubmittingFollowUp, setIsSubmittingFollowUp] = useState(false)

  const handleConnect = async () => {
    if (!username) return
    
    setIsConnecting(true)
    setError(null)
    
    try {
      // First, connect user
      console.log('Connecting user...')
      const response = await fetch(ENDPOINTS.CONNECT_USER, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username }),
      })

      const data: ApiResponse<UserStats> = await response.json()
      console.log('Connect response:', data)

      if (data.status === 'success' && data.data) {
        setIsConnected(true)
        setUserStats(data.data)

        // Then fetch initial data
        console.log('Fetching initial data...')
        console.log('User stats data:', data.data)
        const playerId = data.data.id.startsWith('tr:') ? data.data.id : `tr:${data.data.id}`
        const requestBody = {
          player_id: playerId,
          universe: 'play',
          n: 100,
          before_id: data.data.tstats.cg.toString()
        }
        console.log('Fetch request body:', requestBody)
        console.log('Fetch URL:', ENDPOINTS.FETCH_DATA)
        
        const fetchResponse = await fetch(ENDPOINTS.FETCH_DATA, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestBody),
        })

        console.log('Fetch response status:', fetchResponse.status)
        const fetchResponseText = await fetchResponse.text()
        console.log('Fetch response text:', fetchResponseText)
        
        let fetchData: ApiResponse
        try {
          fetchData = JSON.parse(fetchResponseText)
          console.log('Parsed fetch response:', fetchData)
        } catch (err) {
          console.error('Failed to parse fetch response:', err)
          setError('Failed to parse server response')
          return
        }
        
        if (fetchData.status !== 'success') {
          console.error('Fetch data failed:', fetchData)
          // Don't disconnect user if fetch fails, just show a warning
          setError('Connected, but failed to fetch race data')
          return
        }
      } else {
        throw new Error(data.detail || 'Failed to connect')
      }
    } catch (err) {
      console.error('Connection error:', err)
      setError(err instanceof Error ? err.message : 'An error occurred')
      setIsConnected(false)
      setUserStats(null)
    } finally {
      setIsConnecting(false)
    }
  }

  return (
    <div className="w-64 border-r bg-background p-4 flex flex-col h-full">
      <div className="flex items-center gap-2 mb-8">
        <Button variant="outline" className="w-full justify-start gap-2">
          <Plus className="h-4 w-4" /> New Analysis
        </Button>
      </div>

      <nav className="space-y-2 mb-8">
        {navItems.map((item) => (
          <Button
            key={item.href}
            variant="ghost"
            className="w-full justify-start gap-2"
            asChild
          >
            <a href={item.href}>
              <item.icon className="h-4 w-4" />
              {item.label}
            </a>
          </Button>
        ))}
      </nav>

      <div className="mt-auto space-y-4">
        {currentResults && (
          <div className="space-y-2 mb-4 p-3 border rounded-lg">
            <div className="text-sm font-medium">Follow-up Question</div>
            <div className="space-y-2">
              <Input
                placeholder="Ask a follow-up question..."
                value={followUpQuery}
                onChange={(e) => setFollowUpQuery(e.target.value)}
                disabled={isSubmittingFollowUp}
              />
              <Button 
                className="w-full"
                onClick={() => {
                  if (followUpQuery.trim() && onFollowUpQuery) {
                    setIsSubmittingFollowUp(true);
                    onFollowUpQuery(followUpQuery);
                    setFollowUpQuery('');
                    setIsSubmittingFollowUp(false);
                  }
                }}
                disabled={!followUpQuery.trim() || isSubmittingFollowUp}
              >
                {isSubmittingFollowUp ? 'Processing...' : 'Ask Follow-up'}
              </Button>
            </div>
          </div>
        )}

        <div className="space-y-2">
          <div className="text-sm font-medium">Connection Status</div>
          <Badge variant={isConnected ? "success" : "secondary"} className="w-full justify-center">
            {isConnected ? 'Connected' : 'Disconnected'}
          </Badge>
        </div>

        <div className="space-y-2">
          <Input
            placeholder="Enter username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            disabled={isConnected}
          />
          {error && (
            <div className="text-sm text-red-500">
              {error}
            </div>
          )}
          <Button 
            className="w-full"
            onClick={handleConnect}
            disabled={!username || isConnecting}
          >
            {isConnecting ? 'Connecting...' : isConnected ? 'Connected' : 'Connect'}
          </Button>
        </div>

        {isConnected && userStats && (
          <div className="p-3 border rounded-lg space-y-2">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white">
                {userStats.name.slice(0, 2).toUpperCase()}
              </div>
              <div>
                <div className="text-sm font-medium">{userStats.name}</div>
                <div className="text-xs text-muted-foreground">{userStats.tstats.level}</div>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>
                <div className="text-muted-foreground">WPM</div>
                <div className="font-medium">{userStats.tstats.wpm.toFixed(1)}</div>
              </div>
              <div>
                <div className="text-muted-foreground">Best</div>
                <div className="font-medium">{userStats.tstats.bestGameWpm.toFixed(1)}</div>
              </div>
              <div>
                <div className="text-muted-foreground">Games</div>
                <div className="font-medium">{userStats.tstats.cg}</div>
              </div>
              <div>
                <div className="text-muted-foreground">Won</div>
                <div className="font-medium">{userStats.tstats.gamesWon}</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

