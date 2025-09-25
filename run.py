import os
import time
import decimal
import random
from web3 import Web3
from web3.exceptions import TransactionNotFound
from colorama import Fore, Style, init

init(autoreset=True)

RPC_URL = "https://sepolia-rpc.giwa.io"
CHAIN_ID = 91342
EXPLORER_URL = "https://sepolia-explorer.giwa.io"

SWAP_CONTRACT = "0xAD153c844CcAC3D2ea991170624200e54730bE74"
INDSR_TOKEN = "0x89B38c7414EC86Eb2cB003c6362cf010B562FF1e"

SLIPPAGE_TOLERANCE = 1

def get_amount_out_min(amount_wei, slippage_percent):
    """Calculate minimum amount out with slippage tolerance"""
    amount_decimal = decimal.Decimal(amount_wei)
    slippage_factor = decimal.Decimal(1 - slippage_percent / 100)
    return int(amount_decimal * slippage_factor)

def create_swap_data(amount_out_min, to_address):
    amount_hex = hex(amount_out_min)[2:].zfill(64)
    
    to_address_clean = to_address[2:].lower().zfill(64)
    
    transaction_data = f"0xd6556a67{amount_hex}{to_address_clean}"
    
    return transaction_data

def create_approve_data(spender_address):
    spender_clean = spender_address[2:].lower().zfill(64)
    
    max_amount = "f" * 64
    
    transaction_data = f"0x095ea7b3{spender_clean}{max_amount}"
    
    return transaction_data

def create_add_liquidity_data(amount_token_desired, amount_eth_desired):
    token_hex = hex(amount_token_desired)[2:].zfill(64)
    eth_hex = hex(amount_eth_desired)[2:].zfill(64)
    
    transaction_data = f"0x9cd441da{token_hex}{eth_hex}"
    
    return transaction_data

def get_gas_price(w3):
    """Get current gas price with a small multiplier"""
    try:
        gas_price = w3.eth.gas_price
        return int(gas_price * 1.1)
    except:
        return w3.to_wei('1.2', 'gwei')

def get_giwa_balance(w3, address):
    """Get GIWA (ETH) balance"""
    try:
        balance = w3.eth.get_balance(address)
        return balance
    except Exception as e:
        print(Fore.RED + f"Error getting balance: {e}")
        return 0

def get_indsr_balance(w3, address):
    """Get INDSR token balance"""
    try:
        data = '0x70a08231' + '000000000000000000000000' + address[2:].lower()
        
        result = w3.eth.call({
            'to': Web3.to_checksum_address(INDSR_TOKEN),
            'data': data
        })
        
        if result:
            return int(result.hex(), 16)
        return 0
    except Exception as e:
        print(Fore.YELLOW + f"Note: Could not get INDSR balance: {e}")
        return 0

def get_allowance(w3, owner_address, spender_address):
    """Get INDSR allowance for spender"""
    try:
        data = '0xdd62ed3e' + '000000000000000000000000' + owner_address[2:].lower() + '000000000000000000000000' + spender_address[2:].lower()
        
        result = w3.eth.call({
            'to': Web3.to_checksum_address(INDSR_TOKEN),
            'data': data
        })
        
        if result:
            return int(result.hex(), 16)
        return 0
    except Exception as e:
        print(Fore.YELLOW + f"Note: Could not get allowance: {e}")
        return 0

def get_expected_output(w3, amount_wei):
    """Get expected output amount for the swap"""
    try:
        ratio = decimal.Decimal('882.579')  
        expected_output = int(decimal.Decimal(amount_wei) * ratio / decimal.Decimal(10**18))
        
        print(Fore.CYAN + f"📈 Expected output: {expected_output} wei INDSR")
        return expected_output
        
    except Exception as e:
        print(Fore.YELLOW + f"⚠️ Could not get expected output: {e}")
        return int(decimal.Decimal(amount_wei) * decimal.Decimal('800') / decimal.Decimal(10**18))

