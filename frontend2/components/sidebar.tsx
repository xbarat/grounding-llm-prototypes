'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet'
import { Menu, Home, Activity, BarChart, History, X, Compass, Layers, Library, Plus, Download, Trophy } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import { ENDPOINTS, type UserStats, type ApiResponse, type AnalysisResult } from '@/lib/config'

interface HistoryItem {
  id: string;
  title: string;
  thread: any[];
  timestamp: string;
}

interface SidebarProps {
  className?: string;
  onHistoryItemClick?: (thread: any[]) => void;
}

const navItems: NavItem[] = [
  { icon: Home, label: 'Home', href: '/' },
  { icon: Activity, label: 'Analysis', href: '/analysis' },
  { icon: Trophy, label: 'Stats', href: '/stats' },
  { icon: Library, label: 'History', href: '/history' },
]

export function Sidebar({ className, onHistoryItemClick }: SidebarProps) {
  const [username, setUsername] = useState('')
  const [isConnected, setIsConnected] = useState(false)
  const [isConnecting, setIsConnecting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [userStats, setUserStats] = useState<UserStats | null>(null)
  const [history, setHistory] = useState<HistoryItem[]>([])
  const [isOpen, setIsOpen] = useState(false)

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

  const SidebarContent = () => (
    <div className="flex flex-col h-full">
      <div className="p-4">
        <Button
          variant="outline"
          className="w-full justify-start gap-2 text-white/60 hover:text-white"
          onClick={() => window.location.href = '/'}
        >
          <Home className="h-4 w-4" />
          New Analysis
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        {isConnected && Object.entries(groupHistoryByDate()).map(([date, items]) => (
          <div key={date} className="mb-6">
            <h3 className="text-sm font-medium text-white/60 mb-2">{date}</h3>
            <div className="space-y-2">
              {items.map((item) => (
                <Button
                  key={item.id}
                  variant="ghost"
                  className="w-full justify-start text-left text-sm text-white/60 hover:text-white truncate"
                  onClick={() => {
                    onHistoryItemClick?.(item.thread)
                    setIsOpen(false)
                  }}
                >
                  {item.title}
                </Button>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="p-4 border-t border-white/10">
        <div className="text-sm font-medium mb-2">Connection Status</div>
        {isConnected ? (
          <div className="space-y-2">
            <div className="text-sm text-white/60">Connected as {username}</div>
            <Button
              variant="ghost"
              className="w-full justify-center text-white/60 hover:text-white"
              onClick={handleDisconnect}
            >
              Disconnect
            </Button>
          </div>
        ) : (
          <div className="space-y-2">
            <Input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter username"
              className="bg-[#2C2C2C] border-0"
            />
            <Button
              variant="outline"
              className="w-full"
              onClick={handleConnect}
              disabled={!username.trim()}
            >
              Connect
            </Button>
          </div>
        )}
      </div>
    </div>
  )

  // Desktop sidebar
  const DesktopSidebar = () => (
    <div className="hidden md:block w-[260px] bg-[#1C1C1C] border-r border-white/10">
      <SidebarContent />
    </div>
  )

  // Mobile sidebar
  const MobileSidebar = () => (
    <div className="md:hidden">
      <Sheet open={isOpen} onOpenChange={setIsOpen}>
        <SheetTrigger asChild>
          <Button variant="ghost" size="icon" className="md:hidden fixed top-4 left-4 z-50">
            <Menu className="h-6 w-6" />
          </Button>
        </SheetTrigger>
        <SheetContent side="left" className="w-[80%] max-w-[300px] p-0 bg-[#1C1C1C] border-r border-white/10">
          <SidebarContent />
        </SheetContent>
      </Sheet>
    </div>
  )

  return (
    <>
      <DesktopSidebar />
      <MobileSidebar />
    </>
  )
}

