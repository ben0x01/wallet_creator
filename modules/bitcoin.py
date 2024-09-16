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
        tasks = [self.generate_wallet() for _ in range(self.wallet_amount)]
        wallets = await asyncio.gather(*tasks)

        # Prepare DataFrame
        data = {
            'WALLET': [wallet[2] for wallet in wallets],
            'PUBLIC_KEY': [wallet[1] for wallet in wallets],
            'PRIVATE_KEY': [wallet[0] for wallet in wallets]
        }
        df = pd.DataFrame(data)

        # Write DataFrame to Excel file
        df.to_excel(f"{filename}.xlsx", index=False)

    async def run(self):
        await self.write_data_to_file(self.filename)



