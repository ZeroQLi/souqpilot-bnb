# SouqPilot - Flight Search with Web3

A modern flight search application powered by AI agents and blockchain technology. Search for flights using natural language and book with cryptocurrency through MetaMask.

## Features

- 🤖 **AI-Powered Search**: Natural language flight search using LangChain agents
- 🦊 **MetaMask Integration**: Connect your wallet and pay with crypto
- ✈️ **Real-time Flight Data**: Search flights using the fast-flights library
- 💳 **Smart Contract Payments**: Secure blockchain-based booking system
- 🎨 **Modern UI**: Beautiful, responsive React interface

## Project Structure

```
souqpilot/
├── backend/
│   ├── server.py          # FastAPI server
│   └── requirements.txt   # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── contracts/     # Smart contract ABIs
│   │   ├── App.jsx        # Main app component
│   │   └── main.jsx       # Entry point
│   ├── package.json       # Node dependencies
│   └── vite.config.js     # Vite configuration
├── contracts/
│   └── FlightBooking.sol  # Solidity smart contract
├── work.py                # Original flight agent script
└── flight_search_tool.py  # Flight search tool implementation
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 16+
- MetaMask browser extension
- OpenAI API key (or other LLM provider)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your API keys:
```env
OPENAI_API_KEY=your_openai_api_key_here
# Or use other LLM providers
```

5. Start the backend server:
```bash
python server.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Smart Contract Deployment (Optional)

To deploy the FlightBooking smart contract:

1. Install Hardhat or Truffle
2. Deploy to your preferred network (testnet recommended for development)
3. Update the contract address in `frontend/src/contracts/FlightBooking.js`

## Usage

1. **Connect MetaMask**: Click the "Connect MetaMask" button in the header
2. **Search Flights**: Enter a natural language query like:
   - "Show me flights from Dubai to Chennai on January 15, 2026"
   - "Find business class flights from London to New York"
   - "I need a round-trip ticket from Paris to Tokyo"
3. **View Results**: The AI agent will process your query and display available flights
4. **Book with Crypto**: Click "Book with Crypto" to pay using your connected wallet

## API Endpoints

### GET `/`
Health check endpoint

### POST `/api/search`
Search for flights using natural language

**Request Body:**
```json
{
  "query": "Show me flights from Dubai to Chennai",
  "wallet_address": "0x..."
}
```

### POST `/api/book`
Book a flight with crypto payment

**Request Body:**
```json
{
  "flight_id": "FLIGHT-001",
  "wallet_address": "0x...",
  "transaction_hash": "0x...",
  "amount": "0.01"
}
```

### GET `/api/bookings/{wallet_address}`
Get all bookings for a wallet address

## Technologies Used

### Backend
- FastAPI - Modern Python web framework
- LangChain - AI agent framework
- fast-flights - Flight search library
- Pydantic - Data validation

### Frontend
- React - UI framework
- Vite - Build tool
- ethers.js - Ethereum library
- Axios - HTTP client

### Blockchain
- Solidity - Smart contract language
- Ethereum - Blockchain platform
- MetaMask - Wallet integration

## Development

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Building for Production
```bash
# Frontend build
cd frontend
npm run build
```

## Environment Variables

Create a `.env` file in the root directory:

```env
# LLM Provider (choose one)
OPENAI_API_KEY=your_key_here
# ANTHROPIC_API_KEY=your_key_here
# GOOGLE_API_KEY=your_key_here

# Optional: Custom API endpoints
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
```

## Security Notes

- Never commit your `.env` file
- Use testnet for development
- Verify smart contract code before mainnet deployment
- Implement proper authentication for production
- Add rate limiting to API endpoints

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a pull request

## License

MIT License - feel free to use this project for learning and development.

## Support

For issues and questions, please open a GitHub issue.

## Roadmap

- [ ] Add user authentication
- [ ] Implement booking history
- [ ] Add more payment options (USDC, USDT)
- [ ] Multi-chain support
- [ ] Email notifications
- [ ] Price alerts
- [ ] Mobile app

---

Built with ❤️ using AI, Blockchain, and Modern Web Technologies
