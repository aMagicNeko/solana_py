from solana.rpc.websocket_api import SolanaWsClientProtocol, connect
import asyncio
from solana.rpc.commitment import Confirmed
from raydium_log import *
import threading
from config import *
from solders.signature import Signature
import json
from logger_store import *
from pool_info import *
wss_url = "wss://solana-mainnet.api.syndica.io/api-token/2Tq515vn1usWZBd1CED2ryeAjZsbAfDrwp14W9fyxpUgoAA8J9atUgCzEgNATAxGm4mYgaCrcGhvXUqhdnzvu29j7JDwTLV59Nc6R83wAtHub1MMLyRC9eGXMrK4Z5EDAYvhr1nun27e1G6uEABbjhSKHAhGXapKhrQZWyH4s4ZhpBFEBCnpp6bmGctnsPAsBcTCyH4vwYhxhBU788AVqTJYJFShudP3MTSzmEazaK8CSR11fs5kBtGK7kvJDeeBLuvJM7coBoG41KQMG6pR4gPZgL3KrxJSPerRSLhYUTEC9KGhptkxhL71Ym9qtwQ2XkuMtdjmvaUGpTbUXbdjggqrmsiYh4aJacDfxAoWKrre5TWfDmvqRwqYJCL8wh3Pzom2oUnLDjM5q85husW2pAx57EmWNfyd2PbGoCSRpateLmBWbpNZ29tJuEFHEGV7R4gwZG5iRRm9XtwotsavtR4wCPk7HiwxN2CFn3YopEZk7L4jVgJYfjvCQMQr7/"
def get_tx(sig: Signature):
    print("get tx")
    tx_rsp = client.get_transaction(sig, commitment=Confirmed, max_supported_transaction_version=0)
    if tx_rsp.value is None:
        return
    print("get tx1")
    parse_tx_details(json.loads(tx_rsp.to_json())['result'])

def parse_tx_details(transaction_details: json):
    if transaction_details is None or transaction_details['meta']['err'] is not None:
        return
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
        print_message(log, 0)
        instruction = instructions[i][1]
        if log.log_type == LogType.Init:
            pool_idx = instruction['accounts'][4]
            pool_addr = Pubkey.from_string(address_list[pool_idx])
            pools_infos[pool_addr] = PoolInfo(pool_addr, log.coin_amount, log.pc_amount)
        elif log.log_type == LogType.SwapBaseIn or log.log_type == LogType.SwapBaseOut:
            # for swap, amm pool address
            pool_idx = instruction['accounts'][1]
            pool_addr = Pubkey.from_string(address_list[pool_idx])
            if pool_addr not in pools_infos:
                continue
            step = get_swap_step(log)
            pools_infos[pool_addr].update_position(step)
        elif log.log_type == LogType.Withdraw:
            pool_idx = instruction['accounts'][1]
            pool_addr = Pubkey.from_string(address_list[pool_idx])
            if pool_addr not in pools_infos:
                continue
            ntoken0 = log.pool_coin - log.out_coin
            ntoken1 = log.pool_pc - log.out_pc
            pools_infos[pool_addr].update(ntoken0, ntoken1)
        elif log.log_type == LogType.Deposit:
            pool_idx = instruction['accounts'][1]
            pool_addr = Pubkey.from_string(address_list[pool_idx])
            if pool_addr not in pools_infos:
                continue
            ntoken0 = log.pool_coin + log.deduct_coin
            ntoken1 = log.pool_pc + log.deduct_pc
            pools_infos[pool_addr].update(ntoken0, ntoken1)
    if pool_addr in pools_infos:
        print_message(f"sig{transaction_details['transaction']['signatures']} {log} {pools_infos[pool_addr].nsols}:{pools_infos[pool_addr].ntokens}")

async def main():
    async with connect(wss_url) as wss_client:
        await wss_client.logs_subscribe(commitment=Confirmed)
        while True:
            logs = await wss_client.recv()
            for log_notice in logs:
                #print(log_notice)
                try:
                    if log_notice.result.value.err is not None:
                        continue
                    flag = False
                    for log in log_notice.result.value.logs:
                        if is_ray_log(log):
                            flag = True
                            print("ray log")
                            break
                except:
                    continue
                if flag:
                    #get_tx(log_notice.result.value.signature)
                    my_thread = threading.Thread(target=get_tx, args=(log_notice.result.value.signature,))
                    my_thread.start()
asyncio.get_event_loop().run_until_complete(main())
