'use client'

import { useState } from 'react'
import { Home, Compass, Layers, Library, Plus, Download } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import { ENDPOINTS, type UserStats, type ApiResponse } from '@/lib/config'

interface NavItem {
  icon: React.ComponentType
  label: string
  href: string
}

const navItems: NavItem[] = [
  { icon: Home, label: 'Home', href: '/' },
  { icon: Compass, label: 'Chat History', href: '/discover' },
  { icon: Layers, label: 'Templates', href: '/spaces' },
  { icon: Library, label: 'Discover', href: '/library' },
]

export function Sidebar() {
  const [username, setUsername] = useState('')
  const [isConnected, setIsConnected] = useState(false)
  const [isConnecting, setIsConnecting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [userStats, setUserStats] = useState<UserStats | null>(null)

  const handleConnect = async () => {
    if (!username) return
    
    setIsConnecting(true)
    setError(null)
    
    try {
      const response = await fetch(ENDPOINTS.CONNECT_USER, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username }),
      })

      const data: ApiResponse<UserStats> = await response.json()

      if (data.status === 'success' && data.data) {
        setIsConnected(true)
        setUserStats({
          username,
          ...data.data
        })

        // After successful connection, fetch initial data
        const fetchResponse = await fetch(ENDPOINTS.FETCH_DATA, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            player_id: `tr:${username}`,
            universe: 'play',
            n: 100
          }),
        })

        const fetchData: ApiResponse = await fetchResponse.json()
        if (fetchData.status !== 'success') {
          throw new Error('Failed to fetch initial data')
        }
      } else {
        throw new Error(data.detail || 'Failed to connect')
      }
    } catch (err) {
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
          <Plus className="h-4 w-4" /> New User
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
            disabled={!username || isConnected || isConnecting}
          >
            {isConnecting ? 'Connecting...' : isConnected ? 'Connected' : 'Connect'}
          </Button>
        </div>

        {isConnected && userStats && (
          <div className="p-3 border rounded-lg">
            <div className="text-sm font-medium">Connected as:</div>
            <div className="text-sm">{userStats.username}</div>
          </div>
        )}

        <Button variant="outline" className="w-full justify-start gap-2">
          <Download className="h-4 w-4" />
          Download
        </Button>
      </div>
    </div>
  )
}

