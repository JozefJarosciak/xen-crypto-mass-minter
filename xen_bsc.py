# ----------------------------------------------------------------------------------------------
# XEN CRYPTO (Multi-Wallet Creator & XEN Minter) for Binance Smart Chain (BSC)
#
# DISCLAIMER
## This script is made only for experienced python coders.
# Do not use this script if you don't know Python or do not have a good knowledge of how XEN, BSC and ETH works.lo you're doing.
# None of the authors, or contributors to this script can be responsible for any losses you may experience by not understanding what you're doing.
# Take all steps necessary to gather understanding of how this script works before you attempt to run it or configure it.
# Long live the XEN Crypto!

# DETAILS
# In the README.md file
# Blog post: https://www.joe0.com/2022/10/12/xen-crypto-multi-wallet-creator-xen-minter-for-binance-smart-chain-bsc/
# ----------------------------------------------------------------------------------------------


import time
import traceback
from hexbytes import HexBytes
from mnemonic import Mnemonic
from web3 import Web3
from datetime import datetime, timedelta

# ----------------------------------------------------------------------------------------------
# CONFIG - START
# ----------------------------------------------------------------------------------------------
number_of_accounts_to_create = 10  # number of wallets
filename_for_saving_new_wallet_details = "new_wallets-bnb.txt" # this is where all newly created wallets will be saved, this can be either just a file name, or a full path on your windows or linux machine (only tested on windows)
claim_set_or_date_range = 1  # 0 - for set date for minting | 1 for data range - data range starts at 'offset=x' and goes until 'number_of_accounts_to_create=x')
offset_days = 1  # Only applicable for date range. This will increase by one day for each new account. !!! - Be careful not to go over max. mint days (390 at the moment of release of this script)
days_to_claim = 400  # Ignored in data range setting
from_account = 'Address of you main funding ETH account on BSC network'  # - E.g. 0x78eCxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxfFE
from_account_private_key = 'Address of you main funding ETH account on BSC network'  # - E.g axxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxc
how_much_BNB_to_transfer = 0.0019  # 0.01 BNB - I recommend 0.0019 as a minimum. Seems to work fine for me, but increase if it script fails to mint XEN on the accounts (in that case script would exit with error)
delay_between_funding_new_account_and_claiming_xen_reward = 30  # This is a delay between the new crypto wallet being seeded with money and the action of minting XEN
your_pass_phrase = 'your_pass_phrase' # password phrase to create new accounts

# CONFIG - DO NOT CHANGE TWO VALUES BELOW
bsc_url = 'https://bsc-dataseed.binance.org:443'  # DO NOT CHANGE THIS
xen_account = '0x2AB0e9e4eE70FFf1fB9D67031E44F6410170d00e'  # DONT CHANGE THIS!!! It is an official address of XEN on BSC network (https://bscscan.com/address/0x2AB0e9e4eE70FFf1fB9D67031E44F6410170d00e)
# CONFIG - END
# ----------------------------------------------------------------------------------------------


# Connect to BSC
web3 = Web3(Web3.HTTPProvider(bsc_url))

# First get balance of your funding wallet
balance = web3.eth.getBalance(from_account)
balance = web3.fromWei(balance, 'ether')

# Figure out how many account in total can be created - this is just informational
how_many_accounts_can_be_created = int(float(balance) / float(how_much_BNB_to_transfer)) - 1

if number_of_accounts_to_create > how_many_accounts_can_be_created:
    print("You want to create", number_of_accounts_to_create, " wallet(s), but you only have BNB (", balance, ") available! That's only sufficient for", how_many_accounts_can_be_created, "wallets")
    print("The process will stop now, decrease number of wallets, to a maximum of: ", how_many_accounts_can_be_created)
    exit(0)
else:
    print("Initializing creation of", number_of_accounts_to_create, " wallet(s). Note: Your balance of BNB (", balance, ") is sufficient for", how_many_accounts_can_be_created, "wallets!")
    # print(f'Balance of Metamask ({from_account}) account is : {balance} ETH!')

