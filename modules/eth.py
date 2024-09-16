import asyncio

from aiofile import async_open
from eth_account import Account


class AsyncEthWalletGenerator:
    def __init__(self, wallet_amounts, filename):
        self.wallet_amounts = wallet_amounts
        self.filename = filename

    @staticmethod
    async def generate_wallet():
        account = Account.create()
        private_key = account.key.hex()
        address = account.address

        return address, private_key

    async def write_wallets_to_txt(self, filename):
        tasks = [self.generate_wallet() for _ in range(self.wallet_amounts)]
        wallets = await asyncio.gather(*tasks)

        data = {
            "WALLET": [wallet[0] for wallet in wallets],
            "PRIVATE KEY": [wallet[1] for wallet in wallets],
        }

        df = pd.DataFrame(data)

        df.to_excel(f"{filename}.xlsx", index=False)

    async def run(self):
        await self.write_wallets_to_txt(self.filename)



