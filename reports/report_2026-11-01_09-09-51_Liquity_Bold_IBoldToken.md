Title: Missing disableInitializers in IBoldToken.sol
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
   5 | import "openzeppelin-contracts/contracts/token/ERC20/extensions/IERC20Metadata.sol";
   6 | import "openzeppelin-contracts/contracts/token/ERC20/extensions/IERC20Permit.sol";
   7 | import "openzeppelin-contracts/contracts/interfaces/IERC5267.sol";
   8 | 
   9 | interface IBoldToken is IERC20Metadata, IERC20Permit, IERC5267 {
  10 |     function setBranchAddresses(
  11 |         address _troveManagerAddress,
  12 |         address _stabilityPoolAddress,
  13 |         address _borrowerOperationsAddress,
  14 |         address _activePoolAddress
  15 |     ) external;
  16 | 
  17 |     function setCollateralRegistry(address _collateralRegistryAddress) external;
  18 | 
  19 |     function mint(address _account, uint256 _amount) external;
  20 | 
  21 |     function burn(address _account, uint256 _amount) external;
  22 | 
  23 |     function sendToPool(address _sender, address poolAddress, uint256 _amount) external;
  24 | 
  25 |     function returnFromPool(address poolAddress, address user, uint256 _amount) external;
  26 | }
  27 | 