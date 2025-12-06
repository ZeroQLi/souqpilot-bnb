import React, { useState, useEffect } from 'react';
import { ethers } from 'ethers';
import FlightSearch from './components/FlightSearch';
import WalletConnect from './components/WalletConnect';
import './App.css';

function App() {
  const [walletAddress, setWalletAddress] = useState('');
  const [provider, setProvider] = useState(null);
  const [signer, setSigner] = useState(null);

  useEffect(() => {
    // Check if wallet was previously connected
    const checkWalletConnection = async () => {
      if (window.ethereum) {
        try {
          const accounts = await window.ethereum.request({ 
            method: 'eth_accounts' 
          });
          if (accounts.length > 0) {
            connectWallet();
          }
        } catch (error) {
          console.error('Error checking wallet connection:', error);
        }
      }
    };

    checkWalletConnection();
  }, []);

  const connectWallet = async () => {
    if (typeof window.ethereum !== 'undefined') {
      try {
        // Request account access
        await window.ethereum.request({ method: 'eth_requestAccounts' });
        
        // Create provider and signer
        const web3Provider = new ethers.BrowserProvider(window.ethereum);
        const web3Signer = await web3Provider.getSigner();
        const address = await web3Signer.getAddress();

        setProvider(web3Provider);
        setSigner(web3Signer);
        setWalletAddress(address);

        // Listen for account changes
        window.ethereum.on('accountsChanged', (accounts) => {
          if (accounts.length > 0) {
            setWalletAddress(accounts[0]);
          } else {
            disconnectWallet();
          }
        });

        // Listen for chain changes
        window.ethereum.on('chainChanged', () => {
          window.location.reload();
        });

      } catch (error) {
        console.error('Error connecting wallet:', error);
        alert('Failed to connect wallet. Please try again.');
      }
    } else {
      alert('MetaMask is not installed. Please install it to use this app.');
      window.open('https://metamask.io/download/', '_blank');
    }
  };

  const disconnectWallet = () => {
    setWalletAddress('');
    setProvider(null);
    setSigner(null);
  };

  return (
    <div className="App">
      <header className="App-header">
        <div className="header-content">
          <h1>✈️ SouqPilot</h1>
          <p className="tagline">Book Flights with Crypto</p>
        </div>
        <WalletConnect 
          walletAddress={walletAddress}
          connectWallet={connectWallet}
          disconnectWallet={disconnectWallet}
        />
      </header>

      <main className="App-main">
        <FlightSearch 
          walletAddress={walletAddress}
          signer={signer}
        />
      </main>

      <footer className="App-footer">
        <p>Powered by AI & Blockchain | SouqPilot © 2025</p>
      </footer>
    </div>
  );
}

export default App;
