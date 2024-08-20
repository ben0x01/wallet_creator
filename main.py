import asyncio
from runner import solana_wallet_create, bitcoin_wallet_create


def main_menu():
    print("Main Menu")
    print("1. Run generate solana wallets")
    print("2. Run generate bitcoin wallets ")
    print("3. Exit")

    choice = input("Choose an option: ").strip()

    if choice == '1':
        asyncio.run(solana_wallet_create())
    elif choice == '2':
        asyncio.run(bitcoin_wallet_create())
    elif choice == '3':
        print("Exiting...")
        return
    else:
        print("Invalid choice. Please try again.")
        main_menu()


if __name__ == "__main__":
    main_menu()