def send_transaction(w3, tx, private_key, description):
    """Send a transaction and wait for confirmation"""
    try:
        signed_tx = w3.eth.account.sign_transaction(tx, private_key)
        print(Fore.YELLOW + f"✍️ {description} signed.")

        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        tx_hash_hex = w3.to_hex(tx_hash)
        print(Fore.CYAN + f"🚀 {description} sent! Hash: {tx_hash_hex}")

        print(Fore.YELLOW + f"⏳ Waiting for {description} confirmation...")
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120, poll_latency=2)

        explorer_url = f"{EXPLORER_URL}/tx/{tx_hash_hex}"
        
        if tx_receipt.status == 1:
            print(Style.BRIGHT + Fore.GREEN + f"✅ {description} SUCCESS!")
            return True, tx_hash_hex
        else:
            print(Style.BRIGHT + Fore.RED + f"❌ {description} FAILED!")
            try:
                w3.eth.call({
                    'from': tx['from'],
                    'to': tx['to'],
                    'value': tx.get('value', 0),
                    'data': tx.get('data', '0x'),
                    'gas': tx.get('gas', 200000),
                    'gasPrice': tx.get('gasPrice', w3.eth.gas_price)
                })
            except Exception as e:
                print(Fore.RED + f"📝 Revert reason: {e}")
            
            return False, tx_hash_hex
            
    except Exception as e:
        print(Style.BRIGHT + Fore.RED + f"🔥 Error in {description}: {e}")
        return False, None

def approve_indsr(w3, private_key, nonce):
    """Approve INDSR spending if needed"""
    account = w3.eth.account.from_key(private_key)
    my_address = account.address
    
    current_allowance = get_allowance(w3, my_address, SWAP_CONTRACT)
    if current_allowance > 0:
        print(Fore.CYAN + "✅ INDSR already approved, skipping approval")
        return True, nonce
    
    print(Fore.YELLOW + "⏳ Approving INDSR for spending...")
    
    approve_data = create_approve_data(SWAP_CONTRACT)
    
    gas_estimate = 70000  
    
    tx = {
        'chainId': CHAIN_ID,
        'from': my_address,
        'to': INDSR_TOKEN,
        'gas': gas_estimate,
        'gasPrice': get_gas_price(w3),
        'nonce': nonce,
        'data': approve_data
    }
    
    success, tx_hash = send_transaction(w3, tx, private_key, "Approval")
    if success:
        nonce += 1
        time.sleep(5)  
    
    return success, nonce

def add_liquidity(w3, private_key, indsr_amount, eth_amount, nonce):
    """Add liquidity to the pool"""
    account = w3.eth.account.from_key(private_key)
    my_address = account.address
    
    print(Fore.YELLOW + f"⏳ Adding liquidity: {w3.from_wei(eth_amount, 'ether')} ETH + {w3.from_wei(indsr_amount, 'ether')} INDSR")
    
    liquidity_data = create_add_liquidity_data(indsr_amount, eth_amount)
    
    gas_estimate = 200000  
    
    tx = {
        'chainId': CHAIN_ID,
        'from': my_address,
        'to': SWAP_CONTRACT,
        'gas': gas_estimate,
        'gasPrice': get_gas_price(w3),
        'nonce': nonce,
        'data': liquidity_data,
        'value': eth_amount
    }
    
    return send_transaction(w3, tx, private_key, "Add Liquidity")

