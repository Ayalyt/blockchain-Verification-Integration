/*
 * @source: https://smartcontractsecurity.github.io/SWC-registry/docs/SWC-104#unchecked-return-valuesol
 * @author: -
 * @vulnerable_at_lines: 13, 18
 */

pragma solidity ^0.4.25;

contract ReturnValue {

  function untrustcall(address callee) public {
    // <yes> <report>
    require(callee.call());
  }

  function callnotchecked(address callee) public {
     // <yes> <report>
    callee.delegatecall();
  }
}