import React, { useState } from 'react';
import axios from 'axios';
import { ethers } from 'ethers';
import './FlightSearch.css';

const API_BASE_URL = 'http://localhost:8000';

function FlightSearch({ walletAddress, signer }) {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');
  const [bookingInProgress, setBookingInProgress] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    
    if (!query.trim()) {
      setError('Please enter a search query');
      return;
    }

    setLoading(true);
    setError('');
    setResults(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/search`, {
        query: query,
        wallet_address: walletAddress || null
      });

      if (response.data.success) {
        setResults(response.data.data);
      } else {
        setError('Search failed. Please try again.');
      }
    } catch (err) {
      console.error('Search error:', err);
      setError(err.response?.data?.detail || 'Failed to search flights. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleBooking = async (flightId, price) => {
    if (!walletAddress) {
      alert('Please connect your wallet first');
      return;
    }

    if (!signer) {
      alert('Wallet signer not available');
      return;
    }

    setBookingInProgress(true);

    try {
      // In a real application, you would:
      // 1. Get the payment address from your smart contract
      // 2. Send the payment transaction
      // 3. Wait for confirmation
      // 4. Submit booking to backend

      // For demo purposes, we'll simulate a payment
      const paymentAddress = '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb'; // Example address
      const amountInEth = '0.01'; // Demo amount

      // Send transaction
      const tx = await signer.sendTransaction({
        to: paymentAddress,
        value: ethers.parseEther(amountInEth)
      });

      alert('Transaction sent! Waiting for confirmation...');

      // Wait for transaction to be mined
      const receipt = await tx.wait();

      // Submit booking to backend
      const bookingResponse = await axios.post(`${API_BASE_URL}/api/book`, {
        flight_id: flightId,
        wallet_address: walletAddress,
        transaction_hash: receipt.hash,
        amount: amountInEth
      });

      if (bookingResponse.data.success) {
        alert(`Booking confirmed! Booking ID: ${bookingResponse.data.booking_id}`);
      }

    } catch (err) {
      console.error('Booking error:', err);
      alert('Booking failed: ' + (err.message || 'Unknown error'));
    } finally {
      setBookingInProgress(false);
    }
  };

  return (
    <div className="flight-search-container">
      <div className="search-card">
        <h2>Search Flights</h2>
        <p className="search-description">
          Use natural language to search for flights. Example: "Show me flights from Dubai to Chennai on January 15, 2026"
        </p>

        <form onSubmit={handleSearch} className="search-form">
          <div className="input-group">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Where would you like to fly?"
              className="search-input"
              disabled={loading}
            />
            <button 
              type="submit" 
              className="search-button"
              disabled={loading}
            >
              {loading ? '🔍 Searching...' : '✈️ Search Flights'}
            </button>
          </div>
        </form>

        {error && (
          <div className="error-message">
            ⚠️ {error}
          </div>
        )}

        {results && (
          <div className="results-container">
            <h3>Search Results</h3>
            <div className="query-display">
              <strong>Your Query:</strong> {results.query}
            </div>
            
            <div className="results-content">
              <pre>{results.results}</pre>
            </div>

            {walletAddress && (
              <div className="booking-section">
                <button 
                  className="book-button"
                  onClick={() => handleBooking('DEMO-FLIGHT-001', '0.01')}
                  disabled={bookingInProgress}
                >
                  {bookingInProgress ? '⏳ Processing...' : '💳 Book with Crypto'}
                </button>
                <p className="booking-note">
                  Demo booking: 0.01 ETH
                </p>
              </div>
            )}

            {!walletAddress && (
              <div className="connect-prompt">
                Connect your wallet to book flights with crypto
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default FlightSearch;
