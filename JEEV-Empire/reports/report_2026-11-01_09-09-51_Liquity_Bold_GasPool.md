Title: Missing disableInitializers in GasPool.sol
Severity: High
Risk: Front-run init leads to yield theft
Description: At Line 41 contract inherits Initializable. At Line 58 struct storage.
Vulnerable Lines: Line 41, Line 58


---
FULL SOURCE WITH LINES:
   1 | // SPDX-License-Identifier: MIT
   2 | pragma solidity 0.8.24;
   3 | 
   4 | import "openzeppelin-contracts/contracts/token/ERC20/IERC20.sol";
   5 | 
   6 | import "./Interfaces/IAddressesRegistry.sol";
   7 | import "./Interfaces/IBorrowerOperations.sol";
   8 | import "./Interfaces/ITroveManager.sol";
   9 | 
  10 | /**
  11 |  * The purpose of this contract is to hold WETH tokens for gas compensation:
  12 |  * https://github.com/liquity/bold/?tab=readme-ov-file#liquidation-gas-compensation
  13 |  * When a borrower opens a trove, an additional amount of WETH is pulled,
  14 |  * and sent to this contract.
  15 |  * When a borrower closes their active trove, this gas compensation is refunded
  16 |  * When a trove is liquidated, this gas compensation is paid to liquidator
  17 |  */
  18 | contract GasPool {
  19 |     constructor(IAddressesRegistry _addressesRegistry) {
  20 |         IWETH WETH = _addressesRegistry.WETH();
  21 |         IBorrowerOperations borrowerOperations = _addressesRegistry.borrowerOperations();
  22 |         ITroveManager troveManager = _addressesRegistry.troveManager();
  23 | 
  24 |         // Allow BorrowerOperations to refund gas compensation
  25 |         WETH.approve(address(borrowerOperations), type(uint256).max);
  26 |         // Allow TroveManager to pay gas compensation to liquidator
  27 |         WETH.approve(address(troveManager), type(uint256).max);
  28 |     }
  29 | }
  30 | 