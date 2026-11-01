Title: Missing disableInitializers in CustomTokenAgglayer.sol
Severity: High
Risk: Front-run init leads to yield theft
Description: At Line 41 contract inherits Initializable. At Line 58 struct storage.
Vulnerable Lines: Line 41, Line 58


---
FULL SOURCE WITH LINES:
   1 | // SPDX-License-Identifier: LicenseRef-PolygonLabs-Source-Available
   2 | // Vault Bridge (last updated v1.1.1) (secondary-chain/agglayer/CustomTokenAgglayer.sol)
   3 | 
   4 | pragma solidity 0.8.29;
   5 | 
   6 | // Main functionality.
   7 | import {CustomToken} from "../CustomToken.sol";
   8 | 
   9 | // External contracts.
  10 | import {NativeConverter} from "../NativeConverter.sol";
  11 | 
  12 | // @remind Document.
  13 | /// @author See https://github.com/agglayer/vault-bridge
  14 | abstract contract CustomTokenAgglayer is CustomToken {
  15 |     // -----================= ::: CUSTOM TOKEN ::: =================-----
  16 | 
  17 |     /// @notice This function can be called by Agglayer Bridge, Native Converter, and additional minter-burners only.
  18 |     function mint(address account, uint256 value) external whenNotPaused mintController(account, value) nonReentrant {
  19 |         if (msg.sender == bridge() && account == address(0)) {
  20 |             NativeConverter(nativeConverter()).removeMigrationInProgress(value);
  21 | 
  22 |             emit AlreadyMinted(value);
  23 | 
  24 |             return;
  25 |         }
  26 | 
  27 |         _requireNotPaused();
  28 | 
  29 |         _mint(account, value);
  30 |     }
  31 | 
  32 |     /// @notice Burns Custom Tokens from a holder.
  33 |     /// @notice This function can be called by Agglayer Bridge, Native Converter, and additional minter-burners only.
  34 |     function burn(address account, uint256 value) external whenNotPaused burnController(value) nonReentrant {
  35 |         _burn(account, value);
  36 |     }
  37 | 
  38 |     /// @inheritdoc CustomToken
  39 |     function _CUSTOM_TOKEN_IS_MINTABLE_BURNABLE() internal override {}
  40 | }
  41 | 