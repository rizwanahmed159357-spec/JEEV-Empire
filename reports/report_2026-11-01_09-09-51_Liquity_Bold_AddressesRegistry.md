Title: Missing disableInitializers in AddressesRegistry.sol
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
   5 | import "./Dependencies/Ownable.sol";
   6 | import {MIN_LIQUIDATION_PENALTY_SP, MAX_LIQUIDATION_PENALTY_REDISTRIBUTION} from "./Dependencies/Constants.sol";
   7 | import "./Interfaces/IAddressesRegistry.sol";
   8 | 
   9 | contract AddressesRegistry is Ownable, IAddressesRegistry {
  10 |     IERC20Metadata public collToken;
  11 |     IBorrowerOperations public borrowerOperations;
  12 |     ITroveManager public troveManager;
  13 |     ITroveNFT public troveNFT;
  14 |     IMetadataNFT public metadataNFT;
  15 |     IStabilityPool public stabilityPool;
  16 |     IPriceFeed public priceFeed;
  17 |     IActivePool public activePool;
  18 |     IDefaultPool public defaultPool;
  19 |     address public gasPoolAddress;
  20 |     ICollSurplusPool public collSurplusPool;
  21 |     ISortedTroves public sortedTroves;
  22 |     IInterestRouter public interestRouter;
  23 |     IHintHelpers public hintHelpers;
  24 |     IMultiTroveGetter public multiTroveGetter;
  25 |     ICollateralRegistry public collateralRegistry;
  26 |     IBoldToken public boldToken;
  27 |     IWETH public WETH;
  28 | 
  29 |     // Critical system collateral ratio. If the system's total collateral ratio (TCR) falls below the CCR, some borrowing operation restrictions are applied
  30 |     uint256 public immutable CCR;
  31 |     // Shutdown system collateral ratio. If the system's total collateral ratio (TCR) for a given collateral falls below the SCR,
  32 |     // the protocol triggers the shutdown of the borrow market and permanently disables all borrowing operations except for closing Troves.
  33 |     uint256 public immutable SCR;
  34 | 
  35 |     // Minimum collateral ratio for individual troves
  36 |     uint256 public immutable MCR;
  37 |     // Extra buffer of collateral ratio to join a batch or adjust a trove inside a batch (on top of MCR)
  38 |     uint256 public immutable BCR;
  39 |     // Liquidation penalty for troves offset to the SP
  40 |     uint256 public immutable LIQUIDATION_PENALTY_SP;
  41 |     // Liquidation penalty for troves redistributed
  42 |     uint256 public immutable LIQUIDATION_PENALTY_REDISTRIBUTION;
  43 | 
  44 |     error InvalidCCR();
  45 |     error InvalidMCR();
  46 |     error InvalidBCR();
  47 |     error InvalidSCR();
  48 |     error SPPenaltyTooLow();
  49 |     error SPPenaltyGtRedist();
  50 |     error RedistPenaltyTooHigh();
  51 | 
  52 |     event CollTokenAddressChanged(address _collTokenAddress);
  53 |     event BorrowerOperationsAddressChanged(address _borrowerOperationsAddress);
  54 |     event TroveManagerAddressChanged(address _troveManagerAddress);
  55 |     event TroveNFTAddressChanged(address _troveNFTAddress);
  56 |     event MetadataNFTAddressChanged(address _metadataNFTAddress);
  57 |     event StabilityPoolAddressChanged(address _stabilityPoolAddress);
  58 |     event PriceFeedAddressChanged(address _priceFeedAddress);
  59 |     event ActivePoolAddressChanged(address _activePoolAddress);
  60 |     event DefaultPoolAddressChanged(address _defaultPoolAddress);
  61 |     event GasPoolAddressChanged(address _gasPoolAddress);
  62 |     event CollSurplusPoolAddressChanged(address _collSurplusPoolAddress);
  63 |     event SortedTrovesAddressChanged(address _sortedTrovesAddress);
  64 |     event InterestRouterAddressChanged(address _interestRouterAddress);
  65 |     event HintHelpersAddressChanged(address _hintHelpersAddress);
  66 |     event MultiTroveGetterAddressChanged(address _multiTroveGetterAddress);
  67 |     event CollateralRegistryAddressChanged(address _collateralRegistryAddress);
  68 |     event BoldTokenAddressChanged(address _boldTokenAddress);
  69 |     event WETHAddressChanged(address _wethAddress);
  70 | 
  71 |     constructor(
  72 |         address _owner,
  73 |         uint256 _ccr,
  74 |         uint256 _mcr,
  75 |         uint256 _bcr,
  76 |         uint256 _scr,
  77 |         uint256 _liquidationPenaltySP,
  78 |         uint256 _liquidationPenaltyRedistribution
  79 |     ) Ownable(_owner) {
  80 |         if (_ccr <= 1e18 || _ccr >= 2e18) revert InvalidCCR();
  81 |         if (_mcr <= 1e18 || _mcr >= 2e18) revert InvalidMCR();
  82 |         if (_bcr < 5e16 || _bcr >= 50e16) revert InvalidBCR();
  83 |         if (_scr <= 1e18 || _scr >= 2e18) revert InvalidSCR();
  84 |         if (_liquidationPenaltySP < MIN_LIQUIDATION_PENALTY_SP) revert SPPenaltyTooLow();
  85 |         if (_liquidationPenaltySP > _liquidationPenaltyRedistribution) revert SPPenaltyGtRedist();
  86 |         if (_liquidationPenaltyRedistribution > MAX_LIQUIDATION_PENALTY_REDISTRIBUTION) revert RedistPenaltyTooHigh();
  87 | 
  88 |         CCR = _ccr;
  89 |         SCR = _scr;
  90 |         MCR = _mcr;
  91 |         BCR = _bcr;
  92 |         LIQUIDATION_PENALTY_SP = _liquidationPenaltySP;
  93 |         LIQUIDATION_PENALTY_REDISTRIBUTION = _liquidationPenaltyRedistribution;
  94 |     }
  95 | 
  96 |     function setAddresses(AddressVars memory _vars) external onlyOwner {
  97 |         collToken = _vars.collToken;
  98 |         borrowerOperations = _vars.borrowerOperations;
  99 |         troveManager = _vars.troveManager;
 100 |         troveNFT = _vars.troveNFT;
 101 |         metadataNFT = _vars.metadataNFT;
 102 |         stabilityPool = _vars.stabilityPool;
 103 |         priceFeed = _vars.priceFeed;
 104 |         activePool = _vars.activePool;
 105 |         defaultPool = _vars.defaultPool;
 106 |         gasPoolAddress = _vars.gasPoolAddress;
 107 |         collSurplusPool = _vars.collSurplusPool;
 108 |         sortedTroves = _vars.sortedTroves;
 109 |         interestRouter = _vars.interestRouter;
 110 |         hintHelpers = _vars.hintHelpers;
 111 |         multiTroveGetter = _vars.multiTroveGetter;
 112 |         collateralRegistry = _vars.collateralRegistry;
 113 |         boldToken = _vars.boldToken;
 114 |         WETH = _vars.WETH;
 115 | 
 116 |         emit CollTokenAddressChanged(address(_vars.collToken));
 117 |         emit BorrowerOperationsAddressChanged(address(_vars.borrowerOperations));
 118 |         emit TroveManagerAddressChanged(address(_vars.troveManager));
 119 |         emit TroveNFTAddressChanged(address(_vars.troveNFT));
 120 |         emit MetadataNFTAddressChanged(address(_vars.metadataNFT));
 121 |         emit StabilityPoolAddressChanged(address(_vars.stabilityPool));
 122 |         emit PriceFeedAddressChanged(address(_vars.priceFeed));
 123 |         emit ActivePoolAddressChanged(address(_vars.activePool));
 124 |         emit DefaultPoolAddressChanged(address(_vars.defaultPool));
 125 |         emit GasPoolAddressChanged(_vars.gasPoolAddress);
 126 |         emit CollSurplusPoolAddressChanged(address(_vars.collSurplusPool));
 127 |         emit SortedTrovesAddressChanged(address(_vars.sortedTroves));
 128 |         emit InterestRouterAddressChanged(address(_vars.interestRouter));
 129 |         emit HintHelpersAddressChanged(address(_vars.hintHelpers));
 130 |         emit MultiTroveGetterAddressChanged(address(_vars.multiTroveGetter));
 131 |         emit CollateralRegistryAddressChanged(address(_vars.collateralRegistry));
 132 |         emit BoldTokenAddressChanged(address(_vars.boldToken));
 133 |         emit WETHAddressChanged(address(_vars.WETH));
 134 | 
 135 |         _renounceOwnership();
 136 |     }
 137 | }
 138 | 