// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title BNBTransfer
 * @dev Smart contract for transferring BNB on BNB Smart Chain
 */
contract BNBTransfer {
    // Event emitted when a transfer occurs
    event Transfer(
        address indexed from,
        address indexed to,
        uint256 amount,
        uint256 timestamp
    );

    /**
     * @dev Transfer BNB to a specified address
     * @param _to The address to transfer BNB to
     */
    function transferBNB(address payable _to) 
        public 
        payable 
    {
        require(msg.value > 0, "Amount must be greater than 0");
        require(_to != address(0), "Invalid recipient address");
        require(_to != msg.sender, "Cannot transfer to yourself");
        
        // Transfer BNB to the recipient
        (bool success, ) = _to.call{value: msg.value}("");
        require(success, "Transfer failed");
        
        // Emit transfer event
        emit Transfer(msg.sender, _to, msg.value, block.timestamp);
    }

    /**
     * @dev Get the contract's BNB balance
     * @return The balance in wei
     */
    function getBalance() public view returns (uint256) {
        return address(this).balance;
    }

    /**
     * @dev Get the balance of a specific address
     * @param _address The address to check
     * @return The balance in wei
     */
    function getAddressBalance(address _address) public view returns (uint256) {
        return _address.balance;
    }

    /**
     * @dev Fallback function to receive BNB
     */
    receive() external payable {
        emit Transfer(msg.sender, address(this), msg.value, block.timestamp);
    }

    /**
     * @dev Fallback function
     */
    fallback() external payable {
        emit Transfer(msg.sender, address(this), msg.value, block.timestamp);
    }
}
