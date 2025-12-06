// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title FlightBooking
 * @dev Smart contract for handling flight booking payments
 */
contract FlightBooking {
    address public owner;
    uint256 public bookingCounter;
    
    struct Booking {
        uint256 bookingId;
        address passenger;
        string flightId;
        uint256 amount;
        uint256 timestamp;
        bool isActive;
    }
    
    mapping(uint256 => Booking) public bookings;
    mapping(address => uint256[]) public passengerBookings;
    
    event BookingCreated(
        uint256 indexed bookingId,
        address indexed passenger,
        string flightId,
        uint256 amount,
        uint256 timestamp
    );
    
    event BookingCancelled(
        uint256 indexed bookingId,
        address indexed passenger,
        uint256 refundAmount
    );
    
    event FundsWithdrawn(
        address indexed owner,
        uint256 amount
    );
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }
    
    constructor() {
        owner = msg.sender;
        bookingCounter = 0;
    }
    
    /**
     * @dev Create a new flight booking
     * @param _flightId The flight identifier
     */
    function createBooking(string memory _flightId) external payable returns (uint256) {
        require(msg.value > 0, "Payment amount must be greater than 0");
        require(bytes(_flightId).length > 0, "Flight ID cannot be empty");
        
        bookingCounter++;
        
        Booking memory newBooking = Booking({
            bookingId: bookingCounter,
            passenger: msg.sender,
            flightId: _flightId,
            amount: msg.value,
            timestamp: block.timestamp,
            isActive: true
        });
        
        bookings[bookingCounter] = newBooking;
        passengerBookings[msg.sender].push(bookingCounter);
        
        emit BookingCreated(
            bookingCounter,
            msg.sender,
            _flightId,
            msg.value,
            block.timestamp
        );
        
        return bookingCounter;
    }
    
    /**
     * @dev Cancel a booking and request refund
     * @param _bookingId The booking ID to cancel
     */
    function cancelBooking(uint256 _bookingId) external {
        Booking storage booking = bookings[_bookingId];
        
        require(booking.passenger == msg.sender, "Not your booking");
        require(booking.isActive, "Booking already cancelled");
        
        // Mark booking as inactive
        booking.isActive = false;
        
        // Calculate refund (100% for demo, in production could have fees)
        uint256 refundAmount = booking.amount;
        
        // Transfer refund to passenger
        payable(msg.sender).transfer(refundAmount);
        
        emit BookingCancelled(_bookingId, msg.sender, refundAmount);
    }
    
    /**
     * @dev Get all booking IDs for a passenger
     * @param _passenger The passenger address
     */
    function getPassengerBookings(address _passenger) external view returns (uint256[] memory) {
        return passengerBookings[_passenger];
    }
    
    /**
     * @dev Get booking details
     * @param _bookingId The booking ID
     */
    function getBooking(uint256 _bookingId) external view returns (
        address passenger,
        string memory flightId,
        uint256 amount,
        uint256 timestamp,
        bool isActive
    ) {
        Booking memory booking = bookings[_bookingId];
        return (
            booking.passenger,
            booking.flightId,
            booking.amount,
            booking.timestamp,
            booking.isActive
        );
    }
    
    /**
     * @dev Get contract balance
     */
    function getBalance() external view returns (uint256) {
        return address(this).balance;
    }
    
    /**
     * @dev Withdraw funds (owner only)
     * @param _amount Amount to withdraw
     */
    function withdraw(uint256 _amount) external onlyOwner {
        require(_amount <= address(this).balance, "Insufficient balance");
        
        payable(owner).transfer(_amount);
        
        emit FundsWithdrawn(owner, _amount);
    }
    
    /**
     * @dev Transfer ownership
     * @param _newOwner New owner address
     */
    function transferOwnership(address _newOwner) external onlyOwner {
        require(_newOwner != address(0), "Invalid address");
        owner = _newOwner;
    }
}
