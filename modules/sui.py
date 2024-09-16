import hashlib
import hmac
import struct
from ecdsa import SigningKey, Ed25519
from hashlib import blake2b
from mnemonic import Mnemonic
from bech32 import bech32_encode, convertbits
import pandas as pd
import asyncio

from config import BIP39_PBKDF2_ROUNDS, BIP32_PRIVDEV, DERIVATION_PATH, BIP32_SEED_ED25519, BIP39_SALT_MODIFIER


class Serializer:
    def __init__(self):
        self.data = bytearray()

    def u8(self, value):
        self.data.append(value)

    def fixed_bytes(self, value):
        self.data.extend(value)

    def output(self):
        return bytes(self.data)


class PublicKey25519:
    def __init__(self, private_key):
        self.private_key = private_key

    def to_bytes(self):
        sk = SigningKey.from_string(self.private_key, curve=Ed25519)
        vk = sk.verifying_key
        return vk.to_string()

    def __bytes__(self):
        sk = SigningKey.from_string(self.private_key, curve=Ed25519)
        return b'\x00' + sk.verifying_key.to_string()


class SuiPublicKeyUtils:
    def __init__(self, wallet_amounts, filename, words=None, str_derivation_path=DERIVATION_PATH, curve=Ed25519, modifier=BIP32_SEED_ED25519):
        self.privdev = BIP32_PRIVDEV
        self.curve = curve
        self.str_derivation_path = str_derivation_path
        self.modifier = modifier
        self.wallet_amounts = wallet_amounts
        self.filename = filename

        if words is None:
            self.seed_phrase = self.generate_mnemonic()
        else:
            self.seed_phrase = words

        self.private_key = self.mnemonic_to_private_key(self.seed_phrase)
        self.public_key = PublicKey25519(self.private_key)

    @staticmethod
    def generate_mnemonic():
        mnemonic_generator = Mnemonic("english")
        return mnemonic_generator.generate(strength=256)

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

    @staticmethod
    def mnemonic_to_bip39seed(mnemonic, passphrase):
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
    def private_key_to_bech32(private_key_hex, hrp="suiprivkey"):
        private_key_bytes = bytes.fromhex(private_key_hex)

        key_type_byte = b'\x00'
        key_with_type = key_type_byte + private_key_bytes

        bech32_data = convertbits(key_with_type, 8, 5)

        bech32_private_key = bech32_encode(hrp, bech32_data)

        return bech32_private_key

    def generate_sui_keys(self):
        pt_seed = SuiPublicKeyUtils(self.seed_phrase)
        public_key_bytes = pt_seed.public_key.to_bytes()
        public_key_bytes.hex()

        self.sui_address = self.generate_sui_address(public_key_bytes)

        self.sui_private_key = pt_seed.private_key.hex()

        self.sui_private_key_bech32 = self.private_key_to_bech32(self.sui_private_key)

        return self.sui_address, self.sui_private_key_bech32

    @staticmethod
    def generate_sui_address(public_key_bytes) -> str:
        serializer = Serializer()
        serializer.u8(0x00)
        serializer.fixed_bytes(public_key_bytes)
        serialized_data = serializer.output()

        hashed = blake2b(serialized_data, digest_size=32)
        address = hashed.digest()
        return "0x" + address.hex()

    async def write_wallets_to_xlsx(self, filename):
        tasks = []
        for _ in range(self.wallet_amounts):
            tasks.append(self.generate_wallet())

        wallets = await asyncio.gather(*tasks)

        data = {
            "WALLET": [wallet[0] for wallet in wallets],
            "PRIVATE KEY": [wallet[1] for wallet in wallets],
        }

        df = pd.DataFrame(data)

        df.to_excel(f"{filename}.xlsx", index=False)

    async def generate_wallet(self):
        return self.generate_sui_keys()


    async def run(self):
        await self.write_wallets_to_xlsx(self.filename)
