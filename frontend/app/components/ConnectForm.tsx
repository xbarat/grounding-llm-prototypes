'use client'

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/components/ui/use-toast';
import { useAuth } from '@/hooks/useAuth';

interface Platform {
  id: string;
  name: string;
  description: string;
  identifier_type: string;
  example_identifier: string;
}

export function ConnectForm() {
  const { connect } = useAuth();
  const { toast } = useToast();
  const [platforms, setPlatforms] = useState<Platform[]>([]);
  const [selectedPlatform, setSelectedPlatform] = useState<string>("");
  const [identifier, setIdentifier] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);

  useEffect(() => {
    const fetchPlatforms = async () => {
      try {
        const response = await fetch("/api/v1/platforms");
        if (!response.ok) {
          throw new Error("Failed to fetch platforms");
        }
        const data = await response.json();
        setPlatforms(data);
      } catch (error) {
        console.error("Error fetching platforms:", error);
        toast({
          title: "Error",
          description: "Failed to fetch available platforms",
          variant: "destructive",
        });
      }
    };

    fetchPlatforms();
  }, [toast]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedPlatform || !identifier) {
      toast({
        title: "Error",
        description: "Please select a platform and enter an identifier",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    try {
      await connect(selectedPlatform, identifier);
      toast({
        title: "Success",
        description: `Connected to ${selectedPlatform} successfully`,
      });
    } catch (error) {
      console.error("Connection error:", error);
      toast({
        title: "Error",
        description: "Failed to connect. Please check your identifier and try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const getPlaceholder = () => {
    const platform = platforms.find(p => p.id === selectedPlatform);
    return platform ? platform.example_identifier : "Enter your identifier";
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="platform">Platform</Label>
        <Select
          value={selectedPlatform}
          onValueChange={setSelectedPlatform}
        >
          <SelectTrigger id="platform">
            <SelectValue placeholder="Select a platform" />
          </SelectTrigger>
          <SelectContent>
            {platforms.map((platform) => (
              <SelectItem key={platform.id} value={platform.id}>
                {platform.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {selectedPlatform && (
        <div className="space-y-2">
          <Label htmlFor="identifier">
            {platforms.find(p => p.id === selectedPlatform)?.identifier_type}
          </Label>
          <Input
            id="identifier"
            type="text"
            value={identifier}
            onChange={(e) => setIdentifier(e.target.value)}
            placeholder={getPlaceholder()}
            disabled={isLoading}
          />
        </div>
      )}

      <Button
        type="submit"
        disabled={!selectedPlatform || !identifier || isLoading}
        className="w-full"
      >
        {isLoading ? "Connecting..." : "Connect"}
      </Button>
    </form>
  );
} 