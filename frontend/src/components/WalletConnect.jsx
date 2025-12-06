import React from 'react';
import './WalletConnect.css';

function WalletConnect({ walletAddress, connectWallet, disconnectWallet }) {
  const formatAddress = (address) => {
    return `${address.substring(0, 6)}...${address.substring(address.length - 4)}`;
  };

  return (
    <div className="wallet-connect">
      {!walletAddress ? (
        <button className="connect-button" onClick={connectWallet}>
          🦊 Connect MetaMask
        </button>
      ) : (
        <div className="wallet-info">
          <div className="wallet-address">
            <span className="address-label">Connected:</span>
            <span className="address-value">{formatAddress(walletAddress)}</span>
          </div>
          <button className="disconnect-button" onClick={disconnectWallet}>
            Disconnect
          </button>
        </div>
      )}
    </div>
  );
}

export default WalletConnect;