def process_swap_and_liquidity(private_key):
    """Process swap and add liquidity"""
    try:
        w3 = Web3(Web3.HTTPProvider(RPC_URL))
        
        if not w3.is_connected():
            print(Fore.RED + "🚨 Failed to connect to RPC URL.")
            return False

        account = w3.eth.account.from_key(private_key)
        my_address = account.address
        print(Fore.YELLOW + f"🔑 Address: {my_address}")

        swap_amount_eth = decimal.Decimal(random.uniform(0.00001, 0.00002)).quantize(decimal.Decimal('0.00000001'))
        swap_amount_wei = int(swap_amount_eth * decimal.Decimal(10**18))
        
        print(Fore.CYAN + f"🎲 Random swap amount: {swap_amount_eth:.8f} ETH")
        
        balance = get_giwa_balance(w3, my_address)
        balance_eth = decimal.Decimal(balance) / decimal.Decimal(10**18)
        
        print(Fore.CYAN + f"💰 Current GIWA balance: {balance_eth:.6f} ETH")
        
        if balance < swap_amount_wei:
            print(Fore.RED + f"❌ Insufficient balance. Needed: {swap_amount_eth:.8f} ETH, Has: {balance_eth:.6f} ETH")
            return False

        nonce = w3.eth.get_transaction_count(my_address)
        print(Fore.CYAN + f"🔢 Nonce: {nonce}")

        expected_output = get_expected_output(w3, swap_amount_wei)
        amount_out_min = get_amount_out_min(expected_output, SLIPPAGE_TOLERANCE)
        
        swap_data = create_swap_data(amount_out_min, my_address)
        print(Fore.CYAN + "⚙️ Swap transaction data created successfully.")
        print(Fore.CYAN + f"📊 Amount out min: {amount_out_min} wei INDSR (with {SLIPPAGE_TOLERANCE}% slippage)")

        try:
            gas_estimate = w3.eth.estimate_gas({
                'from': my_address,
                'to': SWAP_CONTRACT,
                'value': swap_amount_wei,
                'data': swap_data
            })
            print(Fore.CYAN + f"⛽ Estimated gas for swap: {gas_estimate}")
        except Exception as e:
            print(Fore.YELLOW + f"⚠️ Could not estimate gas for swap, using default value: {e}")
            gas_estimate = 135783

        swap_tx = {
            'chainId': CHAIN_ID,
            'from': my_address,
            'to': SWAP_CONTRACT,
            'value': swap_amount_wei,
            'gas': gas_estimate,
            'gasPrice': get_gas_price(w3),
            'nonce': nonce,
            'data': swap_data
        }

        swap_success, swap_hash = send_transaction(w3, swap_tx, private_key, "Swap")
        if not swap_success:
            return False
        
        nonce += 1
        time.sleep(5)  
        
        indsr_balance = get_indsr_balance(w3, my_address)
        if indsr_balance == 0:
            print(Fore.RED + "❌ No INDSR received from swap")
            return False
        
        print(Fore.CYAN + f"💰 INDSR balance after swap: {w3.from_wei(indsr_balance, 'ether'):.8f} INDSR")
        
        approve_success, nonce = approve_indsr(w3, private_key, nonce)
        if not approve_success:
            return False

        eth_for_liquidity = min(swap_amount_wei // 10, indsr_balance * 10**18 // 880000000000000000)
        indsr_for_liquidity = indsr_balance
        
        print(Fore.CYAN + f"💧 Adding liquidity with: {w3.from_wei(eth_for_liquidity, 'ether'):.8f} ETH + {w3.from_wei(indsr_for_liquidity, 'ether'):.8f} INDSR")
        
        liquidity_success, liquidity_hash = add_liquidity(w3, private_key, indsr_for_liquidity, eth_for_liquidity, nonce)
        
        return liquidity_success

    except Exception as e:
        print(Style.BRIGHT + Fore.RED + f"🔥 Error occurred: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function to read file and run bot"""
    pk_file = 'privatekey.txt'
    if not os.path.exists(pk_file):
        print(Style.BRIGHT + Fore.RED + f"🚨 File '{pk_file}' not found! Please create it and fill with your private keys.")
        return

    with open(pk_file, 'r') as f:
        private_keys = [line.strip() for line in f if line.strip()]

    if not private_keys:
        print(Style.BRIGHT + Fore.RED + f"🚨 File '{pk_file}' is empty! Please fill with private keys.")
        return

    print(Style.BRIGHT + Fore.CYAN + f"✅ Found {len(private_keys)} wallets to process.")

    for i, pk in enumerate(private_keys, 1):
        print(Style.BRIGHT + Fore.MAGENTA + f"\n--- 💎 Processing Wallet #{i} of {len(private_keys)} ---")
        success = process_swap_and_liquidity(pk)
        
        if i < len(private_keys):
            print(Fore.CYAN + f"\n⏳ Waiting 15 seconds before next wallet...")
            time.sleep(15)
    
    print(Style.BRIGHT + Fore.GREEN + "\n🎉 All processes completed.")

if __name__ == "__main__":
    main()
