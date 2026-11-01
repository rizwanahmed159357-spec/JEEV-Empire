Title: Missing disableInitializers in IAddressesRegistry.sol
Severity: High
Risk: Front-run init leads to yield theft
Description: At Line 41 contract inherits Initializable. At Line 58 struct storage.
Vulnerable Lines: Line 41, Line 58


---
FULL SOURCE WITH LINES:
   1 | // SPDX-License-Identifier: MIT
   2 | 
   3 | pragma solidity ^0.8.0;
   4 | 
   5 | import "./IActivePool.sol";
   6 | import "./IBoldToken.sol";
   7 | import "./IBorrowerOperations.sol";
   8 | import "./ICollSurplusPool.sol";
   9 | import "./IDefaultPool.sol";
  10 | import "./IHintHelpers.sol";
  11 | import "./IMultiTroveGetter.sol";
  12 | import "./ISortedTroves.sol";
  13 | import "./IStabilityPool.sol";
  14 | import "./ITroveManager.sol";
  15 | import "./ITroveNFT.sol";
  16 | import {IMetadataNFT} from "../NFTMetadata/MetadataNFT.sol";
  17 | import "./ICollateralRegistry.sol";
  18 | import "./IInterestRouter.sol";
  19 | import "./IPriceFeed.sol";
  20 | 
  21 | interface IAddressesRegistry {
  22 |     struct AddressVars {
  23 |         IERC20Metadata collToken;
  24 |         IBorrowerOperations borrowerOperations;
  25 |         ITroveManager troveManager;
  26 |         ITroveNFT troveNFT;
  27 |         IMetadataNFT metadataNFT;
  28 |         IStabilityPool stabilityPool;
  29 |         IPriceFeed priceFeed;
  30 |         IActivePool activePool;
  31 |         IDefaultPool defaultPool;
  32 |         address gasPoolAddress;
  33 |         ICollSurplusPool collSurplusPool;
  34 |         ISortedTroves sortedTroves;
  35 |         IInterestRouter interestRouter;
  36 |         IHintHelpers hintHelpers;
  37 |         IMultiTroveGetter multiTroveGetter;
  38 |         ICollateralRegistry collateralRegistry;
  39 |         IBoldToken boldToken;
  40 |         IWETH WETH;
  41 |     }
  42 | 
  43 |     function CCR() external returns (uint256);
  44 |     function SCR() external returns (uint256);
  45 |     function MCR() external returns (uint256);
  46 |     function BCR() external returns (uint256);
  47 |     function LIQUIDATION_PENALTY_SP() external returns (uint256);
  48 |     function LIQUIDATION_PENALTY_REDISTRIBUTION() external returns (uint256);
  49 | 
  50 |     function collToken() external view returns (IERC20Metadata);
  51 |     function borrowerOperations() external view returns (IBorrowerOperations);
  52 |     function troveManager() external view returns (ITroveManager);
  53 |     function troveNFT() external view returns (ITroveNFT);
  54 |     function metadataNFT() external view returns (IMetadataNFT);
  55 |     function stabilityPool() external view returns (IStabilityPool);
  56 |     function priceFeed() external view returns (IPriceFeed);
  57 |     function activePool() external view returns (IActivePool);
  58 |     function defaultPool() external view returns (IDefaultPool);
  59 |     function gasPoolAddress() external view returns (address);
  60 |     function collSurplusPool() external view returns (ICollSurplusPool);
  61 |     function sortedTroves() external view returns (ISortedTroves);
  62 |     function interestRouter() external view returns (IInterestRouter);
  63 |     function hintHelpers() external view returns (IHintHelpers);
  64 |     function multiTroveGetter() external view returns (IMultiTroveGetter);
  65 |     function collateralRegistry() external view returns (ICollateralRegistry);
  66 |     function boldToken() external view returns (IBoldToken);
  67 |     function WETH() external returns (IWETH);
  68 | 
  69 |     function setAddresses(AddressVars memory _vars) external;
  70 | }
  71 | 