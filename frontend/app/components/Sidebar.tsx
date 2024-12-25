'use client'

import { useState, useEffect } from "react";
import { useAuth, usePlatformData } from "@/hooks/useAuth";
import { ConnectForm } from "./ConnectForm";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useToast } from "@/components/ui/use-toast";

export function Sidebar() {
  const { user, disconnect } = useAuth();
  const { platform, identifier, data, fetchPlatformData } = usePlatformData();
  const { toast } = useToast();
  const [exampleQueries, setExampleQueries] = useState<string[]>([]);

  useEffect(() => {
    const fetchQueries = async () => {
      if (!platform) return;
      try {
        const response = await fetch(`/api/v1/platforms/${platform}/queries`);
        if (!response.ok) {
          throw new Error("Failed to fetch example queries");
        }
        const queries = await response.json();
        setExampleQueries(queries);
      } catch (error) {
        console.error("Error fetching queries:", error);
      }
    };

    fetchQueries();
  }, [platform]);

  const renderUserInfo = () => {
    if (!user) return null;

    if (platform === "typeracer") {
      return (
        <div className="space-y-2">
          <h3 className="text-lg font-medium">TypeRacer Stats</h3>
          <p>Username: {identifier}</p>
          <p>Races: {data?.races || 0}</p>
          <p>Average Speed: {data?.average_speed?.toFixed(2) || 0} WPM</p>
          <p>Best Speed: {data?.best_speed?.toFixed(2) || 0} WPM</p>
        </div>
      );
    }

    if (platform === "f1") {
      return (
        <div className="space-y-2">
          <h3 className="text-lg font-medium">F1 Driver Stats</h3>
          <p>Driver: {data?.Driver?.givenName} {data?.Driver?.familyName}</p>
          <p>Team: {data?.Constructor?.name}</p>
          <p>Points: {data?.points || 0}</p>
          <p>Position: {data?.position || "N/A"}</p>
        </div>
      );
    }

    return null;
  };

  const handleDisconnect = () => {
    disconnect();
    toast({
      title: "Disconnected",
      description: "Successfully disconnected from the platform",
    });
  };

  return (
    <aside className="w-80 bg-[#1C1C1C] border-r border-white/10 h-screen p-4 flex flex-col">
      <div className="flex-1 space-y-4">
        {user ? (
          <>
            <Card className="bg-[#2C2C2C] border-0 p-6">
              {renderUserInfo()}
              <Button
                onClick={handleDisconnect}
                variant="destructive"
                className="w-full mt-4"
              >
                Disconnect
              </Button>
            </Card>

            <Card className="bg-[#2C2C2C] border-0 p-6">
              <h3 className="text-lg font-medium mb-4">Example Queries</h3>
              <ul className="space-y-2">
                {exampleQueries.map((query, index) => (
                  <li
                    key={index}
                    className="text-sm text-white/80 hover:text-white cursor-pointer transition-colors"
                    onClick={() => {
                      // Copy query to clipboard
                      navigator.clipboard.writeText(query);
                      toast({
                        title: "Query Copied",
                        description: "Example query copied to clipboard",
                      });
                    }}
                  >
                    {query}
                  </li>
                ))}
              </ul>
            </Card>
          </>
        ) : (
          <Card className="rounded-xl text-card-foreground shadow w-full max-w-[600px] bg-[#2C2C2C] border-0 p-8 text-center">
            <p className="text-lg text-white/90 mb-4">Connect to a platform to start analyzing your data</p>
            <ConnectForm />
          </Card>
        )}
      </div>
    </aside>
  );
} 