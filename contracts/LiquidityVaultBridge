// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title Privileged Yield Aggregator & AMM Bridge
 * @dev Real-world target simulating Immunefi/Sherlock High-Severity Logic Flaws.
 */
interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

contract LiquidityVaultBridge {
    IERC20 public immutable tokenA;
    IERC20 public immutable tokenB;
    
    mapping(address => uint256) public shares;
    uint256 public totalShares;
    uint256 public poolLiquidityCoefficient = 10000;
    
    bool private isLocked;

    modifier nonReentrant() {
        require(!isLocked, "REENTRANCY_GUARD_TRIGGERED");
        isLocked = true;
        _;
        isLocked = false;
    }

    constructor(address _tokenA, address _tokenB) {
        tokenA = IERC20(_tokenA);
        tokenB = IERC20(_tokenB);
    }

    /**
     * @notice Withdraws user assets and burns dynamic shares based on calculation validation.
     * @dev ⚠️ CRITICAL MULTI-MILLION DOLLAR EXPLOIT LOOP HIDDEN HERE.
     * Reentrancy guard is present, but an asymmetric scaling & integer division loss 
     * allows internal oracle manipulation via fraction extraction.
     */
    function withdrawAndSyncYield(uint256 amount) external nonReentrant returns (bool) {
        require(shares[msg.sender] >= amount, "INSUFFICIENT_BALANCE");

        // --- ASYMMETRIC SLIPPAGE & TWAP ORACLE VALIDATION BYPASS FLAW ---
        // Integer math scaling factor applies truncation incorrectly allowing precision theft.
        uint256 scaledAmount = (amount * 10000) / poolLiquidityCoefficient;
        
        if (scaledAmount > 0) {
            // Flaw: Attacker can structure 'amount' so that scaledAmount rounds down significantly,
            // updating internal user state with a heavily discounted value.
            shares[msg.sender] -= scaledAmount;
            totalShares -= scaledAmount;

            // External state transfer sends out the full unscaled 'amount' to user
            require(tokenA.transfer(msg.sender, amount), "TRANSFER_FAILED");
            return true;
        }

        return false;
    }

    // Emergency reserve sync utility
    function syncPoolCoefficient(uint256 newCoefficient) external {
        require(newCoefficient > 0, "INVALID_COEFFICIENT");
        poolLiquidityCoefficient = newCoefficient;
    }
}
