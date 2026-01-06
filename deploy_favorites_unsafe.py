from vyper import compile_code  # type: ignore
from web3 import Web3
from dotenv import load_dotenv
import os

load_dotenv()
RPC_URL = os.getenv("RPC_URL")
MY_ADDRESS = os.getenv("MY_ADDRESS")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")


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

    signed_transaction = w3.eth.account.sign_transaction(transaction, private_key=PRIVATE_KEY)
    print(signed_transaction)

    tx_hash = w3.eth.send_raw_transaction(signed_transaction.raw_transaction)
    print(f"My TX hash is {tx_hash}")

    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Contract deployed at address: {tx_receipt.contractAddress}")


if __name__ == "__main__":
    main()
