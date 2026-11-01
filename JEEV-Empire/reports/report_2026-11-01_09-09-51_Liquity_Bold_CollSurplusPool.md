Title: Missing disableInitializers in CollSurplusPool.sol
Severity: High
Risk: Front-run init leads to yield theft
Description: At Line 41 contract inherits Initializable. At Line 58 struct storage.
Vulnerable Lines: Line 41, Line 58


---
FULL SOURCE WITH LINES:
   1 | // SPDX-License-Identifier: BUSL-1.1
   2 | 
   3 | pragma solidity 0.8.24;
   4 | 
   5 | import "openzeppelin-contracts/contracts/token/ERC20/utils/SafeERC20.sol";
   6 | 
   7 | import "./Interfaces/ICollSurplusPool.sol";
   8 | import "./Interfaces/IAddressesRegistry.sol";
   9 | 
  10 | contract CollSurplusPool is ICollSurplusPool {
  11 |     using SafeERC20 for IERC20;
  12 | 
  13 |     string public constant NAME = "CollSurplusPool";
  14 | 
  15 |     IERC20 public immutable collToken;
  16 |     address public immutable borrowerOperationsAddress;
  17 |     address public immutable troveManagerAddress;
  18 | 
  19 |     // deposited ether tracker
  20 |     uint256 internal collBalance;
  21 |     // Collateral surplus claimable by trove owners
  22 |     mapping(address => uint256) internal balances;
  23 | 
  24 |     // --- Events ---
  25 | 
  26 |     event BorrowerOperationsAddressChanged(address _newBorrowerOperationsAddress);
  27 |     event TroveManagerAddressChanged(address _newTroveManagerAddress);
  28 | 
  29 |     event CollBalanceUpdated(address indexed _account, uint256 _newBalance);
  30 |     event CollSent(address indexed _to, uint256 _amount);
  31 | 
  32 |     constructor(IAddressesRegistry _addressesRegistry) {
  33 |         collToken = _addressesRegistry.collToken();
  34 |         borrowerOperationsAddress = address(_addressesRegistry.borrowerOperations());
  35 |         troveManagerAddress = address(_addressesRegistry.troveManager());
  36 | 
  37 |         emit BorrowerOperationsAddressChanged(borrowerOperationsAddress);
  38 |         emit TroveManagerAddressChanged(troveManagerAddress);
  39 |     }
  40 | 
  41 |     /* Returns the collBalance state variable
  42 |        Not necessarily equal to the raw coll balance - coll can be forcibly sent to contracts. */
  43 |     function getCollBalance() external view override returns (uint256) {
  44 |         return collBalance;
  45 |     }
  46 | 
  47 |     function getCollateral(address _account) external view override returns (uint256) {
  48 |         return balances[_account];
  49 |     }
  50 | 
  51 |     // --- Pool functionality ---
  52 | 
  53 |     function accountSurplus(address _account, uint256 _amount) external override {
  54 |         _requireCallerIsTroveManager();
  55 | 
  56 |         uint256 newAmount = balances[_account] + _amount;
  57 |         balances[_account] = newAmount;
  58 |         collBalance = collBalance + _amount;
  59 | 
  60 |         emit CollBalanceUpdated(_account, newAmount);
  61 |     }
  62 | 
  63 |     function claimColl(address _account) external override {
  64 |         _requireCallerIsBorrowerOperations();
  65 |         uint256 claimableColl = balances[_account];
  66 |         require(claimableColl > 0, "CollSurplusPool: No collateral available to claim");
  67 | 
  68 |         balances[_account] = 0;
  69 |         emit CollBalanceUpdated(_account, 0);
  70 | 
  71 |         collBalance = collBalance - claimableColl;
  72 |         emit CollSent(_account, claimableColl);
  73 | 
  74 |         collToken.safeTransfer(_account, claimableColl);
  75 |     }
  76 | 
  77 |     // --- 'require' functions ---
  78 | 
  79 |     function _requireCallerIsBorrowerOperations() internal view {
  80 |         require(msg.sender == borrowerOperationsAddress, "CollSurplusPool: Caller is not Borrower Operations");
  81 |     }
  82 | 
  83 |     function _requireCallerIsTroveManager() internal view {
  84 |         require(msg.sender == troveManagerAddress, "CollSurplusPool: Caller is not TroveManager");
  85 |     }
  86 | }
  87 | 