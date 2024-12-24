'use client'

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/components/ui/use-toast';
import { useAuth } from '@/hooks/useAuth';
import { ENDPOINTS, PlatformData } from '@/lib/config';
import { Card } from '@/components/ui/card';

// Default platforms in case the API fails
const DEFAULT_PLATFORMS: PlatformData[] = [
  {
    id: 'typeracer',
    name: 'TypeRacer',
    description: 'Competitive typing platform'
  },
  {
    id: 'f1',
    name: 'Formula 1',
    description: 'Formula 1 Racing Statistics'
  }
];

export function ConnectForm() {
  const [platform, setPlatform] = useState<string>('');
  const [identifier, setIdentifier] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [platforms, setPlatforms] = useState<PlatformData[]>(DEFAULT_PLATFORMS);
  const [isLoadingPlatforms, setIsLoadingPlatforms] = useState(true);
  const { toast } = useToast();
  const { connect } = useAuth();

  // Fetch available platforms on component mount
  useEffect(() => {
    console.log('Fetching platforms from:', ENDPOINTS.PLATFORMS);
    setIsLoadingPlatforms(true);
    
    fetch(ENDPOINTS.PLATFORMS)
      .then(res => {
        console.log('Platform response status:', res.status);
        return res.json();
      })
      .then(data => {
        console.log('Platform data:', data);
        if (data.status === 'success' && data.data.platforms) {
          setPlatforms(data.data.platforms);
        } else {
          console.warn('Using default platforms due to invalid API response');
        }
      })
      .catch(error => {
        console.error('Failed to fetch platforms:', error);
        toast({
          title: "Warning",
          description: "Using default platforms list",
          variant: "destructive",
        });
      })
      .finally(() => {
        setIsLoadingPlatforms(false);
      });
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      await connect(platform, identifier);
      toast({
        title: "Success",
        description: `Connected to ${platform} as ${identifier}`,
      });
    } catch (error) {
      console.error('Connection error:', error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to connect",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const getPlaceholder = () => {
    switch (platform) {
      case 'typeracer':
        return 'Enter your TypeRacer username';
      case 'f1':
        return 'Enter driver ID (e.g., max_verstappen)';
      default:
        return 'Select a platform first';
    }
  };

  return (
    <Card className="bg-[#2C2C2C] border-0 p-6">
      <div className="space-y-4">
        <div>
          <h2 className="text-lg font-medium text-white/90 mb-2">Connect to a Platform</h2>
          <p className="text-sm text-white/60">Select a platform and enter your identifier to start analyzing your data.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4" id="connect-form">
          <div className="space-y-2">
            <Label htmlFor="platform-select" className="text-white/90">Choose Platform</Label>
            <div className="relative">
              <Select
                value={platform}
                onValueChange={setPlatform}
                disabled={isLoadingPlatforms}
                name="platform"
              >
                <SelectTrigger 
                  id="platform-select" 
                  className="w-full bg-[#1C1C1C] border border-white/10 text-white h-10 px-3 rounded-md cursor-pointer hover:bg-[#2C2C2C] transition-colors"
                >
                  <SelectValue placeholder={isLoadingPlatforms ? "Loading platforms..." : "Click to select a platform"} />
                </SelectTrigger>
                <SelectContent 
                  className="bg-[#2C2C2C] border border-white/10 text-white rounded-md overflow-hidden"
                  position="popper"
                  sideOffset={5}
                >
                  {platforms.map((p) => (
                    <SelectItem 
                      key={p.id} 
                      value={p.id}
                      className="py-2 px-3 text-white/90 hover:bg-white/10 cursor-pointer transition-colors"
                    >
                      <div className="flex flex-col">
                        <span className="font-medium">{p.name}</span>
                        <span className="text-sm text-white/60">{p.description}</span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {platforms.length === 0 && !isLoadingPlatforms && (
                <p className="text-sm text-red-400 mt-1">No platforms available. Please try refreshing the page.</p>
              )}
            </div>
          </div>

          {platform && (
            <div className="space-y-2">
              <Label htmlFor="identifier-input" className="text-white/90">
                {platform === 'typeracer' ? 'Username' : platform === 'f1' ? 'Driver ID' : 'Identifier'}
              </Label>
              <Input
                id="identifier-input"
                name="identifier"
                type="text"
                placeholder={getPlaceholder()}
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                disabled={!platform || isLoading}
                className="w-full bg-[#1C1C1C] border border-white/10 text-white h-10 px-3 rounded-md placeholder:text-white/40"
                autoComplete={platform === 'typeracer' ? 'username' : 'off'}
              />
            </div>
          )}

          <Button 
            type="submit" 
            className="w-full bg-white/10 hover:bg-white/20 text-white h-10 rounded-md transition-colors"
            disabled={!platform || !identifier || isLoading}
            id="connect-button"
            name="connect-button"
          >
            {isLoading ? "Connecting..." : "Connect"}
          </Button>
        </form>

        {platform && (
          <div className="text-sm text-white/60 pt-4 border-t border-white/10">
            <h3 className="font-medium text-white/90 mb-2">Example Identifiers:</h3>
            {platform === 'typeracer' ? (
              <p>Your TypeRacer username (e.g., "speedracer")</p>
            ) : platform === 'f1' ? (
              <div className="space-y-1">
                <p>- max_verstappen (Max Verstappen)</p>
                <p>- lewis_hamilton (Lewis Hamilton)</p>
                <p>- charles_leclerc (Charles Leclerc)</p>
              </div>
            ) : null}
          </div>
        )}
      </div>
    </Card>
  );
} 