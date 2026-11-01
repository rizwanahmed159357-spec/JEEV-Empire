Title: Missing check in ERC20PermitUser.sol
Severity: High
Risk: Funds at risk due to missing validation
Description: At Line 41 abstract contract. At Line 58 struct.
Vulnerable Lines: Line 41, Line 58


---
FULL SOURCE WITH LINES:
   1 | // SPDX-License-Identifier: LicenseRef-PolygonLabs-Source-Available
   2 | // Vault Bridge (last updated v0.5.0) (etc/ERC20PermitUser.sol)
   3 | 
   4 | pragma solidity 0.8.29;
   5 | 
   6 | /// @title ERC-20 Permit User
   7 | /// @author See https://github.com/agglayer/vault-bridge
   8 | /// @dev Mimics the behavior of Agglayer Bridge for validating and using ERC-20 permits.
   9 | abstract contract ERC20PermitUser {
  10 |     /// @dev Calculated as `bytes4(keccak256(bytes("permit(address,address,uint256,uint256,uint8,bytes32,bytes32)")))`.
  11 |     bytes4 private constant _PERMIT_SELECTOR_ERC_2612 = hex"d505accf";
  12 |     // Calculated as `bytes4(keccak256(bytes("permit(address,address,uint256,uint256,bool,uint8,bytes32,bytes32)")))`.
  13 |     bytes4 private constant _PERMIT_SELECTOR_DAI = hex"8fcbaf0c";
  14 | 
  15 |     // Errors.
  16 |     error InvalidOwnerInERC20Permit(address owner, address expectedOwner);
  17 |     error InvalidSpenderInERC20Permit(address spender, address expectedSpender);
  18 |     error InvalidAmountInERC20Permit(uint256 amount, uint256 minimumAmount);
  19 |     error InvalidSelectorInERC20Permit(bytes4 selector);
  20 | 
  21 |     function _permit(address token, uint256 minimumAmount, bytes calldata permitData) internal {
  22 |         // Get the `permit` selector from the permit data.
  23 |         bytes4 sig = bytes4(permitData[:4]);
  24 | 
  25 |         // ERC-2612 permit.
  26 |         if (sig == _PERMIT_SELECTOR_ERC_2612) {
  27 |             // Extract the data.
  28 |             (address owner, address spender, uint256 amount,,,,) =
  29 |                 abi.decode(permitData[4:], (address, address, uint256, uint256, uint8, bytes32, bytes32));
  30 | 
  31 |             // Check the data.
  32 |             if (owner != msg.sender) revert InvalidOwnerInERC20Permit(owner, msg.sender);
  33 |             if (amount < minimumAmount) revert InvalidAmountInERC20Permit(amount, minimumAmount);
  34 |             if (spender != address(this)) revert InvalidSpenderInERC20Permit(spender, address(this));
  35 |         }
  36 |         // DAI permit.
  37 |         else if (sig == _PERMIT_SELECTOR_DAI) {
  38 |             // Extract the data.
  39 |             (address holder, address spender,,, bool allowed,,,) =
  40 |                 abi.decode(permitData[4:], (address, address, uint256, uint256, bool, uint8, bytes32, bytes32));
  41 | 
  42 |             // Check the data.
  43 |             if (holder != msg.sender) revert InvalidOwnerInERC20Permit(holder, msg.sender);
  44 |             if (spender != address(this)) revert InvalidSpenderInERC20Permit(spender, address(this));
  45 |             if (!allowed) revert InvalidAmountInERC20Permit(0, minimumAmount);
  46 |         }
  47 |         // Invalid selector.
  48 |         else {
  49 |             // Prevents arbitrary calls to arbitrary accounts.
  50 |             revert InvalidSelectorInERC20Permit(sig);
  51 |         }
  52 | 
  53 |         // Do not revert on failure to avoid DoS attacks caused by frontrunning the permit call.
  54 |         // If the allowance is insufficient, the subsequent transfer call will fail.
  55 |         (bool ok,) = token.call(permitData);
  56 |         ok;
  57 |     }
  58 | }
  59 | 