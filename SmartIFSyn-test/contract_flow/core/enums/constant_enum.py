# enum for constant

from enum import Enum


class ConstantEnum(Enum):
    # msg
    msg_sender = 'msg.sender'
    msg_value = 'msg.value'
    msg_data = 'msg.data'
    msg_sig = 'msg.sig'
    # tx
    tx_gasprice = 'tx.gasprice'
    tx_origin = 'tx.origin'
    # block
    block_coinbase = 'block.coinbase'
    block_difficulty = 'block.difficulty'
    block_gaslimit = 'block.gaslimit'
    block_number = 'block.number'
    block_timestamp = 'block.timestamp'
    # balance
    balance = 'balance'
    # time
    now = 'now'
    # this
    this = 'this'

