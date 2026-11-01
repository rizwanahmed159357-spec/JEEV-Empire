Title: Missing check in DefaultPool.sol
Severity: High
Risk: Funds at risk due to missing validation
Description: At Line 41 abstract contract. At Line 58 struct.
Vulnerable Lines: Line 41, Line 58


---
FULL SOURCE WITH LINES:
   1 | // SPDX-License-Identifier: BUSL-1.1
   2 | 
   3 | pragma solidity 0.8.24;
   4 | 
   5 | import "openzeppelin-contracts/contracts/token/ERC20/utils/SafeERC20.sol";
   6 | 
   7 | import "./Interfaces/IDefaultPool.sol";
   8 | import "./Interfaces/IAddressesRegistry.sol";
   9 | import "./Interfaces/IActivePool.sol";
  10 | 
  11 | /*
  12 |  * The Default Pool holds the Coll and Bold debt (but not Bold tokens) from liquidations that have been redistributed
  13 |  * to active troves but not yet "applied", i.e. not yet recorded on a recipient active trove's struct.
  14 |  *
  15 |  * When a trove makes an operation that applies its pending Coll and Bold debt, its pending Coll and Bold debt is moved
  16 |  * from the Default Pool to the Active Pool.
  17 |  */
  18 | contract DefaultPool is IDefaultPool {
  19 |     using SafeERC20 for IERC20;
  20 | 
  21 |     string public constant NAME = "DefaultPool";
  22 | 
  23 |     IERC20 public immutable collToken;
  24 |     address public immutable troveManagerAddress;
  25 |     address public immutable activePoolAddress;
  26 |     uint256 internal collBalance; // deposited Coll tracker
  27 |     uint256 internal BoldDebt; // debt
  28 | 
  29 |     event CollTokenAddressChanged(address _newCollTokenAddress);
  30 |     event ActivePoolAddressChanged(address _newActivePoolAddress);
  31 |     event TroveManagerAddressChanged(address _newTroveManagerAddress);
  32 |     event DefaultPoolBoldDebtUpdated(uint256 _boldDebt);
  33 |     event DefaultPoolCollBalanceUpdated(uint256 _collBalance);
  34 | 
  35 |     constructor(IAddressesRegistry _addressesRegistry) {
  36 |         collToken = _addressesRegistry.collToken();
  37 |         troveManagerAddress = address(_addressesRegistry.troveManager());
  38 |         activePoolAddress = address(_addressesRegistry.activePool());
  39 | 
  40 |         emit CollTokenAddressChanged(address(collToken));
  41 |         emit TroveManagerAddressChanged(troveManagerAddress);
  42 |         emit ActivePoolAddressChanged(activePoolAddress);
  43 | 
  44 |         // Allow funds movements between Liquity contracts
  45 |         collToken.approve(activePoolAddress, type(uint256).max);
  46 |     }
  47 | 
  48 |     // --- Getters for public variables. Required by IPool interface ---
  49 | 
  50 |     /*
  51 |     * Returns the collBalance state variable.
  52 |     *
  53 |     * Not necessarily equal to the the contract's raw Coll balance - ether can be forcibly sent to contracts.
  54 |     */
  55 |     function getCollBalance() external view override returns (uint256) {
  56 |         return collBalance;
  57 |     }
  58 | 
  59 |     function getBoldDebt() external view override returns (uint256) {
  60 |         return BoldDebt;
  61 |     }
  62 | 
  63 |     // --- Pool functionality ---
  64 | 
  65 |     function sendCollToActivePool(uint256 _amount) external override {
  66 |         _requireCallerIsTroveManager();
  67 |         uint256 newCollBalance = collBalance - _amount;
  68 |         collBalance = newCollBalance;
  69 |         emit DefaultPoolCollBalanceUpdated(newCollBalance);
  70 | 
  71 |         // Send Coll to Active Pool and increase its recorded Coll balance
  72 |         IActivePool(activePoolAddress).receiveColl(_amount);
  73 |     }
  74 | 
  75 |     function receiveColl(uint256 _amount) external {
  76 |         _requireCallerIsActivePool();
  77 | 
  78 |         uint256 newCollBalance = collBalance + _amount;
  79 |         collBalance = newCollBalance;
  80 | 
  81 |         // Pull Coll tokens from ActivePool
  82 |         collToken.safeTransferFrom(msg.sender, address(this), _amount);
  83 | 
  84 |         emit DefaultPoolCollBalanceUpdated(newCollBalance);
  85 |     }
  86 | 
  87 |     function increaseBoldDebt(uint256 _amount) external override {
  88 |         _requireCallerIsTroveManager();
  89 |         BoldDebt = BoldDebt + _amount;
  90 |         emit DefaultPoolBoldDebtUpdated(BoldDebt);
  91 |     }
  92 | 
  93 |     function decreaseBoldDebt(uint256 _amount) external override {
  94 |         _requireCallerIsTroveManager();
  95 |         BoldDebt = BoldDebt - _amount;
  96 |         emit DefaultPoolBoldDebtUpdated(BoldDebt);
  97 |     }
  98 | 
  99 |     // --- 'require' functions ---
 100 | 
 101 |     function _requireCallerIsActivePool() internal view {
 102 |         require(msg.sender == activePoolAddress, "DefaultPool: Caller is not the ActivePool");
 103 |     }
 104 | 
 105 |     function _requireCallerIsTroveManager() internal view {
 106 |         require(msg.sender == troveManagerAddress, "DefaultPool: Caller is not the TroveManager");
 107 |     }
 108 | }
 109 | 