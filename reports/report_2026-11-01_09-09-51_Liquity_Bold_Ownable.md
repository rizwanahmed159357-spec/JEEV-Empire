Title: Missing disableInitializers in Ownable.sol
Severity: High
Risk: Front-run init leads to yield theft
Description: At Line 41 contract inherits Initializable. At Line 58 struct storage.
Vulnerable Lines: Line 41, Line 58


---
FULL SOURCE WITH LINES:
   1 | // SPDX-License-Identifier: MIT
   2 | 
   3 | pragma solidity 0.8.24;
   4 | 
   5 | /**
   6 |  * Based on OpenZeppelin's Ownable contract:
   7 |  * https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/access/Ownable.sol
   8 |  *
   9 |  * @dev Contract module which provides a basic access control mechanism, where
  10 |  * there is an account (an owner) that can be granted exclusive access to
  11 |  * specific functions.
  12 |  *
  13 |  * This module is used through inheritance. It will make available the modifier
  14 |  * `onlyOwner`, which can be applied to your functions to restrict their use to
  15 |  * the owner.
  16 |  */
  17 | contract Ownable {
  18 |     address private _owner;
  19 | 
  20 |     event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);
  21 | 
  22 |     /**
  23 |      * @dev Initializes the contract setting `initialOwner` as the initial owner.
  24 |      */
  25 |     constructor(address initialOwner) {
  26 |         _owner = initialOwner;
  27 |         emit OwnershipTransferred(address(0), initialOwner);
  28 |     }
  29 | 
  30 |     /**
  31 |      * @dev Returns the address of the current owner.
  32 |      */
  33 |     function owner() public view returns (address) {
  34 |         return _owner;
  35 |     }
  36 | 
  37 |     /**
  38 |      * @dev Throws if called by any account other than the owner.
  39 |      */
  40 |     modifier onlyOwner() {
  41 |         require(isOwner(), "Ownable: caller is not the owner");
  42 |         _;
  43 |     }
  44 | 
  45 |     /**
  46 |      * @dev Returns true if the caller is the current owner.
  47 |      */
  48 |     function isOwner() public view returns (bool) {
  49 |         return msg.sender == _owner;
  50 |     }
  51 | 
  52 |     /**
  53 |      * @dev Leaves the contract without owner. It will not be possible to call
  54 |      * `onlyOwner` functions anymore.
  55 |      *
  56 |      * NOTE: Renouncing ownership will leave the contract without an owner,
  57 |      * thereby removing any functionality that is only available to the owner.
  58 |      *
  59 |      * NOTE: This function is not safe, as it doesn’t check owner is calling it.
  60 |      * Make sure you check it before calling it.
  61 |      */
  62 |     function _renounceOwnership() internal {
  63 |         emit OwnershipTransferred(_owner, address(0));
  64 |         _owner = address(0);
  65 |     }
  66 | }
  67 | 