for i in range(number_of_accounts_to_create):
    try:

        if claim_set_or_date_range == 1:
            days_to_claim_adjusted = i + offset_days  # for claim date to be adjusted correctly (in range)
        else:
            days_to_claim_adjusted = days_to_claim

        days_to_claim_hex = hex(days_to_claim_adjusted)[2:]  # mint term number will increase from 1 to number of wallets you're creating (shouldn't be higher than max mint term)
        days_to_claim_hex_len = len(days_to_claim_hex)
        xen_string = '0x9ff054df0000000000000000000000000000000000000000000000000000000000000000' # DO NOT CHANGE, THIS IS REQUIRED FOR MINTING
        xen_string = xen_string[:-days_to_claim_hex_len]
        xen_string = xen_string + days_to_claim_hex

        now = datetime.now() + timedelta(days=days_to_claim_adjusted)  # increasing term number reflected here as well
        date_total = now.strftime("%a-%Y-%b-%d_%H-%M-%S")
        label = "XEN_BSC_" + date_total
        print(f"--------------WALLET #{i + 1} of {number_of_accounts_to_create}---------------")

        # print(web3.fromWei(web3.eth.gas_price,'gwei'), web3.eth.gas_price)

        # CREATE A BRAND NEW WALLET
        mnemo = Mnemonic("english")
        words = mnemo.generate(strength=256)
        seed = mnemo.to_seed(words, passphrase=your_pass_phrase)
        account = web3.eth.account.privateKeyToAccount(seed[:32])

        print("NEW NAME: ", label)
        date_pretty = now.strftime("%a %Y-%b-%d")
        print("Minted ", days_to_claim_adjusted, "days from today (", date_pretty, ")")
        print("NEW WALLET SEED WORDS: ", words)
        seed_string = str(HexBytes(seed).hex())
        print("SEED STRING: ", seed_string)
        private_key_string = str(HexBytes(account.privateKey).hex())
        print("PRIVATE KEY: ", private_key_string)
        new_account_eth_address = account.address
        print("ETH ADDRESS: ", new_account_eth_address)
        # SEND MONEY FROM METAMASK ACCOUNT TO THE NEW ACCOUNT
        sender_private_key_string = from_account_private_key

        # Account details
        nonce = web3.eth.getTransactionCount(from_account)
        tx = {
            # 'type': '0x2',
            'nonce': nonce,
            'from': from_account,
            'to': new_account_eth_address,
            'value': web3.toWei(how_much_BNB_to_transfer, 'ether'),
            'gasPrice': '0x2540be400',
            # 'maxFeePerGas': web3.toWei('50', 'gwei'),
            # 'maxPriorityFeePerGas': web3.toWei('1.5', 'gwei'),
            # 'chainId': 56
        }
        gas = web3.eth.estimateGas(tx)
        tx['gas'] = gas
        signed_tx = web3.eth.account.sign_transaction(tx, sender_private_key_string)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print("Transaction hash: https://bscscan.com/tx/" + str(web3.toHex(tx_hash)))

        print("Claiming XEN Reward")  # , from :", new_account_eth_address, "to new account: ", xen_account)
        time.sleep(delay_between_funding_new_account_and_claiming_xen_reward)
        data_input = {
            # 'chainId': 56,
            'gas': 190000,
            'gasPrice': '0x2540be400',
            'nonce': web3.eth.getTransactionCount(web3.toChecksumAddress(new_account_eth_address)),
            # 'maxFeePerGas': web3.toWei(10, 'gwei'),
            # 'maxPriorityFeePerGas': web3.toWei(1.5, 'gwei'),
            'value': web3.toWei(0, 'ether'),
            'data': xen_string,
            'to': web3.toChecksumAddress(xen_account),
            'from': new_account_eth_address
        }
        signed_txn = web3.eth.account.signTransaction(data_input, private_key_string)
        txn_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
        hash = web3.toHex(txn_hash)
        print("Transaction hash: https://bscscan.com/tx/" + str(hash))

        with open(filename_for_saving_new_wallet_details, 'a+') as f:
            f.write("------------------------------------" + "\n")
            f.write("NEW NAME: " + label + "\n")
            f.write("Minted " + str(days_to_claim_adjusted) + " days from today (" + str(date_pretty) + ")" + "\n")
            f.write("NEW WALLET SEED WORDS: " + words + "\n")
            f.write("PRIVATE KEY: " + private_key_string + "\n")
            f.write("ETH ADDRESS: " + new_account_eth_address + "\n")
            f.write("Transaction hash (funding new account): https://bscscan.com/tx/" + str(web3.toHex(tx_hash)) + "\n")
            f.write("Transaction hash (claiming XEN): https://bscscan.com/tx/" + str(hash) + "\n")
            # f.write("Transaction cost = " + str(cost) + " ETH")
            f.write("------------------------------------" + "\n" + "\n")
        f.close()

        print("--------------TRANSACTION END---------------")

        print("")
        print("")
    except Exception as ex:
        print("Something went wrong. Error: ", ex)
        print(traceback.format_exc())
        exit(0)
