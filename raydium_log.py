import base64
import struct
from dataclasses import dataclass
from enum import Enum

class LogType(Enum):
    Init = 0
    Deposit = 1
    Withdraw = 2
    SwapBaseIn = 3
    SwapBaseOut = 4

    @classmethod
    def from_u8(cls, log_type):
        return cls(log_type)

    def into_u8(self):
        return self.value

@dataclass
class InitLog:
    log_type: LogType
    time: int
    pc_decimals: int
    coin_decimals: int
    pc_lot_size: int
    coin_lot_size: int
    pc_amount: int
    coin_amount: int
    market: str

@dataclass
class DepositLog:
    log_type: LogType
    max_coin: int
    max_pc: int
    base: int
    pool_coin: int
    pool_pc: int
    pool_lp: int
    calc_pnl_x: int
    calc_pnl_y: int
    deduct_coin: int
    deduct_pc: int
    mint_lp: int

@dataclass
class WithdrawLog:
    log_type: LogType
    withdraw_lp: int
    user_lp: int
    pool_coin: int
    pool_pc: int
    pool_lp: int
    calc_pnl_x: int
    calc_pnl_y: int
    out_coin: int
    out_pc: int

@dataclass
class SwapBaseInLog:
    log_type: LogType
    amount_in: int
    minimum_out: int
    direction: int
    user_source: int
    pool_coin: int
    pool_pc: int
    out_amount: int

@dataclass
class SwapBaseOutLog:
    log_type: LogType
    max_in: int
    amount_out: int
    direction: int
    user_source: int
    pool_coin: int
    pool_pc: int
    deduct_in: int

def parse_log(log: str):
    # Remove the 'Program log: ray_log: ' prefix if present
    prefix = 'Program log: ray_log: '
    if log.startswith(prefix):
        log = log[len(prefix):]
    
    # Decode base64
    bytes_data = base64.b64decode(log)
    
    # Determine the log type
    log_type = LogType.from_u8(bytes_data[0])
    log_instance = None

    if log_type == LogType.Init:
        log_instance = InitLog(
            log_type=log_type,
            time=struct.unpack("<Q", bytes_data[1:9])[0],
            pc_decimals=bytes_data[9],
            coin_decimals=bytes_data[10],
            pc_lot_size=struct.unpack("<Q", bytes_data[11:19])[0],
            coin_lot_size=struct.unpack("<Q", bytes_data[19:27])[0],
            pc_amount=struct.unpack("<Q", bytes_data[27:35])[0],
            coin_amount=struct.unpack("<Q", bytes_data[35:43])[0],
            market=base64.b64encode(bytes_data[43:75]).decode('utf-8')
        )
    elif log_type == LogType.Deposit:
        log_instance = DepositLog(
            log_type=log_type,
            max_coin=struct.unpack("<Q", bytes_data[1:9])[0],
            max_pc=struct.unpack("<Q", bytes_data[9:17])[0],
            base=struct.unpack("<Q", bytes_data[17:25])[0],
            pool_coin=struct.unpack("<Q", bytes_data[25:33])[0],
            pool_pc=struct.unpack("<Q", bytes_data[33:41])[0],
            pool_lp=struct.unpack("<Q", bytes_data[41:49])[0],
            calc_pnl_x=struct.unpack("<Q", bytes_data[49:57])[0],
            calc_pnl_y=struct.unpack("<Q", bytes_data[57:65])[0],
            deduct_coin=struct.unpack("<Q", bytes_data[65:73])[0],
            deduct_pc=struct.unpack("<Q", bytes_data[73:81])[0],
            mint_lp=struct.unpack("<Q", bytes_data[81:89])[0]
        )
    elif log_type == LogType.Withdraw:
        log_instance = WithdrawLog(
            log_type=log_type,
            withdraw_lp=struct.unpack("<Q", bytes_data[1:9])[0],
            user_lp=struct.unpack("<Q", bytes_data[9:17])[0],
            pool_coin=struct.unpack("<Q", bytes_data[17:25])[0],
            pool_pc=struct.unpack("<Q", bytes_data[25:33])[0],
            pool_lp=struct.unpack("<Q", bytes_data[33:41])[0],
            calc_pnl_x=struct.unpack("<Q", bytes_data[41:49])[0],
            calc_pnl_y=struct.unpack("<Q", bytes_data[49:57])[0],
            out_coin=struct.unpack("<Q", bytes_data[57:65])[0],
            out_pc=struct.unpack("<Q", bytes_data[65:73])[0]
        )
    elif log_type == LogType.SwapBaseIn:
        log_instance = SwapBaseInLog(
            log_type=log_type,
            amount_in=struct.unpack("<Q", bytes_data[1:9])[0],
            minimum_out=struct.unpack("<Q", bytes_data[9:17])[0],
            direction=struct.unpack("<Q", bytes_data[17:25])[0],
            user_source=struct.unpack("<Q", bytes_data[25:33])[0],
            pool_coin=struct.unpack("<Q", bytes_data[33:41])[0],
            pool_pc=struct.unpack("<Q", bytes_data[41:49])[0],
            out_amount=struct.unpack("<Q", bytes_data[49:57])[0]
        )
    elif log_type == LogType.SwapBaseOut:
        log_instance = SwapBaseOutLog(
            log_type=log_type,
            max_in=struct.unpack("<Q", bytes_data[1:9])[0],
            amount_out=struct.unpack("<Q", bytes_data[9:17])[0],
            direction=struct.unpack("<Q", bytes_data[17:25])[0],
            user_source=struct.unpack("<Q", bytes_data[25:33])[0],
            pool_coin=struct.unpack("<Q", bytes_data[33:41])[0],
            pool_pc=struct.unpack("<Q", bytes_data[41:49])[0],
            deduct_in=struct.unpack("<Q", bytes_data[49:57])[0]
        )
    
    return log_instance

class SwapStep:
    zero_for_one: bool
    amount_in: int
    amount_out: int
    pool_coin: int
    pool_pc: int

def get_swap_step(log) -> SwapStep:
    step = SwapStep()
    step.pool_coin = log.pool_coin
    step.pool_pc = log.pool_pc
    if log.direction == 2:
        step.zero_for_one = True
    else:
        step.zero_for_one = False
    if log.log_type == LogType.SwapBaseIn:
        step.amount_in = log.amount_in
        step.amount_out = log.out_amount
    else:
        step.amount_in = log.deduct_in
        step.amount_out = log.amount_out
    if step.zero_for_one:
        step.pool_coin += step.amount_in
        step.pool_pc -= step.amount_out
    else:
        step.pool_coin -= step.amount_out
        step.pool_pc += step.amount_in
    return step

if __name__ == "__main__":
    # Example usage
    log_str = 'AwDgZn+3gQUAAAAAAAAAAAACAAAAAAAAAADgZn+3gQUADpoeT5tufAEFLSZXEAAAAEIdijsAAAAA'
    parsed_log = parse_log(log_str)
    print(parsed_log)

