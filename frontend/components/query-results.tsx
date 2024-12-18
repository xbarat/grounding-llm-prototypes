'use client'

import { useState } from 'react'
import { ChevronDown, ChevronUp } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import Image from 'next/image'
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible'

interface QueryResultsProps {
  results: {
    result?: any;
    figure?: string;
    code?: string;
  }
}

export function QueryResults({ results }: QueryResultsProps) {
  const [isOpen, setIsOpen] = useState(true)

  return (
    <Card className="w-full max-w-[600px] bg-[#2C2C2C] border-0 p-4">
      <div className="prose dark:prose-invert max-w-none">
        {results.result && (
          <pre className="text-sm text-white/80 overflow-auto">
            <code>{JSON.stringify(results.result, null, 2)}</code>
          </pre>
        )}

        {results.code && (
          <Collapsible open={isOpen} onOpenChange={setIsOpen}>
            <CollapsibleTrigger asChild>
              <Button variant="outline" className="w-full justify-between">
                View Code
                {isOpen ? (
                  <ChevronUp className="h-4 w-4" />
                ) : (
                  <ChevronDown className="h-4 w-4" />
                )}
              </Button>
            </CollapsibleTrigger>
            <CollapsibleContent className="mt-4">
              <pre className="bg-muted p-4 rounded-lg overflow-x-auto">
                <code>{results.code}</code>
              </pre>
            </CollapsibleContent>
          </Collapsible>
        )}

        {results.figure && (
          <div className="mt-4">
            <h3 className="text-lg font-semibold mb-2">Visualization</h3>
            <div className="relative w-full h-[400px] bg-[#1C1C1C] rounded-lg overflow-hidden">
              <Image
                src={`data:image/png;base64,${results.figure}`}
                alt="Analysis Result"
                fill
                style={{ objectFit: 'contain' }}
              />
            </div>
          </div>
        )}
      </div>
    </Card>
  )
}

