// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract PremiumStaking {
    IERC20 public stakingToken;
    mapping(address => uint256) public stakedBalances;
    uint256 public totalStaked;

    constructor(address _stakingToken) {
        stakingToken = IERC20(_stakingToken);
    }

    function emergencyWithdraw() external {
        uint256 balance = stakedBalances[msg.sender];
        require(balance > 0, "No balance");
        stakedBalances[msg.sender] = 0;
        totalStaked -= balance;
        stakingToken.transfer(msg.sender, balance);
    }
}