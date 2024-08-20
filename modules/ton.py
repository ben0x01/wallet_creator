import asyncio

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

        return wallet.address.to_string(True, True, True), wallet_mnemonics

    async def write_wallets_to_txt(self, filename):
        async with async_open(filename, 'w') as afp:

            tasks = []
            for _ in range(self.wallet_amounts):
                tasks.append(self.generate_wallet())

            wallets = await asyncio.gather(*tasks)

            for wallet in wallets:
                await afp.write(f"WALLET: {wallet[0]} - PRIVATE KEY: {wallet[1]}\n")

    async def run(self):
        await self.write_wallets_to_txt(self.filename)
