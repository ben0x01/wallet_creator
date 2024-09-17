import pandas as pd
from mnemonic import Mnemonic
from bip_utils import Bip44, Bip44Coins, Bip44Changes, Bip39SeedGenerator, Bip39MnemonicValidator
from bech32 import bech32_encode, convertbits
import hashlib


class SeiWalletGenerator:
    def __init__(self, num_wallets, filename):
        self.num_wallets = num_wallets
        self.filename = filename

    # Method to generate a new mnemonic phrase
    def generate_mnemonic(self):
        mnemo = Mnemonic("english")
        return mnemo.generate(strength=128)  # 12-word mnemonic for 128 bits

    # Method to convert bytes to Bech32 encoding with the desired prefix
    def to_bech32(self, prefix, data):
        five_bit_r = convertbits(data, 8, 5)
        return bech32_encode(prefix, five_bit_r)

    # Method to generate a Sei address from a mnemonic phrase
    def generate_sei_address(self, mnemonic, derivation_path="m/44'/118'/0'/0/0", prefix="sei"):
        # Validate and convert the mnemonic into a seed
        validator = Bip39MnemonicValidator()
        if not validator.IsValid(mnemonic):
            raise ValueError("Invalid mnemonic phrase")

        # Generate seed from mnemonic
        seed = Bip39SeedGenerator(mnemonic).Generate()

        # Derive the BIP44 path for Cosmos-based chains (118 is the coin type for Cosmos)
        bip44_wallet = Bip44.FromSeed(seed, Bip44Coins.COSMOS)
        account = bip44_wallet.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)

        # Get the public key and private key
        pub_key = account.PublicKey().RawCompressed().ToBytes()
        priv_key = account.PrivateKey().Raw().ToBytes()

        # Generate the Cosmos (Sei) address from the public key using Bech32 encoding
        sha256_digest = hashlib.sha256(pub_key).digest()
        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(sha256_digest)
        address_bytes = ripemd160.digest()

        # Bech32 encode the address with the Sei prefix
        sei_address = self.to_bech32(prefix, address_bytes)

        return sei_address, mnemonic, priv_key.hex()

    # Method to generate wallets and save them to a CSV file
    def generate_sei_wallets_to_csv(self):
        wallet_data = []

        for _ in range(self.num_wallets):
            mnemonic = self.generate_mnemonic()
            sei_address, mnemonic, priv_key = self.generate_sei_address(mnemonic)

            wallet_data.append({
                "Sei Address": sei_address,
                "Private Key": priv_key
            })

        df = pd.DataFrame(wallet_data)
        df.to_csv(self.filename, index=False)

        print(f"{self.num_wallets} wallets have been saved to {self.filename}")
