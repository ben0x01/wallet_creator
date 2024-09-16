import asyncio
from aptos_sdk.account import Account
from mnemonic import Mnemonic
import pandas as pd

import hashlib, hmac, struct
from ecdsa.curves import Ed25519
from config import BIP39_PBKDF2_ROUNDS, BIP32_PRIVDEV, DERIVATION_PATH, BIP32_SEED_ED25519, BIP39_SALT_MODIFIER


class PublicKey25519:
    def __init__(self, private_key):
        self.private_key = private_key

    def __bytes__(self):
        sk = Ed25519.SigningKey(self.private_key)
        return '\x00' + sk.get_verifying_key().to_bytes()


class PublicKeyUtils:
    def __init__(self, wallet_amounts, filename, words=Mnemonic("english").generate(), str_derivation_path=DERIVATION_PATH, curve=Ed25519,
                 modifier=BIP32_SEED_ED25519):
        self.filename = filename
        self.wallet_amounts = wallet_amounts
        self.privdev = BIP32_PRIVDEV
        self.curve = curve
        self.str_derivation_path = str_derivation_path
        self.modifier = modifier

        self.private_key = self.mnemonic_to_private_key(words)
        self.public_key = PublicKey25519(self.private_key)

    def derive_bip32childkey(self, parent_key, parent_chain_code, i):
        assert len(parent_key) == 32
        assert len(parent_chain_code) == 32
        k = parent_chain_code
        if (i & self.privdev) != 0:
            key = b'\x00' + parent_key
        else:
            key = bytes(PublicKey25519(parent_key))

        d = key + struct.pack('>L', i)

        h = hmac.new(k, d, hashlib.sha512).digest()
        key, chain_code = h[:32], h[32:]

        return key, chain_code

    def mnemonic_to_bip39seed(self, mnemonic, passphrase):
        mnemonic = bytes(mnemonic, 'utf8')
        salt = bytes(BIP39_SALT_MODIFIER + passphrase, 'utf8')
        return hashlib.pbkdf2_hmac('sha512', mnemonic, salt, BIP39_PBKDF2_ROUNDS)

    def mnemonic_to_private_key(self, mnemonic, passphrase=""):
        derivation_path = self.parse_derivation_path()
        bip39seed = self.mnemonic_to_bip39seed(mnemonic, passphrase)
        master_private_key, master_chain_code = self.bip39seed_to_bip32masternode(bip39seed)
        private_key, chain_code = master_private_key, master_chain_code
        for i in derivation_path:
            private_key, chain_code = self.derive_bip32childkey(private_key, chain_code, i)
        return private_key

    def bip39seed_to_bip32masternode(self, seed):
        k = seed
        h = hmac.new(self.modifier, seed, hashlib.sha512).digest()
        key, chain_code = h[:32], h[32:]
        return key, chain_code

    def parse_derivation_path(self):
        path = []
        if self.str_derivation_path[0:2] != 'm/':
            raise ValueError("Can't recognize derivation path. It should look like \"m/44'/chaincode/change'/index\".")
        for i in self.str_derivation_path.lstrip('m/').split('/'):
            if "'" in i:
                path.append(self.privdev + int(i[:-1]))
            else:
                path.append(int(i))

        return path

    @staticmethod
    async def generate_wallet(filename):
        path = f"m/44'/637'/1'/0'/0'"
        pt = PublicKeyUtils(path, filename)
        apt_account = Account.load_key(pt.private_key.hex())

        return apt_account.address(), f"0x{pt.private_key.hex()}"

    async def write_wallets_to_txt(self, filename):
        tasks = []
        for _ in range(self.wallet_amounts):
            tasks.append(self.generate_wallet(filename))

        wallets = await asyncio.gather(*tasks)

        data = {
            "WALLET": [wallet[0] for wallet in wallets],
            "PRIVATE KEY": [wallet[1] for wallet in wallets],
        }

        df = pd.DataFrame(data)

        df.to_excel(f"{filename}.xlsx", index=False)

    async def run(self):
        await self.write_wallets_to_txt(self.filename)
