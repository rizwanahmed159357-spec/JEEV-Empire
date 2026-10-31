# Review /tmp/target/certora/harnesses/GenericVaultBridgeToken.sol
Strategy: Agglayer Vault Bridge - $250000 - FREE
Wallet: 0x3e9f8D47103E2f6a6DcBEDf913c1d8E1f97A1C40

Manual review needed.
   1 | // SPDX-License-Identifier: LicenseRef-PolygonLabs-Open-Attribution OR LicenseRef-PolygonLabs-Source-Available
   2 | // Vault Bridge (last updated v1.0.0) (vault-bridge-tokens/GenericVaultBridgeToken.sol)
   3 | 
   4 | pragma solidity 0.8.29;
   5 | 
   6 | // Main functionality.
   7 | import {VaultBridgeToken} from "../../src/VaultBridgeToken.sol";
   8 | 
   9 | /// @title Generic Vault Bridge Token
  10 | /// @author See https://github.com/agglayer/vault-bridge
  11 | /// @dev This contract can be used to deploy vbTokens that do not require any customization.
  12 | contract GenericVaultBridgeToken is VaultBridgeToken {
  13 |     constructor() {
  14 |         _disableInitializers();
  15 |     }
  16 | 
  17 |     function initialize(address initializer_, VaultBridgeToken.InitializationParameters calldata initParams)
  18 |         external
  19 |         initializer
  20 |     {
  21 |         // Initialize the base implementation.
  22 |         __VaultBridgeToken_init(initializer_, initParams);
  23 |     }
  24 | 
  25 |     // Harness methods  
  26 |     function rebalanceReserve_harness(bool force, bool allowRebalanceDown) external 
  27 |     {
  28 |         _rebalanceReserve(force, allowRebalanceDown);
  29 |     }
  30 | 
  31 |     function simulateWithdraw_harness(uint256 assets, bool force) external returns (uint256)
  32 |     {
  33 |         return _simulateWithdraw(assets, force);
  34 |     }
  35 | 
  36 |     function depositIntoYieldVault_harness(uint256 assets, bool exact) external returns (uint256)
  37 |     {
  38 |         return _depositIntoYieldVault(assets, exact);
  39 |     }
  40 | 
  41 |     /// @notice Yield collected getter
  42 | 
  43 | }
  44 | 


---
FULL SOURCE WITH LINES:
   1 | // SPDX-License-Identifier: LicenseRef-PolygonLabs-Open-Attribution OR LicenseRef-PolygonLabs-Source-Available
   2 | // Vault Bridge (last updated v1.0.0) (vault-bridge-tokens/GenericVaultBridgeToken.sol)
   3 | 
   4 | pragma solidity 0.8.29;
   5 | 
   6 | // Main functionality.
   7 | import {VaultBridgeToken} from "../../src/VaultBridgeToken.sol";
   8 | 
   9 | /// @title Generic Vault Bridge Token
  10 | /// @author See https://github.com/agglayer/vault-bridge
  11 | /// @dev This contract can be used to deploy vbTokens that do not require any customization.
  12 | contract GenericVaultBridgeToken is VaultBridgeToken {
  13 |     constructor() {
  14 |         _disableInitializers();
  15 |     }
  16 | 
  17 |     function initialize(address initializer_, VaultBridgeToken.InitializationParameters calldata initParams)
  18 |         external
  19 |         initializer
  20 |     {
  21 |         // Initialize the base implementation.
  22 |         __VaultBridgeToken_init(initializer_, initParams);
  23 |     }
  24 | 
  25 |     // Harness methods  
  26 |     function rebalanceReserve_harness(bool force, bool allowRebalanceDown) external 
  27 |     {
  28 |         _rebalanceReserve(force, allowRebalanceDown);
  29 |     }
  30 | 
  31 |     function simulateWithdraw_harness(uint256 assets, bool force) external returns (uint256)
  32 |     {
  33 |         return _simulateWithdraw(assets, force);
  34 |     }
  35 | 
  36 |     function depositIntoYieldVault_harness(uint256 assets, bool exact) external returns (uint256)
  37 |     {
  38 |         return _depositIntoYieldVault(assets, exact);
  39 |     }
  40 | 
  41 |     /// @notice Yield collected getter
  42 | 
  43 | }
  44 | 