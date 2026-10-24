import os
from groq import Groq

# 1. Groq Client setup karein (Apni asli API key lagayein)
client = Groq(api_key="AAPKI_GROQ_API_KEY_YAHAN_LAGAYEIN")

# 2. Yeh woh galti wali coding hai jo hum check karwana chahte hain
vulnerable_code = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract PremiumStaking is ReentrancyGuard {
    IERC20 public stakingToken;
    mapping(address => uint256) public stakedBalances;
    uint256 public totalStaked;

    function emergencyWithdraw() external nonReentrant {
        uint256 balance = stakedBalances[msg.sender];
        require(balance > 0, "No staked balance");

        stakedBalances[msg.sender] = 0;
        totalStaked -= balance;

        bool success = stakingToken.transfer(msg.sender, balance);
        require(success, "Transfer failed");
    }
}
"""

# 3. AI ko prompt bhein taake woh KHUD galti dhoonde, pehle se answer na ho
chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": f"Analyze this Solidity code for critical smart contract bugs like Read-Only Reentrancy or state sync flaws. Do not give generic advice, find the exact issue:\n\n{vulnerable_code}"
        }
    ],
    model="llama3-8b-8192", # Ya jo bhi Groq model aap use kar rahe hain
)

# 4. Jo AI ne KHUD dimaag chala kar answer diya, woh print hoga
print("=== ASLI BOT RESPONSE ===")
print(chat_completion.choices[0].message.content)
