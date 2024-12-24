'use client'

import { ConnectForm } from "./ConnectForm";
import { useAuth } from "@/hooks/useAuth";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { LogOut } from "lucide-react";

export function Sidebar() {
  const { user, disconnect } = useAuth();

  return (
    <div className="w-[350px] border-r bg-[#1C1C1C] border-[#2C2C2C] p-6">
      <div className="flex flex-col h-full">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-xl font-semibold text-white/90">GIRAFFE</h1>
          {user && (
            <Button
              variant="ghost"
              size="icon"
              onClick={disconnect}
              className="text-white/60 hover:text-white"
            >
              <LogOut className="h-4 w-4" />
            </Button>
          )}
        </div>

        {user ? (
          <Card className="bg-[#2C2C2C] border-0 p-4">
            <div className="space-y-2">
              <h2 className="text-sm font-medium text-white/90">Connected as</h2>
              <div className="text-sm text-white/60">
                {user.platform === 'typeracer' ? (
                  <>
                    <p>Username: {user.identifier}</p>
                    {user.data?.typeracer && (
                      <>
                        <p>Average Speed: {user.data.typeracer.avgSpeed} WPM</p>
                        <p>Best Speed: {user.data.typeracer.bestSpeed} WPM</p>
                        <p>Games Played: {user.data.typeracer.gamesPlayed}</p>
                      </>
                    )}
                  </>
                ) : user.platform === 'f1' ? (
                  <>
                    <p>Driver: {user.identifier}</p>
                    {user.data?.f1 && (
                      <>
                        <p>Name: {user.data.f1.givenName} {user.data.f1.familyName}</p>
                        <p>Team: {user.data.f1.Constructor.name}</p>
                        <p>Position: {user.data.f1.position}</p>
                        <p>Points: {user.data.f1.points}</p>
                        <p>Wins: {user.data.f1.wins}</p>
                      </>
                    )}
                  </>
                ) : null}
              </div>
            </div>
          </Card>
        ) : (
          <div className="flex-1">
            <ConnectForm />
          </div>
        )}
      </div>
    </div>
  );
} 