from typing import Dict
from solders.pubkey import Pubkey
import json
from raydium_log import SwapStep, WithdrawLog
from raydium_swap import fetch_pool_keys, SOL
class PoolInfo:
    def __init__(self, address: Pubkey, ntoken0: int, ntoken1: int):
        self.holdings: Dict[Pubkey, int]= dict() # sol in the pool
        self.address: Pubkey = address
        self.pool_keys = fetch_pool_keys(address.__str__())
        base = self.pool_keys['base_mint']
        if base == Pubkey.from_string(SOL):
            self.sol_as_base: bool = True
            self.nsols = ntoken0
            self.ntokens = ntoken1
        else:
            self.sol_as_base: bool = False
            self.nsols: int = ntoken1
            self.ntokens: int = ntoken0

    def update_position(self, step: SwapStep, address: Pubkey):
        if address not in self.holdings:
            self.holdings[address] = 0
        if self.sol_as_base:
            self.nsols = step.pool_coin
            self.ntokens = step.pool_pc
            if step.zero_for_one:
                self.holdings[address] += step.amount_in
            else:
                self.holdings[address] -= step.amount_out
        else:
            self.nsols = step.pool_pc
            self.ntokens = step.pool_coin
            if step.zero_for_one:
                self.holdings[address] -= step.amount_out
            else:
                self.holdings[address] += step.amount_in
    
    def update(self, ntoken0, ntoken1):
        if self.sol_as_base:
            self.nsols = ntoken0
            self.ntokens = ntoken1
        else:
            self.nsols = ntoken1
            self.ntokens = ntoken0
pools_infos: Dict[Pubkey, PoolInfo] = {}