from solana.rpc.api import Client
from solders.keypair import Keypair #type: ignore

PUB_KEY = "BAwzi681zGP8WMT57piNvm5dPMLdDRrQT1L6YMqZomoK"
PRIV_KEY = "48iiNa3w5n3XSQ9L6dQK6d2hvjXfZZQGgnDTpTMrRaA69ky6ZbijPAZ1NJyW7PqFgj9LPcNWHv6vCeFNrP4DcMLh"
RPC = "https://api.mainnet-beta.solana.com/"
client = Client(RPC)
payer_keypair = Keypair.from_base58_string(PRIV_KEY)
RAY_V4 = "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"
follow_ratio = 1
full_sell_ratio = 0.7
follow_addresses = ["E2SRcmvvX71efevxnYJTcW9oggnprz7Xk2aSj3DV558L", "6gqSyT8GP1H6yXbzM1QKHBcTsWebx7dFK4RCqhhkHRHX", "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj", "4DdrfiDHpmx55i4SPssxVzS9ZaKLb8qr45NKY9Er9nNh", "7saQeFGCGqMffWMMBynTtqgVcXNSp79sJp7BngNuepK9",
"3m213yY4n12wuY8P3L5nRDy5erkCibhkz9fbQDQ4Nuz7", "BPNUnorWNGLAhek7aK9Qf4hP4k2TRcWh2TMqwH9a3mXT", "CVJAHZpDZuhmF5dEqnPW9xtBYwKqrDqZHxprES4qyS1B", "E2SRcmvvX71efevxnYJTcW9oggnprz7Xk2aSj3DV558L"]