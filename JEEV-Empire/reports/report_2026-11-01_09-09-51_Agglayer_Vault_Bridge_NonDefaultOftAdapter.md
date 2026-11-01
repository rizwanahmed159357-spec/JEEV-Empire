Title: Missing disableInitializers in NonDefaultOftAdapter.sol
Severity: High
Risk: Front-run init leads to yield theft
Description: At Line 41 contract inherits Initializable. At Line 58 struct storage.
Vulnerable Lines: Line 41, Line 58


---
FULL SOURCE WITH LINES:
   1 | // SPDX-License-Identifier: LicenseRef-PolygonLabs-Source-Available
   2 | // Vault Bridge (last updated v1.1.0) (primary-chain/ethereum/layerzero/GenericOftAdapter.sol)
   3 | 
   4 | pragma solidity 0.8.29;
   5 | 
   6 | // @remind Document (the entire file).
   7 | 
   8 | // Main functionality.
   9 | import {OFTAdapterUpgradeable} from "@layerzerolabs-oft-evm-upgradeable/contracts/oft/OFTAdapterUpgradeable.sol";
  10 | 
  11 | // Other functionality.
  12 | import {
  13 |     ReentrancyGuardTransientUpgradeable
  14 | } from "@openzeppelin-contracts-upgradeable/utils/ReentrancyGuardTransientUpgradeable.sol";
  15 | import {InitializationCounterUpgradeable} from "../../etc/InitializationCounterUpgradeable.sol";
  16 | 
  17 | /// @title Non-Default OFT Adapter
  18 | /// @author See https://github.com/agglayer/vault-bridge
  19 | contract NonDefaultOftAdapter is
  20 |     OFTAdapterUpgradeable,
  21 |     ReentrancyGuardTransientUpgradeable,
  22 |     InitializationCounterUpgradeable
  23 | {
  24 |     // Errors.
  25 |     error InvalidToken();
  26 |     error InvalidLzEndpoint();
  27 | 
  28 |     // -----================= ::: SETUP ::: =================-----
  29 | 
  30 |     constructor(address _token, address _lzEndpoint) OFTAdapterUpgradeable(_token, _lzEndpoint) {
  31 |         _disableInitializers();
  32 | 
  33 |         require(_token != address(0), InvalidToken());
  34 |         require(_lzEndpoint != address(0), InvalidLzEndpoint());
  35 |     }
  36 | 
  37 |     function reinitialize1(address _owner, address _delegate)
  38 |         external
  39 |         locked
  40 |         reinitializer(_incrementGlobalInitializationCounter(1))
  41 |         nonReentrant
  42 |     {
  43 |         __Ownable_init(_owner);
  44 |         __OFTAdapter_init(_delegate);
  45 |         __ReentrancyGuardTransient_init();
  46 |     }
  47 | 
  48 |     /*
  49 |     /// @dev How to add a new reinitializer:
  50 |     function reinitialize2()
  51 |         external
  52 |         locked
  53 |         reinitializer(_incrementGlobalInitializationCounter(2))
  54 |         nonReentrant
  55 |     {}
  56 |     */
  57 | 
  58 |     // @remind Document (the entire function).
  59 |     function reinitialize(bytes[] calldata reinitializeData) external {
  60 |         bytes4[] memory reinitializeSelectors = new bytes4[](1);
  61 | 
  62 |         reinitializeSelectors[0] = this.reinitialize1.selector;
  63 | 
  64 |         _reinitialize(reinitializeSelectors, reinitializeData);
  65 |     }
  66 | }
  67 | 