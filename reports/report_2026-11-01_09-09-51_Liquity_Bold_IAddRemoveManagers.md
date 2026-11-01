Title: Missing disableInitializers in IAddRemoveManagers.sol
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
   5 | interface IAddRemoveManagers {
   6 |     function setAddManager(uint256 _troveId, address _manager) external;
   7 |     function setRemoveManager(uint256 _troveId, address _manager) external;
   8 |     function setRemoveManagerWithReceiver(uint256 _troveId, address _manager, address _receiver) external;
   9 |     function addManagerOf(uint256 _troveId) external view returns (address);
  10 |     function removeManagerReceiverOf(uint256 _troveId) external view returns (address, address);
  11 | }
  12 | 