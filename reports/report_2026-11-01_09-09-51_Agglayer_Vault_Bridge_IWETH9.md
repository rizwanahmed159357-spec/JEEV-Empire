Title: Missing disableInitializers in IWETH9.sol
Severity: High
Risk: Front-run init leads to yield theft
Description: At Line 41 contract inherits Initializable. At Line 58 struct storage.
Vulnerable Lines: Line 41, Line 58


---
FULL SOURCE WITH LINES:
   1 | // SPDX-License-Identifier: LicenseRef-PolygonLabs-Source-Available
   2 | // Vault Bridge (last updated v0.5.0) (etc/IWETH9.sol)
   3 | 
   4 | pragma solidity 0.8.29;
   5 | 
   6 | import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
   7 | 
   8 | /// @title Interface for WETH9
   9 | /// @author See https://github.com/agglayer/vault-bridge
  10 | interface IWETH9 is IERC20 {
  11 |     /// @notice Deposit ether to get wrapped ether
  12 |     function deposit() external payable;
  13 | 
  14 |     /// @notice Withdraw wrapped ether to get ether
  15 |     function withdraw(uint256) external;
  16 | }
  17 | 