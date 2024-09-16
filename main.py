import asyncio
from runner import solana_wallet_create, bitcoin_wallet_create, eth_wallet_create, ton_wallet_create, \
    aptos_wallet_create, sui_wallet_create


def main_menu():
    print("Main Menu")
    print("1. Run generate solana wallets")
    print("2. Run generate bitcoin wallets ")
    print("3. Run generate eth wallets")
    print("4. Run generate ton wallets")
    print("5. Run generate aptos wallets")
    print("6. Run generate sui wallets")
    print("7. Exit")

    choice = input("Choose an option: ").strip()

    if choice == '1':
        asyncio.run(solana_wallet_create())
    elif choice == '2':
        asyncio.run(bitcoin_wallet_create())
    elif choice == '3':
        asyncio.run(eth_wallet_create())
    elif choice == '4':
        asyncio.run(ton_wallet_create())
    elif choice == '5':
        asyncio.run(aptos_wallet_create())
    elif choice == '6':
        asyncio.run(sui_wallet_create())
    elif choice == '7':
        print("Exiting...")
        return
    else:
        print("Invalid choice. Please try again.")
        main_menu()


if __name__ == "__main__":
    main_menu()
