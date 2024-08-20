from config import AMOUNT_WALLETS, BTC_WALLET_SETUP
from modules.bitcoin import BitcoinWalletGenerator
from modules.solana import AsyncSolanaWalletGenerator


async def solana_wallet_create():
    solana_filename = input("Введите название файла для записи:")
    solana_generator = AsyncSolanaWalletGenerator(AMOUNT_WALLETS, solana_filename)
    await solana_generator.run()


async def bitcoin_wallet_create():
    btc_filename = input("Введите название файла для записи:")
    btc_generator = BitcoinWalletGenerator(AMOUNT_WALLETS, BTC_WALLET_SETUP, btc_filename)
    await btc_generator.run()
