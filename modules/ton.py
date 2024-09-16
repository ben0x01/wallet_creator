import asyncio
import pandas as pd
from aiofile import async_open
from tonsdk.contract.wallet import WalletVersionEnum, Wallets
from tonsdk.crypto import mnemonic_new
from tonsdk.utils import bytes_to_b64str

class AsyncTonWalletGenerator:
    def __init__(self, wallet_amounts, filename):
        self.wallet_amounts = wallet_amounts
        self.filename = filename

    async def generate_wallet(self):
        wallet_workchain = 0
        wallet_version = WalletVersionEnum.v3r2
        wallet_mnemonics = mnemonic_new()

        _mnemonics, _pub_k, _priv_k, wallet = Wallets.from_mnemonics(
            wallet_mnemonics, wallet_version, wallet_workchain)

        query = wallet.create_init_external_message()
        bytes_to_b64str(query["message"].to_boc(False))

        user_friendly_address = wallet.address.to_string(is_user_friendly=True)
        raw_address = wallet.address.to_string(is_user_friendly=False)

        user_friendly_address_safe = user_friendly_address.replace('+', '-').replace('/', '_')
        raw_address_safe = raw_address.replace('+', '-').replace('/', '_')

        return user_friendly_address_safe, raw_address_safe, wallet_mnemonics

    async def write_wallets_to_excel(self, filename):
        tasks = []
        for _ in range(self.wallet_amounts):
            tasks.append(self.generate_wallet())

        wallets = await asyncio.gather(*tasks)

        data = {
            "WALLET": [wallet[0] for wallet in wallets],
            "MNEMONIC": [' '.join(wallet[2]) for wallet in wallets],
        }

        df = pd.DataFrame(data)

        df.to_excel(f"{filename}.xlsx", index=False)

    async def run(self):
        await self.write_wallets_to_excel(self.filename)
