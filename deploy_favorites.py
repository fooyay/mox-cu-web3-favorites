from vyper import compile_code  # type: ignore
from web3 import Web3
from dotenv import load_dotenv
import os
from encrypt_key import KEYSTORE_PATH
import getpass
from eth_account import Account

load_dotenv()
RPC_URL = os.getenv("RPC_URL")
MY_ADDRESS = os.getenv("MY_ADDRESS")


def main():
    print("Deploying favorites contract...")
    with open("favorites.vy", "r") as favorites_file:
        favorites_code = favorites_file.read()
        compilation_details = compile_code(favorites_code, output_formats=["bytecode", "abi"])
        # print(compilation_details)

    w3 = Web3(Web3.HTTPProvider(RPC_URL))

    favorites_contract = w3.eth.contract(bytecode=compilation_details["bytecode"], abi=compilation_details["abi"])
    # print(favorites_contract)

    print("Building transaction...")
    nonce = w3.eth.get_transaction_count(w3.eth.accounts[0])
    transaction = favorites_contract.constructor().build_transaction(
        {
            "nonce": nonce,
            "from": w3.eth.accounts[0],
            "gasPrice": w3.eth.gas_price,
        }
    )

    private_key = decrypt_key()
    signed_transaction = w3.eth.account.sign_transaction(transaction, private_key=private_key)
    print(signed_transaction)

    tx_hash = w3.eth.send_raw_transaction(signed_transaction.raw_transaction)
    print(f"My TX hash is {tx_hash}")

    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Contract deployed at address: {tx_receipt.contractAddress}")


def decrypt_key() -> str:
    with open(KEYSTORE_PATH, "r") as keystore_file:
        encrypted_account = keystore_file.read()
        password = getpass.getpass("Enter your password: ")
        key = Account.decrypt(encrypted_account, password)
        return key


if __name__ == "__main__":
    main()
