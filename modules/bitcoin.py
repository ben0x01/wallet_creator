import asyncio
from aiofile import async_open
from bitcoinutils.keys import PrivateKey
from bitcoinutils.setup import setup


class BitcoinWalletGenerator:
    def __init__(self, wallet_amount, setup_network, filename):
        self.wallet_amount = wallet_amount
        self.network = setup_network
        self.filename = filename

    async def generate_wallet(self):
        setup(self.network)
        private_key = PrivateKey()
        public_key = private_key.get_public_key()
        address = public_key.get_address()

        return private_key.to_wif(), public_key.to_hex(), address.to_string()

    async def write_data_to_file(self, filename):
        async with async_open(f"{filename}", "w") as file:
            tasks = [self.generate_wallet() for _ in range(self.wallet_amount)]
            wallets = await asyncio.gather(*tasks)

            for wallet in wallets:
                await file.write(f"WALLET: {wallet[2]} - PUBLIC_KEY: {wallet[1]} - PRIVATE KEY: {wallet[0]}\n")

    async def run(self):
        await self.write_data_to_file(self.filename)



