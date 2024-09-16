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
        tasks = []
        for _ in range(self.wallets_amount):
            tasks.append(self.generate_wallet())

        wallets = await asyncio.gather(*tasks)

        data = {
            "WALLET": [wallet[0] for wallet in wallets],
            "PRIVATE KEY": [wallet[1] for wallet in wallets],
        }

        df = pd.DataFrame(data)

        df.to_excel(f"{filename}.xlsx", index=False)

    async def run(self):
        await self.write_wallets_to_txt(self.filename)
