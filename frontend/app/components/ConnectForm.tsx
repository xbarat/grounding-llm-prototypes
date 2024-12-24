'use client'

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/components/ui/use-toast';
import { useAuth } from '@/hooks/useAuth';
import { ENDPOINTS, PlatformData } from '@/lib/config';

export function ConnectForm() {
  const [platform, setPlatform] = useState<string>('');
  const [identifier, setIdentifier] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [platforms, setPlatforms] = useState<PlatformData[]>([]);
  const { toast } = useToast();
  const { connect } = useAuth();

  // Fetch available platforms on component mount
  useEffect(() => {
    fetch(ENDPOINTS.PLATFORMS)
      .then(res => res.json())
      .then(data => {
        if (data.status === 'success') {
          setPlatforms(data.data.platforms);
        }
      })
      .catch(error => {
        console.error('Failed to fetch platforms:', error);
        toast({
          title: "Error",
          description: "Failed to load available platforms",
          variant: "destructive",
        });
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
    <form onSubmit={handleSubmit} className="space-y-4 w-full max-w-sm">
      <div className="space-y-2">
        <Label htmlFor="platform">Platform</Label>
        <Select
          value={platform}
          onValueChange={setPlatform}
        >
          <SelectTrigger id="platform">
            <SelectValue placeholder="Select a platform" />
          </SelectTrigger>
          <SelectContent>
            {platforms.map((p) => (
              <SelectItem key={p.id} value={p.id}>
                {p.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <Label htmlFor="identifier">
          {platform === 'typeracer' ? 'Username' : platform === 'f1' ? 'Driver ID' : 'Identifier'}
        </Label>
        <Input
          id="identifier"
          type="text"
          placeholder={getPlaceholder()}
          value={identifier}
          onChange={(e) => setIdentifier(e.target.value)}
          disabled={!platform || isLoading}
        />
      </div>

      <Button 
        type="submit" 
        className="w-full"
        disabled={!platform || !identifier || isLoading}
      >
        {isLoading ? "Connecting..." : "Connect"}
      </Button>
    </form>
  );
} 