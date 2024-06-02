from typing import Dict
from solders.pubkey import Pubkey
from logger_store import print_message

class Wallet:
    def __init__(self, follow_addr):
        self.token_dict = {}
        self.nsols = 0
        self.follow_addr = follow_addr

    def __str__(self):
        ret = f"follow_addr:{self.follow_addr} nsols:{self.nsols}"
        for token in self.token_dict:
            ret += f" {token}:{self.token_dict[token]}"
        return ret
    
    def compute_sell_num(self, token, num_out):
        if token not in self.token_dict:
            return 0
        if num_out >= self.token_dict[token] * 0.7:
            num_out = self.token_dict[token]
        return int(num_out)

    def sell(self, token, num_out, sol_in):
        if token not in self.token_dict or self.token_dict[token] < num_out:
            return
        self.token_dict[token] -= int(num_out)
        if self.token_dict[token] == 0:
            self.token_dict.pop(token)
        self.nsols += int(sol_in)
        print_message(f"{self.follow_addr} sell token:{token} token_out:{num_out} sol_num:{sol_in}", 0)

    def buy(self, token, num_in, sol_out):
        if token not in self.token_dict:
            self.token_dict[token] = 0
        self.token_dict[token] += int(num_in)
        self.nsols -= int(sol_out)
        print_message(f"{self.follow_addr} buy token:{token}, num:{num_in}, sol_out{sol_out}", 0)

follow_wallets: Dict[Pubkey, Wallet] = {}