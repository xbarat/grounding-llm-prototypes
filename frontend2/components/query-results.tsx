'use client'

import { useState } from 'react'
import { ChevronDown, ChevronUp, Table } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import Image from 'next/image'
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible'
import { type AnalysisResult } from '@/lib/config'

interface QueryResultsProps {
  results: AnalysisResult
}

export function QueryResults({ results }: QueryResultsProps) {
  const [isDataOpen, setIsDataOpen] = useState(false)

  return (
    <Card className="w-full max-w-[800px] bg-card border-border">
      <div className="p-6 space-y-6">
        {results.summary && (
          <div className="prose dark:prose-invert max-w-none">
            <p className="text-lg text-foreground">{results.summary}</p>
          </div>
        )}

        {results.visualization && (
          <div>
            <h3 className="text-lg font-semibold mb-4 text-foreground">Visualization</h3>
            <div className="relative w-full h-[500px] bg-muted rounded-lg overflow-hidden">
              <Image
                src={`data:image/png;base64,${results.visualization}`}
                alt="F1 Analysis Visualization"
                fill
                style={{ objectFit: 'contain' }}
                priority
              />
            </div>
          </div>
        )}

        {results.data && (
          <Collapsible open={isDataOpen} onOpenChange={setIsDataOpen}>
            <CollapsibleTrigger asChild>
              <Button variant="outline" className="w-full justify-between">
                <div className="flex items-center gap-2">
                  <Table className="h-4 w-4" />
                  View Data
                </div>
                {isDataOpen ? (
                  <ChevronUp className="h-4 w-4" />
                ) : (
                  <ChevronDown className="h-4 w-4" />
                )}
              </Button>
            </CollapsibleTrigger>
            <CollapsibleContent className="mt-4">
              <div className="bg-muted p-4 rounded-lg overflow-x-auto">
                <pre className="text-sm text-muted-foreground">
                  <code>{JSON.stringify(results.data, null, 2)}</code>
                </pre>
              </div>
            </CollapsibleContent>
          </Collapsible>
        )}

        {results.rawData && (
          <div className="text-xs text-muted-foreground">
            <p>Raw data available for download</p>
          </div>
        )}
      </div>
    </Card>
  )
}

