from typing import Dict
from solders.pubkey import Pubkey
import json
wss_url = "wss://solana-mainnet.api.syndica.io/api-token/2Tq515vn1usWZBd1CED2ryeAjZsbAfDrwp14W9fyxpUgoAA8J9atUgCzEgNATAxGm4mYgaCrcGhvXUqhdnzvu29j7JDwTLV59Nc6R83wAtHub1MMLyRC9eGXMrK4Z5EDAYvhr1nun27e1G6uEABbjhSKHAhGXapKhrQZWyH4s4ZhpBFEBCnpp6bmGctnsPAsBcTCyH4vwYhxhBU788AVqTJYJFShudP3MTSzmEazaK8CSR11fs5kBtGK7kvJDeeBLuvJM7coBoG41KQMG6pR4gPZgL3KrxJSPerRSLhYUTEC9KGhptkxhL71Ym9qtwQ2XkuMtdjmvaUGpTbUXbdjggqrmsiYh4aJacDfxAoWKrre5TWfDmvqRwqYJCL8wh3Pzom2oUnLDjM5q85husW2pAx57EmWNfyd2PbGoCSRpateLmBWbpNZ29tJuEFHEGV7R4gwZG5iRRm9XtwotsavtR4wCPk7HiwxN2CFn3YopEZk7L4jVgJYfjvCQMQr7/"

class PoolInfo:
    def __init__(self):
        self.holdings: Dict[Pubkey, int]= dict() # sol in the pool
        self.sol_as_base: bool = False
        self.nsols: int = 0
        self.ntokens: int = 0
        self.address: Pubkey = None

    def update_position(self, transaction_details: json):
        
