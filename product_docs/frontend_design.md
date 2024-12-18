# Frontend Design Specification - TypeRacer Analysis Interface

## Design Philosophy
The interface should follow Perplexity's clean, focused design while specializing in TypeRacer data analysis. Key differences from the designer's spec:

1. **Simplified Flow**: Focus on the chat-like interface rather than traditional dashboard layouts
2. **Progressive Disclosure**: Show advanced features contextually rather than overwhelming users with options
3. **Immediate Value**: Provide instant suggestions and results rather than requiring complex configuration

## Core Interface Components

### 1. Main Chat Interface
```typescript
interface ChatInterface {
  // Core Components
  MessageThread: {
    messages: Message[]
    layout: 'focused' | 'split'  // Split when showing visualizations
  }
  
  QueryInput: {
    input: string
    attachments?: File[]
    suggestions: string[]
    mode: 'focus' | 'attach' | 'pro'
  }
  
  MessageTypes: {
    USER_QUERY: 'user'
    SYSTEM_RESPONSE: 'system'
    VISUALIZATION: 'viz'
    CODE: 'code'
    ERROR: 'error'
  }
}
```

### 2. Header Components
```typescript
interface HeaderComponents {
  UserConnection: {
    username: string
    status: 'connected' | 'disconnected'
    lastSync: Date
  }
  
  ThreadControls: {
    newThread: () => void
    focusMode: boolean
    toggleHistory: () => void
  }
}
```

### 3. Sidebar Components
```typescript
interface SidebarComponents {
  HistoryPanel: {
    threads: AnalysisThread[]
    filter: string
    selectedId: string
  }
  
  SuggestionsPanel: {
    categories: Category[]
    suggestions: Question[]
    activeCategory: string
  }
}
```

## User Experience Flow

### 1. Initial State
- Clean interface with prominent query input
- "Ask anything..." placeholder
- Quick suggestion chips for common analyses
- Subtle connection status indicator

### 2. Query Flow
1. User types or selects a query
2. Real-time suggestions appear below input
3. On submit:
   - Query appears as chat message
   - Immediate loading indicator
   - Progressive result display:
     1. Generated code (collapsible)
     2. Execution status
     3. Visualization/results
     4. Follow-up suggestions

### 3. Visualization Integration
- Visualizations expand inline within chat
- Toggle between focused and split views
- Interactive elements for data exploration
- Quick export/share options

## API Integration with Existing Backend

```typescript
// Maintain existing endpoint structure while adding real-time features
interface APIIntegration {
  // Existing Endpoints
  endpoints: {
    connectUser: '/api/v1/connect_user'
    fetchData: '/api/v1/fetch_data'
    loadData: '/api/v1/load_data'
    generateCode: '/api/v1/generate_code'
    executeCode: '/api/v1/execute_code'
    queryGuidance: '/api/v1/query_guidance'
  }
  
  // New Real-time Features
  websocket: {
    connect: () => void
    subscribeToExecution: (queryId: string) => void
    onProgressUpdate: (callback: (progress: number) => void) => void
    onVisualizationUpdate: (callback: (vizData: any) => void) => void
  }
}
```

## Component Architecture

### 1. Core Components
```
src/
  components/
    ChatThread/
      Message.tsx
      CodeBlock.tsx
      Visualization.tsx
      FollowupSuggestions.tsx
    
    QueryInput/
      Input.tsx
      Suggestions.tsx
      ToolbarControls.tsx
    
    Header/
      ConnectionStatus.tsx
      ThreadControls.tsx
    
    Sidebar/
      History.tsx
      Categories.tsx
```

### 2. Hooks and Services
```typescript
// Custom hooks for backend integration
const useAnalysis = () => {
  const executeQuery = async (question: string) => {
    const code = await generateCode(question)
    const stream = await executeCodeWithProgress(code)
    return new VisualizationStream(stream)
  }
  
  return { executeQuery }
}

// Real-time visualization handling
class VisualizationStream {
  onProgress: (progress: number) => void
  onUpdate: (vizData: any) => void
  onComplete: (result: any) => void
}
```

## Design Challenges to Address

1. **Real-time Updates**:
   - Challenge: Designer's spec lacks WebSocket support
   - Solution: Add real-time progress and visualization updates
   - Impact: More engaging user experience

2. **Code Display**:
   - Challenge: Designer focuses on dashboard view
   - Solution: Collapsible, syntax-highlighted code blocks in chat
   - Impact: Maintains power user features without cluttering

3. **State Management**:
   - Challenge: Complex state across components
   - Solution: Use React Context for thread state, Redux for app state
   - Impact: Better performance and maintainability

## Implementation Priorities

### Phase 1: Core Experience
1. Chat interface with query input
2. Basic message thread display
3. Code and visualization rendering
4. Real-time execution updates

### Phase 2: Enhanced Features
1. History and threading
2. Advanced suggestions
3. Visualization interactions
4. Export capabilities

### Phase 3: Polish
1. Animations and transitions
2. Keyboard shortcuts
3. Progressive loading
4. Performance optimizations

## Development Guidelines

### 1. Technology Choices
- Next.js 14 with App Router
- TailwindCSS for styling
- SWR for data fetching
- Framer Motion for animations

### 2. Performance
- Stream large datasets
- Lazy load visualizations
- Cache query results
- Debounce user inputs

### 3. Accessibility
- Keyboard navigation
- Screen reader support
- High contrast mode
- Focus management

## Feedback for Designer's Spec

1. **Simplification Needed**:
   - Remove complex dashboard in favor of chat interface
   - Focus on progressive disclosure of features
   - Streamline the user journey

2. **Real-time Considerations**:
   - Add WebSocket support for live updates
   - Consider server-sent events for progress
   - Implement streaming for large datasets

3. **User Experience**:
   - Adopt chat-like interaction model
   - Provide immediate feedback
   - Maintain context in conversation

4. **Technical Alignment**:
   - Leverage existing backend capabilities
   - Add real-time features gradually
   - Keep code generation visible but unobtrusive
``` 