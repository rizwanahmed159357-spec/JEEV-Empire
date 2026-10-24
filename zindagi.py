# ===== STEP 1: TARGET LOADER WTIH ULTRA-HIGH LEVEL DEFI PROBLEM =====
TARGET_FILE = pathlib.Path("contracts/PremiumStaking.sol")
if not TARGET_FILE.exists(): TARGET_FILE = pathlib.Path("PremiumStaking.sol")

if TARGET_FILE.exists():
    code_text = TARGET_FILE.read_text()
else:
    # Agar file nahi milti to AI ke samne yeh sab se mushkil logic paish hoga:
    code_text = """
    // SPDX-License-Identifier: MIT
    pragma solidity ^0.8.20;

    interface IUniswapV3Pool {
        function slot0() external view returns (uint160 sqrtPriceX96, int24 tick, uint16 observationIndex, uint16 observationCardinality, uint16 observationCardinalityNext, uint8 feeProtocol, bool unlocked);
    }

    interface IERC20 {
        function balanceOf(address account) external view returns (uint256);
        function transfer(address to, uint256 value) external returns (bool);
        function transferFrom(address from, address to, uint256 value) external returns (bool);
    }

    contract PremiumVaultStaking {
        IUniswapV3Pool public immutable targetPool;
        IERC20 public immutable stakingToken;
        IERC20 public immutable rewardToken;

        mapping(address => uint256) public shares;
        uint256 public totalShares;

        constructor(address _pool, address _staking, address _reward) {
            targetPool = IUniswapV3Pool(_pool);
            stakingToken = IERC20(_staking);
            rewardToken = IERC20(_reward);
        }

        // VULNERABILITY CONTEXT: Read-Only Reentrancy & Oracle Manipulation Chain
        // Attacker blocks trigger liquidity changes in the pool, and call this mid-stream.
        function getVaultAssetPrice() public view returns (uint256) {
            (uint160 sqrtPriceX96,,,,,, bool unlocked) = targetPool.slot0();
            // Flaw: Checking 'unlocked' boolean is missing, allowing read-only reentrancy mid-swap
            uint256 spotBalance = stakingToken.balanceOf(address(targetPool));
            return (uint256(sqrtPriceX96) * spotBalance) / 1e18;
        }

        function depositCollateral(uint256 amount) external {
            uint256 price = getVaultAssetPrice();
            uint256 shareToMint = (amount * 1e18) / price;
            
            stakingToken.transferFrom(msg.sender, address(this), amount);
            shares[msg.sender] += shareToMint;
            totalShares += shareToMint;
        }

        function withdrawCollateral(uint256 shareAmount) external {
            require(shares[msg.sender] >= shareAmount, "Insufficient shares");
            uint256 price = getVaultAssetPrice();
            uint256 amountToWithdraw = (shareAmount * price) / 1e18;

            // Low-level state updates after balance shifts - Dangerous workflow sequence
            shares[msg.sender] -= shareAmount;
            totalShares -= shareAmount;
            
            // Interaction before checking complete transfer return state
            (bool success, ) = msg.sender.call{value: 0}(
                abi.encodeWithSignature("transfer(address,uint256)", msg.sender, amountToWithdraw)
            );
            require(success, "Low-level call failed");
        }
    }
    """
    print("No contract file found. Injected High-Level Cross-Contract Read-Only Reentrancy & Oracle Vector for evaluation.")
