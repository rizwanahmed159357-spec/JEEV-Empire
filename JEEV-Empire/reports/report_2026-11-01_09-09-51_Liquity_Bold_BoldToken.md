Title: Missing disableInitializers in BoldToken.sol
Severity: High
Risk: Front-run init leads to yield theft
Description: At Line 41 contract inherits Initializable. At Line 58 struct storage.
Vulnerable Lines: Line 41, Line 58


---
FULL SOURCE WITH LINES:
   1 | // SPDX-License-Identifier: BUSL-1.1
   2 | 
   3 | pragma solidity 0.8.24;
   4 | 
   5 | import "openzeppelin-contracts/contracts/token/ERC20/extensions/ERC20Permit.sol";
   6 | import "./Dependencies/Ownable.sol";
   7 | import "./Interfaces/IBoldToken.sol";
   8 | 
   9 | /*
  10 |  * --- Functionality added specific to the BoldToken ---
  11 |  *
  12 |  * 1) Transfer protection: blacklist of addresses that are invalid recipients (i.e. core Liquity contracts) in external
  13 |  * transfer() and transferFrom() calls. The purpose is to protect users from losing tokens by mistakenly sending BOLD directly to a Liquity
  14 |  * core contract, when they should rather call the right function.
  15 |  *
  16 |  * 2) sendToPool() and returnFromPool(): functions callable only Liquity core contracts, which move BOLD tokens between Liquity <-> user.
  17 |  */
  18 | 
  19 | contract BoldToken is Ownable, IBoldToken, ERC20Permit {
  20 |     string internal constant _NAME = "BOLD Stablecoin";
  21 |     string internal constant _SYMBOL = "BOLD";
  22 | 
  23 |     // --- Addresses ---
  24 | 
  25 |     address public collateralRegistryAddress;
  26 |     mapping(address => bool) troveManagerAddresses;
  27 |     mapping(address => bool) stabilityPoolAddresses;
  28 |     mapping(address => bool) borrowerOperationsAddresses;
  29 |     mapping(address => bool) activePoolAddresses;
  30 | 
  31 |     // --- Events ---
  32 |     event CollateralRegistryAddressChanged(address _newCollateralRegistryAddress);
  33 |     event TroveManagerAddressAdded(address _newTroveManagerAddress);
  34 |     event StabilityPoolAddressAdded(address _newStabilityPoolAddress);
  35 |     event BorrowerOperationsAddressAdded(address _newBorrowerOperationsAddress);
  36 |     event ActivePoolAddressAdded(address _newActivePoolAddress);
  37 | 
  38 |     constructor(address _owner) Ownable(_owner) ERC20(_NAME, _SYMBOL) ERC20Permit(_NAME) {}
  39 | 
  40 |     function setBranchAddresses(
  41 |         address _troveManagerAddress,
  42 |         address _stabilityPoolAddress,
  43 |         address _borrowerOperationsAddress,
  44 |         address _activePoolAddress
  45 |     ) external override onlyOwner {
  46 |         troveManagerAddresses[_troveManagerAddress] = true;
  47 |         emit TroveManagerAddressAdded(_troveManagerAddress);
  48 | 
  49 |         stabilityPoolAddresses[_stabilityPoolAddress] = true;
  50 |         emit StabilityPoolAddressAdded(_stabilityPoolAddress);
  51 | 
  52 |         borrowerOperationsAddresses[_borrowerOperationsAddress] = true;
  53 |         emit BorrowerOperationsAddressAdded(_borrowerOperationsAddress);
  54 | 
  55 |         activePoolAddresses[_activePoolAddress] = true;
  56 |         emit ActivePoolAddressAdded(_activePoolAddress);
  57 |     }
  58 | 
  59 |     function setCollateralRegistry(address _collateralRegistryAddress) external override onlyOwner {
  60 |         collateralRegistryAddress = _collateralRegistryAddress;
  61 |         emit CollateralRegistryAddressChanged(_collateralRegistryAddress);
  62 | 
  63 |         _renounceOwnership();
  64 |     }
  65 | 
  66 |     // --- Functions for intra-Liquity calls ---
  67 | 
  68 |     function mint(address _account, uint256 _amount) external override {
  69 |         _requireCallerIsBOorAP();
  70 |         _mint(_account, _amount);
  71 |     }
  72 | 
  73 |     function burn(address _account, uint256 _amount) external override {
  74 |         _requireCallerIsCRorBOorTMorSP();
  75 |         _burn(_account, _amount);
  76 |     }
  77 | 
  78 |     function sendToPool(address _sender, address _poolAddress, uint256 _amount) external override {
  79 |         _requireCallerIsStabilityPool();
  80 |         _transfer(_sender, _poolAddress, _amount);
  81 |     }
  82 | 
  83 |     function returnFromPool(address _poolAddress, address _receiver, uint256 _amount) external override {
  84 |         _requireCallerIsStabilityPool();
  85 |         _transfer(_poolAddress, _receiver, _amount);
  86 |     }
  87 | 
  88 |     // --- External functions ---
  89 | 
  90 |     function transfer(address recipient, uint256 amount) public override(ERC20, IERC20) returns (bool) {
  91 |         _requireValidRecipient(recipient);
  92 |         return super.transfer(recipient, amount);
  93 |     }
  94 | 
  95 |     function transferFrom(address sender, address recipient, uint256 amount)
  96 |         public
  97 |         override(ERC20, IERC20)
  98 |         returns (bool)
  99 |     {
 100 |         _requireValidRecipient(recipient);
 101 |         return super.transferFrom(sender, recipient, amount);
 102 |     }
 103 | 
 104 |     // --- 'require' functions ---
 105 | 
 106 |     function _requireValidRecipient(address _recipient) internal view {
 107 |         require(
 108 |             _recipient != address(0) && _recipient != address(this),
 109 |             "BoldToken: Cannot transfer tokens directly to the Bold token contract or the zero address"
 110 |         );
 111 |     }
 112 | 
 113 |     function _requireCallerIsBOorAP() internal view {
 114 |         require(
 115 |             borrowerOperationsAddresses[msg.sender] || activePoolAddresses[msg.sender],
 116 |             "BoldToken: Caller is not BO or AP"
 117 |         );
 118 |     }
 119 | 
 120 |     function _requireCallerIsCRorBOorTMorSP() internal view {
 121 |         require(
 122 |             msg.sender == collateralRegistryAddress || borrowerOperationsAddresses[msg.sender]
 123 |                 || troveManagerAddresses[msg.sender] || stabilityPoolAddresses[msg.sender],
 124 |             "BoldToken: Caller is neither CR nor BorrowerOperations nor TroveManager nor StabilityPool"
 125 |         );
 126 |     }
 127 | 
 128 |     function _requireCallerIsStabilityPool() internal view {
 129 |         require(stabilityPoolAddresses[msg.sender], "BoldToken: Caller is not the StabilityPool");
 130 |     }
 131 | }
 132 | 