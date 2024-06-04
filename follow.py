import time
from solana.rpc.api import Client
from solders.pubkey import Pubkey
from solders.signature import Signature
from solana.rpc.types import TokenAccountOpts, TxOpts
from typing import Dict, List, Optional, Sequence, Union
from raydium_log import *
from config import *
from raydium_instr import *
from raydium_swap import *
import json
import threading
import time
from wallet import *

def get_latest_transactions(address: Pubkey, tx_client: Client, known_signatures:set):
    # 获取最近的20个交易签名
    response = json.loads(tx_client.get_signatures_for_address(address, limit=1000).to_json())
    new_signatures = []
    #print(response)
    if response['result']:
        for transaction in response['result']:
            signature = transaction['signature']
            if signature not in known_signatures:
                new_signatures.append(signature)
                known_signatures.add(signature)
    return new_signatures

def get_transaction_details(tx_client: Client, signature: Signature):
    response = json.loads(tx_client.get_transaction(Signature.from_string(signature), max_supported_transaction_version=0).to_json())
    if response['result']:
        return response['result']
    return None

def parse_tx_details(transaction_details: json, follow_addr: Pubkey):
    current_utc_timestamp = int(time.time())
    if current_utc_timestamp - transaction_details['blockTime'] >= 5:
        #return
        pass
    ray_logs = [s for s in transaction_details['meta']['logMessages'] if s.startswith("Program log: ray_log:")]
    address_list = []
    address_list += transaction_details['transaction']['message']['accountKeys']
    address_list += transaction_details['meta']['loadedAddresses']['writable']
    address_list += transaction_details['meta']['loadedAddresses']['readonly']
    #print_message(address_list, 0)
    try:
        program_idx = address_list.index("675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8")
    except:
        return
    instructions = []
    for i in range(len(transaction_details['transaction']['message']['instructions'])):
        instr = transaction_details['transaction']['message']['instructions'][i]
        if instr['programIdIndex'] == program_idx:
            instructions.append((i, instr))
    for instrs in transaction_details['meta']['innerInstructions']:
        index = instrs['index']
        for instr in instrs['instructions']:
            if instr['programIdIndex'] == program_idx:
                instructions.append((index, instr))
    instructions.sort(key=lambda x: x[0])
    if len(instructions) != len(ray_logs):
        print_message("log and instruction size not comp!", 0)
    for i in range(len(ray_logs)):
        log = parse_log(ray_logs[i])
        if log.log_type != LogType.SwapBaseIn and log.log_type != LogType.SwapBaseOut:
            continue
        print_message(log, 0)
        pool_idx = parse_instruction(instructions[i][1])
        pool_addr = address_list[pool_idx]
        step = get_swap_step(log)
        simulate_process(pool_addr, step, follow_addr)
    #my_thread = threading.Thread(target=process_swap, args=(pool_addr, step))
    #my_thread = threading.Thread(target=simulate_process, args=(pool_addr, step))
    #my_thread.start()

def main(address: Pubkey):
    wallet.follow_wallets[address] = Wallet(address)
    tx_client = Client("https://solana-mainnet.g.alchemy.com/v2/uXh0wPKkEKt7Ni91RyP7rFQzsHgu5HY3")
    known_signatures = set()
    while True:
        try:
            new_signatures = get_latest_transactions(address, tx_client, known_signatures)
        except:
            continue
        for signature in new_signatures:
            try:
                transaction_details = get_transaction_details(tx_client, signature)
            except:
                continue
            if transaction_details and transaction_details['meta']['err'] is None:
                #print(f"Transaction {signature}: {transaction_details}")
                parse_tx_details(transaction_details, address)
        time.sleep(0.4)

if __name__ == "__main__":
    for address in follow_addresses:
        my_thread = threading.Thread(target=main, args=((Pubkey.from_string(address),)))
        my_thread.start()