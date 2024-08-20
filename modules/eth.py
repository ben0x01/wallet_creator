import asyncio

from aiofile import async_open
from eth_account import Account


class AsyncEthWalletGenerator:
    def __init__(self, wallet_amounts, filename):
        self.wallet_amounts = wallet_amounts
        self.filename = filename

    async def generate_wallet(self):
        account = Account.create()
        private_key = account.key.hex()
        address = account.address

        return address, private_key

    async def write_wallets_to_txt(self, filename):
        async with async_open(filename, 'w') as afp:
            tasks = [self.generate_wallet() for _ in range(self.wallet_amounts)]
            wallets = await asyncio.gather(*tasks)

            for wallet in wallets:
                await afp.write(f"WALLET: {wallet[0]} - PRIVATE KEY: {wallet[1]}\n")

    async def run(self):
        await self.write_wallets_to_txt(self.filename)



