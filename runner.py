from config import AMOUNT_WALLETS, BTC_WALLET_SETUP
from modules.bitcoin import BitcoinWalletGenerator
from modules.eth import AsyncEthWalletGenerator
from modules.solana import AsyncSolanaWalletGenerator
from modules.ton import AsyncTonWalletGenerator
from modules.aptos import PublicKeyUtils
from modules.sui import SuiPublicKeyUtils


async def solana_wallet_create():
    solana_filename = input("Введите название файла для записи:")
    solana_generator = AsyncSolanaWalletGenerator(AMOUNT_WALLETS, solana_filename)
    await solana_generator.run()


async def bitcoin_wallet_create():
    btc_filename = input("Введите название файла для записи:")
    btc_generator = BitcoinWalletGenerator(AMOUNT_WALLETS, BTC_WALLET_SETUP, btc_filename)
    await btc_generator.run()


async def eth_wallet_create():
    eth_filename = input("Введите название файла для записи:")
    eth_generator = AsyncEthWalletGenerator(AMOUNT_WALLETS, eth_filename)
    await eth_generator.run()


async def ton_wallet_create():
    ton_filename = input("Введите название файла для записи:")
    ton_generator = AsyncTonWalletGenerator(AMOUNT_WALLETS, ton_filename)
    await ton_generator.run()


async def aptos_wallet_create():
    aptos_filename = input("Введите название файла для записи:")
    aptos_generator = PublicKeyUtils(AMOUNT_WALLETS, aptos_filename)
    await aptos_generator.run()


async def sui_wallet_create():
    sui_filename = input("Введите название файла для записи:")
    sui_utils = SuiPublicKeyUtils(wallet_amounts=AMOUNT_WALLETS, filename=sui_filename)
    await sui_utils.run()

async def sei_wallet_create():
    sei_filename = input("Введите название файла для записи:")
    sei_wallet_generator = SeiWalletGenerator(AMOUNT_WALLETS, filename=f"{sei_filename}")
    sei_wallet_generator.generate_sei_wallets_to_csv()

