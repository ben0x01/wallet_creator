import asyncio

import base58
from aiofile import async_open
from solders.keypair import Keypair


class AsyncSolanaWalletGenerator:
    def __init__(self, wallets_amount, filename):
        self.wallets_amount = wallets_amount
        self.filename = filename

    @staticmethod
    async def generate_wallet():
        account = Keypair()
        private_key = base58.b58encode(account.secret() + base58.b58decode(str(account.pubkey()))).decode('utf-8')
        return str(account.pubkey()), private_key

    async def write_wallets_to_txt(self, filename):
        async with async_open(filename, 'w') as afp:

            tasks = []
            for _ in range(self.wallets_amount):
                tasks.append(self.generate_wallet())

            wallets = await asyncio.gather(*tasks)

            for wallet in wallets:
                await afp.write(f"WALLET: {wallet[0]} - PRIVATE KEY: {wallet[1]}\n")

    async def run(self):
        await self.write_wallets_to_txt(self.filename)
