import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { query } = body

    if (!query) {
      return NextResponse.json(
        { status: 'error', detail: 'No query provided' },
        { status: 400 }
      )
    }

    // Forward the request to the backend
    const backendUrl = process.env.NEXT_PUBLIC_API_URL
    if (!backendUrl) {
      return NextResponse.json(
        { status: 'error', detail: 'Backend URL not configured' },
        { status: 500 }
      )
    }

    const response = await fetch(`${backendUrl}/api/v1/process_query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    })

    if (!response.ok) {
      const error = await response.text()
      return NextResponse.json(
        { status: 'error', detail: `Backend error: ${error}` },
        { status: response.status }
      )
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error processing query:', error)
    return NextResponse.json(
      { status: 'error', detail: 'Internal server error' },
      { status: 500 }
    )
  }
} 