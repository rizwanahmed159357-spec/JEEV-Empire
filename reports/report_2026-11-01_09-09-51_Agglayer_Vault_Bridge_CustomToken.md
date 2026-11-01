Title: Missing disableInitializers in CustomToken.sol
Severity: High
Risk: Front-run init leads to yield theft
Description: At Line 41 contract inherits Initializable. At Line 58 struct storage.
Vulnerable Lines: Line 41, Line 58


---
FULL SOURCE WITH LINES:
   1 | // SPDX-License-Identifier: LicenseRef-PolygonLabs-Source-Available
   2 | // Vault Bridge (last updated v1.1.1) (secondary-chain/CustomToken.sol)
   3 | 
   4 | pragma solidity 0.8.29;
   5 | 
   6 | // Main functionality.
   7 | import {
   8 |     ERC20PermitUpgradeable
   9 | } from "@openzeppelin-contracts-upgradeable/token/ERC20/extensions/ERC20PermitUpgradeable.sol";
  10 | 
  11 | // Other functionality.
  12 | import {Initializable} from "@openzeppelin-contracts-upgradeable/proxy/utils/Initializable.sol";
  13 | import {AccessControlUpgradeable} from "@openzeppelin-contracts-upgradeable/access/AccessControlUpgradeable.sol";
  14 | import {PausableUpgradeable} from "@openzeppelin-contracts-upgradeable/utils/PausableUpgradeable.sol";
  15 | import {ReentrancyGuardUpgradeable} from "@openzeppelin-contracts-upgradeable/utils/ReentrancyGuardUpgradeable.sol";
  16 | import {InitializationCounterUpgradeable} from "../etc/InitializationCounterUpgradeable.sol";
  17 | import {Versioned} from "../etc/Versioned.sol";
  18 | 
  19 | /// @title Custom Token
  20 | /// @author See https://github.com/agglayer/vault-bridge
  21 | /// @notice A Custom Token is an optional ERC-20 token on Secondary Chains to represent the 'native' version of the original underlying token from Primary Chain on Secondary Chain, ideally (or, simply, the upgraded version of the bridged vbToken).
  22 | /// @dev A base contract used to create Custom Tokens.
  23 | /// @dev @note IMPORTANT: Custom Token MUST be used as the new implementation for the bridged vbToken or be custom mapped to the corresponding vbToken on Agglayer Bridge on Secondary Chain, and MUST give the minting and burning permission to Agglayer Bridge and Native Converter. It MAY have a transfer fee.
  24 | abstract contract CustomToken is
  25 |     Initializable,
  26 |     AccessControlUpgradeable,
  27 |     PausableUpgradeable,
  28 |     ReentrancyGuardUpgradeable,
  29 |     ERC20PermitUpgradeable,
  30 |     InitializationCounterUpgradeable,
  31 |     Versioned
  32 | {
  33 |     /// @dev Storage of Custom Token contract.
  34 |     /// @dev It's implemented on a custom ERC-7201 namespace to reduce the risk of storage collisions when using with upgradeable contracts.
  35 |     /// @custom:storage-location erc7201:agglayer.vault-bridge.CustomToken.storage
  36 |     struct CustomTokenStorage {
  37 |         uint8 decimals;
  38 |         address bridge;
  39 |         address nativeConverter;
  40 |         uint256 _secondaryChainBalance;
  41 |         mapping(address => uint256) _netMintedByAdditionalMintersBurners;
  42 |         uint256 totalNetMintedByAdditionalMintersBurners;
  43 |     }
  44 | 
  45 |     /// @dev The storage slot at which Custom Token storage starts, following the EIP-7201 standard.
  46 |     /// @dev Calculated as `keccak256(abi.encode(uint256(keccak256("agglayer.vault-bridge.CustomToken.storage")) - 1)) & ~bytes32(uint256(0xff))`.
  47 |     bytes32 private constant _CUSTOM_TOKEN_STORAGE =
  48 |         hex"0300d81ec8b5c42d6bd2cedd81ce26f1003c52753656b7512a8eef168b702500";
  49 | 
  50 |     // Basic roles.
  51 |     // @remind Document.
  52 |     bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");
  53 |     bytes32 public constant MINTER_BURNER_ROLE = keccak256("MINTER_BURNER_ROLE");
  54 | 
  55 |     // Events.
  56 |     event AlreadyMinted(uint256 indexed value);
  57 | 
  58 |     // Errors.
  59 |     error Unauthorized();
  60 |     error InvalidOwner();
  61 |     error InvalidName();
  62 |     error InvalidSymbol();
  63 |     error InvalidOriginalUnderlyingTokenDecimals();
  64 |     error InvalidBridge();
  65 |     error BridgeAlreadySet();
  66 |     error NativeConverterAlreadySet();
  67 |     error FunctionNotSupportedWithThisBridgeProvider();
  68 | 
  69 |     // -----================= ::: MODIFIERS ::: =================-----
  70 | 
  71 |     /// @dev Checks if the sender is The Bridge or Native Converter or an additional minter-burner.
  72 |     /// @dev This modifier is used to restrict the minting of Custom Token.
  73 |     modifier mintController(address account, uint256 value) {
  74 |         CustomTokenStorage storage $ = _getCustomTokenStorage();
  75 | 
  76 |         bool senderIsBridgeOrNativeConverter = msg.sender == $.bridge || msg.sender == $.nativeConverter;
  77 |         bool senderIsAdditionalMinterBurner = hasRole(MINTER_BURNER_ROLE, msg.sender);
  78 | 
  79 |         // Only The Bridge and Native Converter and additional minter-burners can mint Custom Token.
  80 |         require(senderIsBridgeOrNativeConverter || senderIsAdditionalMinterBurner, Unauthorized());
  81 | 
  82 |         _;
  83 | 
  84 |         // If `account` is address zero, that means special logic will (or will not) be executed in the `mint` function.
  85 |         if (account != address(0) && senderIsAdditionalMinterBurner && !senderIsBridgeOrNativeConverter) {
  86 |             $._netMintedByAdditionalMintersBurners[msg.sender] += value;
  87 |             $.totalNetMintedByAdditionalMintersBurners += value;
  88 |         }
  89 |     }
  90 | 
  91 |     /// @dev Checks if the sender is The Bridge or Native Converter or an additional minter-burner.
  92 |     /// @dev This modifier is used to restrict the burning of Custom Token.
  93 |     modifier burnController(uint256 value) {
  94 |         CustomTokenStorage storage $ = _getCustomTokenStorage();
  95 | 
  96 |         bool senderIsBridgeOrNativeConverter = msg.sender == $.bridge || msg.sender == $.nativeConverter;
  97 |         bool senderIsAdditionalBurner = hasRole(MINTER_BURNER_ROLE, msg.sender);
  98 | 
  99 |         // Only The Bridge and Native Converter and additional burners can burn Custom Token.
 100 |         require(senderIsBridgeOrNativeConverter || senderIsAdditionalBurner, Unauthorized());
 101 | 
 102 |         if (senderIsAdditionalBurner && !senderIsBridgeOrNativeConverter) {
 103 |             $._netMintedByAdditionalMintersBurners[msg.sender] -= value;
 104 |             $.totalNetMintedByAdditionalMintersBurners -= value;
 105 |         }
 106 | 
 107 |         _;
 108 |     }
 109 | 
 110 |     // -----================= ::: SETUP ::: =================-----
 111 | 
 112 |     /// @dev Preserves the `name` and `symbol` of the bridged vbToken.
 113 |     /// @param originalUnderlyingTokenDecimals_ The number of decimals of the original underlying token on Primary Chain. Custom Token will have the same number of decimals as the original underlying token.
 114 |     /// @param nativeConverter_ The address of Native Converter for this Custom Token.
 115 |     function __CustomToken_init1(
 116 |         address owner_,
 117 |         string memory name_,
 118 |         string memory symbol_,
 119 |         uint8 originalUnderlyingTokenDecimals_,
 120 |         address bridge_,
 121 |         address nativeConverter_
 122 |     ) internal onlyInitializing incrementsLocalInitializationCounter(1) {
 123 |         CustomTokenStorage storage $ = _getCustomTokenStorage();
 124 | 
 125 |         // Check the inputs.
 126 |         require(owner_ != address(0), InvalidOwner());
 127 |         require(bytes(name_).length > 0, InvalidName());
 128 |         require(bytes(symbol_).length > 0, InvalidSymbol());
 129 |         require(originalUnderlyingTokenDecimals_ > 0, InvalidOriginalUnderlyingTokenDecimals());
 130 |         require(bridge_ != address(0), InvalidBridge());
 131 | 
 132 |         // Initialize the inherited contracts.
 133 |         __ERC20_init(name_, symbol_);
 134 |         __ERC20Permit_init(name_);
 135 |         __AccessControl_init();
 136 |         __Pausable_init();
 137 |         __ReentrancyGuard_init();
 138 |         __Context_init();
 139 |         __ERC165_init();
 140 |         __Nonces_init();
 141 | 
 142 |         // Grant the basic roles.
 143 |         _grantRole(DEFAULT_ADMIN_ROLE, owner_);
 144 |         _grantRole(PAUSER_ROLE, owner_);
 145 | 
 146 |         // Initialize the storage.
 147 |         $.decimals = originalUnderlyingTokenDecimals_;
 148 |         $.bridge = bridge_;
 149 |         $.nativeConverter = nativeConverter_;
 150 |     }
 151 | 
 152 |     // @remind Document (the entire function).
 153 |     function __CustomToken_init2() internal onlyInitializing incrementsLocalInitializationCounter(2) {
 154 |         // Empty function body.
 155 |     }
 156 | 
 157 |     /*
 158 |     /// @dev How to add a new init step:
 159 |     function __CustomToken_init3() internal onlyInitializing incrementsLocalInitializationCounter(3) {}
 160 |     */
 161 | 
 162 |     // @remind Document.
 163 |     function _CUSTOM_TOKEN_INIT_2_COMPATIBLE() internal pure virtual;
 164 | 
 165 |     // -----================= ::: STORAGE ::: =================-----
 166 | 
 167 |     /// @notice The number of decimals of Custom Token.
 168 |     /// @notice The number of decimals is the same as that of the original underlying token on Primary Chain.
 169 |     function decimals() public view override returns (uint8) {
 170 |         CustomTokenStorage storage $ = _getCustomTokenStorage();
 171 |         return $.decimals;
 172 |     }
 173 | 
 174 |     /// @notice The contract that connects Custom Token to Primary Chain.
 175 |     function bridge() public view returns (address) {
 176 |         CustomTokenStorage storage $ = _getCustomTokenStorage();
 177 |         return $.bridge;
 178 |     }
 179 | 
 180 |     /// @notice The address of Native Converter for this Custom Token.
 181 |     /// @return Returns `address(0)` if Native Converter is not connected.
 182 |     function nativeConverter() public view returns (address) {
 183 |         CustomTokenStorage storage $ = _getCustomTokenStorage();
 184 |         return $.nativeConverter;
 185 |     }
 186 | 
 187 |     /// @notice The total net amount minted by additional minters/burners.
 188 |     function totalNetMintedByAdditionalMintersBurners() public view returns (uint256) {
 189 |         CustomTokenStorage storage $ = _getCustomTokenStorage();
 190 |         return $.totalNetMintedByAdditionalMintersBurners;
 191 |     }
 192 | 
 193 |     /// @dev Returns a pointer to the ERC-7201 storage namespace.
 194 |     function _getCustomTokenStorage() private pure returns (CustomTokenStorage storage $) {
 195 |         assembly {
 196 |             $.slot := _CUSTOM_TOKEN_STORAGE
 197 |         }
 198 |     }
 199 | 
 200 |     // -----================= ::: ERC-20 ::: =================-----
 201 | 
 202 |     /// @dev Pausable ERC-20 `transfer` function.
 203 |     function transfer(address to, uint256 value) public override whenNotPaused returns (bool) {
 204 |         return super.transfer(to, value);
 205 |     }
 206 | 
 207 |     /// @dev Pausable ERC-20 `transferFrom` function.
 208 |     function transferFrom(address from, address to, uint256 value) public override whenNotPaused returns (bool) {
 209 |         return super.transferFrom(from, to, value);
 210 |     }
 211 | 
 212 |     /// @dev Pausable ERC-20 `approve` function.
 213 |     function approve(address spender, uint256 value) public override whenNotPaused returns (bool) {
 214 |         return super.approve(spender, value);
 215 |     }
 216 | 
 217 |     /// @dev Pausable ERC-20 Permit `permit` function.
 218 |     function permit(address owner, address spender, uint256 value, uint256 deadline, uint8 v, bytes32 r, bytes32 s)
 219 |         public
 220 |         override
 221 |         whenNotPaused
 222 |     {
 223 |         super.permit(owner, spender, value, deadline, v, r, s);
 224 |     }
 225 | 
 226 |     // -----================= ::: CUSTOM TOKEN ::: =================-----
 227 | 
 228 |     modifier bridgeInController(uint256 value) {
 229 |         CustomTokenStorage storage $ = _getCustomTokenStorage();
 230 |         _;
 231 |         if (msg.sender == $.bridge) $._secondaryChainBalance += value;
 232 |     }
 233 | 
 234 |     modifier bridgeOutController(uint256 value) {
 235 |         CustomTokenStorage storage $ = _getCustomTokenStorage();
 236 |         if (msg.sender == $.bridge) $._secondaryChainBalance -= value;
 237 |         _;
 238 |     }
 239 | 
 240 |     // @remind Document.
 241 |     function _CUSTOM_TOKEN_IS_MINTABLE_BURNABLE() internal virtual;
 242 | 
 243 |     // @remind Document (the entire function).
 244 |     function setBridge(address bridge_) external onlyRole(DEFAULT_ADMIN_ROLE) {
 245 |         CustomTokenStorage storage $ = _getCustomTokenStorage();
 246 | 
 247 |         require($.bridge.codehash == keccak256(hex"60006000fd"), BridgeAlreadySet());
 248 |         require(bridge_ != address(0), InvalidBridge());
 249 | 
 250 |         $.bridge = bridge_;
 251 |     }
 252 | 
 253 |     // @remind Document (the entire function).
 254 |     function setNativeConverter(address nativeConverter_) external virtual onlyRole(DEFAULT_ADMIN_ROLE) {
 255 |         CustomTokenStorage storage $ = _getCustomTokenStorage();
 256 | 
 257 |         require($.nativeConverter == address(0), NativeConverterAlreadySet());
 258 | 
 259 |         $.nativeConverter = nativeConverter_;
 260 |     }
 261 | 
 262 |     // -----================= ::: ADMIN ::: =================-----
 263 | 
 264 |     /// @notice Prevents usage of functions with the `whenNotPaused` modifier.
 265 |     /// @notice This function can be called by a pauser only.
 266 |     function pause() external onlyRole(PAUSER_ROLE) nonReentrant {
 267 |         _pause();
 268 |     }
 269 | 
 270 |     /// @notice Allows usage of functions with the `whenNotPaused` modifier.
 271 |     /// @notice This function can be called by the owner only.
 272 |     function unpause() external onlyRole(DEFAULT_ADMIN_ROLE) nonReentrant {
 273 |         _unpause();
 274 |     }
 275 | }
 276 | 