# Backend Server Test

## Quick Start

Open two separate terminals:

### Terminal 1 - Start Backend:
```bash
cd /home/zeroql/webdev/souqpilot/backend
python3 server.py
```

You should see:
```
✓ Flight search tools initialized successfully
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Terminal 2 - Start Frontend:
```bash
cd /home/zeroql/webdev/souqpilot/frontend
npm run dev
```

You should see:
```
VITE ready in XXX ms
Local: http://localhost:3000/
```

## Test the Backend API

With the backend running, test it:

```bash
# Test health endpoint
curl http://localhost:8000/

# Test flight search
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me flights from Dubai to Chennai on January 15, 2026 for 1 adult in economy"}'
```

## Troubleshooting

### Error: "Address already in use"
Kill existing process:
```bash
lsof -ti:8000 | xargs kill -9
```

### Error: "Failed to search flights"
1. Make sure backend is running (check Terminal 1)
2. Check backend logs for errors
3. Verify you have a .env file with API keys in the root directory
4. Make sure frontend is connecting to http://localhost:8000

### Frontend not loading
```bash
cd /home/zeroql/webdev/souqpilot/frontend
rm -rf node_modules
npm install
npm run dev
```

## Key Changes Made

The backend has been simplified to work **without requiring a full LangChain agent setup**. Instead:

1. **Direct Tool Usage**: Uses `FlightSearchTool` directly instead of the agent
2. **Query Parsing**: Parses natural language queries using regex patterns
3. **Airport Code Lookup**: Built-in airport code mapping
4. **Simple API**: Clean REST endpoints for search and booking

The frontend connects via standard HTTP requests to these endpoints.
