Title: Missing check in IVaultBridgeTokenInitializer.sol
Severity: High
Risk: Funds at risk due to missing validation
Description: At Line 41 abstract contract. At Line 58 struct.
Vulnerable Lines: Line 41, Line 58


---
FULL SOURCE WITH LINES:
   1 | // SPDX-License-Identifier: LicenseRef-PolygonLabs-Source-Available
   2 | // Vault Bridge (last updated v1.0.0) (etc/IVaultBridgeTokenInitializer.sol)
   3 | 
   4 | pragma solidity 0.8.29;
   5 | 
   6 | // Main functionality.
   7 | import {VaultBridgeToken} from "../primary-chain/VaultBridgeToken.sol";
   8 | 
   9 | /// @title Vault Bridge Token Initializer Interface
  10 | /// @author See https://github.com/agglayer/vault-bridge
  11 | /// @dev This interface exists because of a limitiation in the Solidity compiler.
  12 | interface IVaultBridgeTokenInitializer {
  13 |     /// @dev Vault Bridge Token delegates the initialization to this contract.
  14 |     /// @dev Please refer to `__VaultBridgeToken_init` in `VaultBridgeToken.sol` for more information.
  15 |     function init1(VaultBridgeToken.InitializationParameters calldata initParams) external;
  16 | }
  17 | 