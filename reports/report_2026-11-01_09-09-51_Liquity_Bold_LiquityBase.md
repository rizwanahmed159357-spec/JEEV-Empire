Title: Missing disableInitializers in LiquityBase.sol
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
   5 | import "./Constants.sol";
   6 | import "./LiquityMath.sol";
   7 | import "../Interfaces/IAddressesRegistry.sol";
   8 | import "../Interfaces/IActivePool.sol";
   9 | import "../Interfaces/IDefaultPool.sol";
  10 | import "../Interfaces/IPriceFeed.sol";
  11 | import "../Interfaces/ILiquityBase.sol";
  12 | 
  13 | /*
  14 | * Base contract for TroveManager, BorrowerOperations and StabilityPool. Contains global system constants and
  15 | * common functions.
  16 | */
  17 | contract LiquityBase is ILiquityBase {
  18 |     IActivePool public activePool;
  19 |     IDefaultPool internal defaultPool;
  20 |     IPriceFeed internal priceFeed;
  21 | 
  22 |     event ActivePoolAddressChanged(address _newActivePoolAddress);
  23 |     event DefaultPoolAddressChanged(address _newDefaultPoolAddress);
  24 |     event PriceFeedAddressChanged(address _newPriceFeedAddress);
  25 | 
  26 |     constructor(IAddressesRegistry _addressesRegistry) {
  27 |         activePool = _addressesRegistry.activePool();
  28 |         defaultPool = _addressesRegistry.defaultPool();
  29 |         priceFeed = _addressesRegistry.priceFeed();
  30 | 
  31 |         emit ActivePoolAddressChanged(address(activePool));
  32 |         emit DefaultPoolAddressChanged(address(defaultPool));
  33 |         emit PriceFeedAddressChanged(address(priceFeed));
  34 |     }
  35 |     // --- Gas compensation functions ---
  36 | 
  37 |     function getEntireBranchColl() public view returns (uint256 entireSystemColl) {
  38 |         uint256 activeColl = activePool.getCollBalance();
  39 |         uint256 liquidatedColl = defaultPool.getCollBalance();
  40 | 
  41 |         return activeColl + liquidatedColl;
  42 |     }
  43 | 
  44 |     function getEntireBranchDebt() public view returns (uint256 entireSystemDebt) {
  45 |         uint256 activeDebt = activePool.getBoldDebt();
  46 |         uint256 closedDebt = defaultPool.getBoldDebt();
  47 | 
  48 |         return activeDebt + closedDebt;
  49 |     }
  50 | 
  51 |     function _getTCR(uint256 _price) internal view returns (uint256 TCR) {
  52 |         uint256 entireSystemColl = getEntireBranchColl();
  53 |         uint256 entireSystemDebt = getEntireBranchDebt();
  54 | 
  55 |         TCR = LiquityMath._computeCR(entireSystemColl, entireSystemDebt, _price);
  56 | 
  57 |         return TCR;
  58 |     }
  59 | 
  60 |     function _checkBelowCriticalThreshold(uint256 _price, uint256 _CCR) internal view returns (bool) {
  61 |         uint256 TCR = _getTCR(_price);
  62 | 
  63 |         return TCR < _CCR;
  64 |     }
  65 | 
  66 |     function _calcInterest(uint256 _weightedDebt, uint256 _period) internal pure returns (uint256) {
  67 |         return _weightedDebt * _period / ONE_YEAR / DECIMAL_PRECISION;
  68 |     }
  69 | }
  70 | 