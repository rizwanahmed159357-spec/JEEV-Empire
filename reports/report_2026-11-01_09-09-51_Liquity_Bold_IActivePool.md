Title: Missing disableInitializers in IActivePool.sol
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
   5 | import "./IInterestRouter.sol";
   6 | import "./IBoldRewardsReceiver.sol";
   7 | import "../Types/TroveChange.sol";
   8 | 
   9 | interface IActivePool {
  10 |     function defaultPoolAddress() external view returns (address);
  11 |     function borrowerOperationsAddress() external view returns (address);
  12 |     function troveManagerAddress() external view returns (address);
  13 |     function interestRouter() external view returns (IInterestRouter);
  14 |     // We avoid IStabilityPool here in order to prevent creating a dependency cycle that would break flattening
  15 |     function stabilityPool() external view returns (IBoldRewardsReceiver);
  16 | 
  17 |     function getCollBalance() external view returns (uint256);
  18 |     function getBoldDebt() external view returns (uint256);
  19 |     function lastAggUpdateTime() external view returns (uint256);
  20 |     function aggRecordedDebt() external view returns (uint256);
  21 |     function aggWeightedDebtSum() external view returns (uint256);
  22 |     function aggBatchManagementFees() external view returns (uint256);
  23 |     function aggWeightedBatchManagementFeeSum() external view returns (uint256);
  24 |     function calcPendingAggInterest() external view returns (uint256);
  25 |     function calcPendingSPYield() external view returns (uint256);
  26 |     function calcPendingAggBatchManagementFee() external view returns (uint256);
  27 |     function getNewApproxAvgInterestRateFromTroveChange(TroveChange calldata _troveChange)
  28 |         external
  29 |         view
  30 |         returns (uint256);
  31 | 
  32 |     function mintAggInterest() external;
  33 |     function mintAggInterestAndAccountForTroveChange(TroveChange calldata _troveChange, address _batchManager)
  34 |         external;
  35 |     function mintBatchManagementFeeAndAccountForChange(TroveChange calldata _troveChange, address _batchAddress)
  36 |         external;
  37 | 
  38 |     function setShutdownFlag() external;
  39 |     function hasBeenShutDown() external view returns (bool);
  40 |     function shutdownTime() external view returns (uint256);
  41 | 
  42 |     function sendColl(address _account, uint256 _amount) external;
  43 |     function sendCollToDefaultPool(uint256 _amount) external;
  44 |     function receiveColl(uint256 _amount) external;
  45 |     function accountForReceivedColl(uint256 _amount) external;
  46 | }
  47 | 