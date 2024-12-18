'use client'

import { useState } from 'react'
import { ChevronDown, ChevronUp } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible'

interface QueryResultsProps {
  results: string
}

export function QueryResults({ results }: QueryResultsProps) {
  const [isOpen, setIsOpen] = useState(true)

  return (
    <Card className="p-4">
      <div className="prose dark:prose-invert max-w-none">
        <p>{results}</p>

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
              <code>{`// Sample code
function example() {
  return "Hello, World!"
}`}</code>
            </pre>
          </CollapsibleContent>
        </Collapsible>

        <div className="mt-4">
          <h3 className="text-lg font-semibold mb-2">Visualization</h3>
          <div className="aspect-video bg-muted rounded-lg flex items-center justify-center">
            Chart Placeholder
          </div>
        </div>
      </div>
    </Card>
  )
}

