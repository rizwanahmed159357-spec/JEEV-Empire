Title: Missing disableInitializers in GenericVaultBridgeToken.sol
Severity: High
Risk: Front-run init leads to yield theft
Description: At Line 41 contract inherits Initializable. At Line 58 struct storage.
Vulnerable Lines: Line 41, Line 58


---
FULL SOURCE WITH LINES:
   1 | // SPDX-License-Identifier: LicenseRef-PolygonLabs-Source-Available
   2 | // Vault Bridge (last updated v1.0.0) (primary-chain/ethereum/GenericVaultBridgeToken.sol)
   3 | 
   4 | pragma solidity 0.8.29;
   5 | 
   6 | // Main functionality.
   7 | import {VaultBridgeToken} from "../VaultBridgeToken.sol";
   8 | 
   9 | /// @title Generic Vault Bridge Token
  10 | /// @author See https://github.com/agglayer/vault-bridge
  11 | /// @dev This contract can be used to deploy vbTokens that do not require any customization.
  12 | contract GenericVaultBridgeToken is VaultBridgeToken {
  13 |     // -----================= ::: SETUP ::: =================-----
  14 | 
  15 |     constructor() {
  16 |         _disableInitializers();
  17 |     }
  18 | 
  19 |     // @remind Document.
  20 |     function reinitialize1(address initializer_, VaultBridgeToken.InitializationParameters calldata initParams)
  21 |         external
  22 |         reinitializer(1)
  23 |         nonReentrant
  24 |     {
  25 |         // Initialize the base implementation.
  26 |         __VaultBridgeToken_init1(initializer_, initParams);
  27 |     }
  28 | 
  29 |     // @remind Document (the entire function).
  30 |     function reinitialize2() external reinitializer(2) nonReentrant {
  31 |         _incrementGlobalInitializationCounter(1);
  32 |         _incrementGlobalInitializationCounter(2);
  33 | 
  34 |         __VaultBridgeToken_init2();
  35 |     }
  36 | 
  37 |     /*
  38 |     /// @dev How to add a new reinitializer:
  39 |     function reinitialize3()
  40 |         external
  41 |         reinitializer(_incrementGlobalInitializationCounter(3))
  42 |         nonReentrant
  43 |     {}
  44 |     */
  45 | 
  46 |     // @remind Document (the entire function).
  47 |     function reinitialize(bytes[] calldata reinitializeData) external {
  48 |         bytes4[] memory reinitializeSelectors = new bytes4[](2);
  49 | 
  50 |         reinitializeSelectors[0] = this.reinitialize1.selector;
  51 |         reinitializeSelectors[1] = this.reinitialize2.selector;
  52 | 
  53 |         _reinitialize(reinitializeSelectors, reinitializeData);
  54 |     }
  55 | 
  56 |     /// @inheritdoc VaultBridgeToken
  57 |     function _VAULT_BRIDGE_TOKEN_INIT_2_COMPATIBLE() internal pure override {}
  58 | }
  59 | 