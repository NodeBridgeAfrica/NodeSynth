# Author: nodebridgeafrica.eth | nodebridge.africa
# License: GNU GPL
# Source: https://github.com/nodebridgeafrica/nodesynth
#
# Validator-Install: Standalone Nimbus BN + Standalone Nimbus VC + Nethermind EL + MEVboost
# Quickstart :: Minority Client :: Docker-free
#
# Made for home and solo stakers 🏠🥩
#
# Acknowledgments
# Validator-Install is branched from validator-install written by Accidental-green: https://github.com/accidental-green/validator-install
# The groundwork for this project was established through their previous efforts.

import os
import requests
import random
import tarfile
import subprocess
import random
import sys
from consolemenu import *
from consolemenu.items import *
import argparse
from utils import *

import os

clear_screen()  # Call the function to clear the screen

# Valid configurations
valid_networks = ['MAINNET', 'HOLESKY', 'SEPOLIA']
valid_exec_clients = ['NETHERMIND']
valid_consensus_clients = ['NIMBUS']
valid_install_configs = ['Solo Staking Node', 'Full Node Only', 'Lido CSM Staking Node', 'Validator Client Only', 'Failover Staking Node']

# MEV Relay Data
mainnet_relay_options = [
    {'name': 'Aestus', 'url': 'https://0xa15b52576bcbf1072f4a011c0f99f9fb6c66f3e1ff321f11f461d15e31b1cb359caa092c71bbded0bae5b5ea401aab7e@aestus.live'},
    {'name': 'Agnostic Gnosis', 'url': 'https://0xa7ab7a996c8584251c8f925da3170bdfd6ebc75d50f5ddc4050a6fdc77f2a3b5fce2cc750d0865e05d7228af97d69561@agnostic-relay.net'},
    {'name': 'bloXroute Max Profit', 'url': 'https://0x8b5d2e73e2a3a55c6c87b8b6eb92e0149a125c852751db1422fa951e42a09b82c142c3ea98d0d9930b056a3bc9896b8f@bloxroute.max-profit.blxrbdn.com'},
    {'name': 'bloXroute Regulated', 'url': 'https://0xb0b07cd0abef743db4260b0ed50619cf6ad4d82064cb4fbec9d3ec530f7c5e6793d9f286c4e082c0244ffb9f2658fe88@bloxroute.regulated.blxrbdn.com'},
    {'name': 'Eden Network', 'url': 'https://0xb3ee7afcf27f1f1259ac1787876318c6584ee353097a50ed84f51a1f21a323b3736f271a895c7ce918c038e4265918be@relay.edennetwork.io'},
    {'name': 'Flashbots', 'url': 'https://0xac6e77dfe25ecd6110b8e780608cce0dab71fdd5ebea22a16c0205200f2f8e2e3ad3b71d3499c54ad14d6c21b41a37ae@boost-relay.flashbots.net'},
    {'name': 'Ultra Sound', 'url': 'https://0xa1559ace749633b997cb3fdacffb890aeebdb0f5a3b6aaa7eeeaf1a38af0a8fe88b9e4b1f61f236d2e64d95733327a62@relay.ultrasound.money'}
]

holesky_relay_options = [
    {'name': 'Aestus', 'url': 'https://0xab78bf8c781c58078c3beb5710c57940874dd96aef2835e7742c866b4c7c0406754376c2c8285a36c630346aa5c5f833@holesky.aestus.live'},
    {'name': 'Ultra Sound', 'url': 'https://0xb1559beef7b5ba3127485bbbb090362d9f497ba64e177ee2c8e7db74746306efad687f2cf8574e38d70067d40ef136dc@relay-stag.ultrasound.money'},
    {'name': 'Flashbots', 'url': 'https://0xafa4c6985aa049fb79dd37010438cfebeb0f2bd42b115b89dd678dab0670c1de38da0c4e9138c9290a398ecd9a0b3110@boost-relay-holesky.flashbots.net'},
    {'name': 'bloXroute', 'url': 'https://0x821f2a65afb70e7f2e820a925a9b4c80a159620582c1766b1b09729fec178b11ea22abb3a51f07b288be815a1a2ff516@bloxroute.holesky.blxrbdn.com'},
    {'name': 'Eden Network', 'url': 'https://0xb1d229d9c21298a87846c7022ebeef277dfc321fe674fa45312e20b5b6c400bfde9383f801848d7837ed5fc449083a12@relay-holesky.edennetwork.io'},
    {'name': 'Titan Relay', 'url': 'https://0xaa58208899c6105603b74396734a6263cc7d947f444f396a90f7b7d3e65d102aec7e5e5291b27e08d02c50a050825c2f@holesky.titanrelay.xyz'}
]

sepolia_relay_options = [
    {'name': 'Flashbots', 'url': 'https://0x845bd072b7cd566f02faeb0a4033ce9399e42839ced64e8b2adcfc859ed1e8e1a5a293336a49feac6d9a5edb779be53a@boost-relay-sepolia.flashbots.net'}
]

# Checkpoint-Sync Data
mainnet_sync_urls = [
    ("ETHSTAKER", "https://beaconstate.ethstaker.cc"),
    ("BEACONCHA.IN", "https://sync-mainnet.beaconcha.in"),
    ("ATTESTANT", "https://mainnet-checkpoint-sync.attestant.io"),
    ("SIGMA PRIME", "https://mainnet.checkpoint.sigp.io"),
    ("Lodestar", "https://beaconstate-mainnet.chainsafe.io"),
    ("BeaconState.info", "https://beaconstate.info"),
    ("PietjePuk", "https://checkpointz.pietjepuk.net"),
    ("invistools", "https://sync.invis.tools"),
    ("Nimbus", "http://testing.mainnet.beacon-api.nimbus.team"),
]

holesky_sync_urls = [
    ("ETHSTAKER", "https://holesky.beaconstate.ethstaker.cc"),
    ("BEACONSTATE", "https://holesky.beaconstate.info"),
    ("EF DevOps", "https://checkpoint-sync.holesky.ethpandaops.io"),
    ("Lodestar", "https://beaconstate-holesky.chainsafe.io"),
]

sepolia_sync_urls = [
    ("Beaconstate", "https://sepolia.beaconstate.info"),
    ("Lodestar", "https://beaconstate-sepolia.chainsafe.io"),
    ("EF DevOps", "https://checkpoint-sync.sepolia.ethpandaops.io"),
]


# Set options to parsed arguments
EL_P2P_PORT=os.getenv('EL_P2P_PORT')
EL_RPC_PORT=os.getenv('EL_RPC_PORT')
EL_MAX_PEER_COUNT=os.getenv('EL_MAX_PEER_COUNT')
CL_P2P_PORT=os.getenv('CL_P2P_PORT')
CL_REST_PORT=os.getenv('CL_REST_PORT')
CL_MAX_PEER_COUNT=os.getenv('CL_MAX_PEER_COUNT')
CL_IP_ADDRESS=os.getenv('CL_IP_ADDRESS')
JWTSECRET_PATH=os.getenv('JWTSECRET_PATH')
GRAFFITI=os.getenv('GRAFFITI')
FEE_RECIPIENT_ADDRESS=os.getenv('FEE_RECIPIENT_ADDRESS')
MEV_MIN_BID=os.getenv('MEV_MIN_BID')
CSM_FEE_RECIPIENT_ADDRESS=os.getenv('CSM_FEE_RECIPIENT_ADDRESS')
CSM_GRAFFITI=os.getenv('CSM_GRAFFITI')
CSM_MEV_MIN_BID=os.getenv('CSM_MEV_MIN_BID')
CSM_WITHDRAWAL_ADDRESS=os.getenv('CSM_WITHDRAWAL_ADDRESS')

# Create argparse options
parser = argparse.ArgumentParser(description='Validator Install Options :: nodebridge.africa',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--network", type=str, help="Sets the Ethereum network", choices=valid_networks, default="")
parser.add_argument("--jwtsecret", type=str,help="Sets the jwtsecret file", default=JWTSECRET_PATH)
parser.add_argument("--graffiti", type=str, help="Sets the validator graffiti message", default=GRAFFITI)
parser.add_argument("--fee_address", type=str, help="Sets the fee recipient address", default="")
parser.add_argument("--el_p2p_port", type=int, help="Sets the Execution Client's P2P Port", default=EL_P2P_PORT)
parser.add_argument("--el_rpc_port", type=int, help="Sets the Execution Client's RPC Port", default=EL_RPC_PORT)
parser.add_argument("--el_max_peers", type=int, help="Sets the Execution Client's max peer count", default=EL_MAX_PEER_COUNT)
parser.add_argument("--cl_p2p_port", type=int, help="Sets the Consensus Client's P2P Port", default=CL_P2P_PORT)
parser.add_argument("--cl_rest_port", type=int, help="Sets the Consensus Client's REST Port", default=CL_REST_PORT)
parser.add_argument("--cl_max_peers", type=int, help="Sets the Consensus Client's max peer count", default=CL_MAX_PEER_COUNT)
parser.add_argument("--vc_only_bn_address", type=str, help="Sets Validator Only configuration's (beacon node) IP address, e.g. http://192.168.1.123:5052")
parser.add_argument("--skip_prompts", type=str, help="Performs non-interactive installation. Skips any interactive prompts if set to true", default="")
parser.add_argument("--install_config", type=str, help="Sets the node installation configuration", choices=valid_install_configs, default="")
parser.add_argument("-v", "--version", action="version", version="%(prog)s 1.0.0")
args = parser.parse_args()
#print(args)

binary_arch=get_machine_architecture()
platform_arch=get_computer_platform()

# Change to the home folder
os.chdir(os.path.expanduser("~"))

eth_network = select_network(
    args=args,
    networks=valid_networks,
    subtitle='Installs Nethermind EL / Nimbus BN / Nimbus VC / MEVboost\nSelect Ethereum network:'
)

if not args.install_config and not args.skip_prompts:
    # Sepolia can only be full node
    if eth_network == "sepolia":
        install_config=valid_install_configs[1]
    else:
        # Ask the user for installation config
        index = SelectionMenu.get_selection(valid_install_configs,title='Validator Install Quickstart :: nodebridge.africa',subtitle='What type of installation would you like?\nSelect your type:',show_exit_option=False)
        # Set install configuration
        install_config=valid_install_configs[index]
else:
    install_config=args.install_config

if eth_network == "mainnet" and install_config == "Lido CSM Staking Node":
    print("Lido CSM is only available on HOLESKY. Mainnet not yet available.")
    exit(0)

# Sepolia is a permissioned validator set, default to NODE_ONLY
if eth_network == "sepolia":
    NODE_ONLY=True
    MEVBOOST_ENABLED=False
    VALIDATOR_ENABLED=False
    VALIDATOR_ONLY=False
else:
    match install_config:
       case "Solo Staking Node":
          NODE_ONLY=False
          MEVBOOST_ENABLED=True
          VALIDATOR_ENABLED=True
          VALIDATOR_ONLY=False
       case "Full Node Only":
          NODE_ONLY=True
          MEVBOOST_ENABLED=False
          VALIDATOR_ENABLED=False
          VALIDATOR_ONLY=False
       case "Lido CSM Staking Node":
          NODE_ONLY=False
          MEVBOOST_ENABLED=True
          VALIDATOR_ENABLED=True
          VALIDATOR_ONLY=False
          FEE_RECIPIENT_ADDRESS=CSM_FEE_RECIPIENT_ADDRESS
          GRAFFITI=CSM_GRAFFITI
          MEV_MIN_BID=CSM_MEV_MIN_BID
       case "Validator Client Only":
          NODE_ONLY=False
          MEVBOOST_ENABLED=True
          VALIDATOR_ENABLED=True
          VALIDATOR_ONLY=True
       case "Failover Staking Node":
          NODE_ONLY=False
          MEVBOOST_ENABLED=True
          VALIDATOR_ENABLED=False
          VALIDATOR_ONLY=False

execution_client=""
consensus_client=""

if not VALIDATOR_ONLY:
    # Set clients to nethermind
    execution_client = valid_exec_clients[0]
    execution_client = execution_client.lower()

# Set clients to nimbus
consensus_client = valid_consensus_clients[0]
# Set to lowercase
consensus_client = consensus_client.lower()


# Set FEE_RECIPIENT_ADDRESS
if not NODE_ONLY and FEE_RECIPIENT_ADDRESS == "" and not args.skip_prompts:
    # Prompt User for validator tips address
    while True:
        FEE_RECIPIENT_ADDRESS = Screen().input(f'Enter your Ethereum address (aka Fee Recipient Address)\n Hints: \n - Use ETH adddress from a hardware wallet.\n - Do not use an exchange address.\n > ')
        if is_valid_eth_address(FEE_RECIPIENT_ADDRESS):
            print("Valid Ethereum address")
            break
        else:
            print("Invalid Ethereum address. Try again.")

# Validates an CL beacon node address with port
def validate_beacon_node_address(ip_port):
    pattern = r"^(http|https|ws):\/\/((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(:?\d{1,5})?$"
    if re.match(pattern, ip_port):
        return True
    else:
        return False

BN_ADDRESS=""
# Set BN_ADDRESS
if VALIDATOR_ONLY and args.vc_only_bn_address is None and not args.skip_prompts:
    # Prompt User for beacon node address
    while True:
        BN_ADDRESS = Screen().input(f'\nEnter your consensus client (beacon node) address.\nExample: http://192.168.1.123:5052\n > ')
        if validate_beacon_node_address(BN_ADDRESS):
            print("Valid beacon node address")
            break
        else:
            print("Invalid beacon node address. Try again.")
else:
    BN_ADDRESS=args.vc_only_bn_address



if not args.skip_prompts:
    # Format confirmation message
    if install_config == "Solo Staking Node" or install_config == "Lido CSM Staking Node" or install_config == "Failover Staking Node":
        message=f'\nConfirmation: Verify your settings\n\nNetwork: {eth_network.upper()}\nInstallation configuration: {install_config}\nFee Recipient Address: {FEE_RECIPIENT_ADDRESS}\n\nIs this correct?'
    elif install_config == "Full Node Only":
        message=f'\nConfirmation: Verify your settings\n\nNetwork: {eth_network.upper()}\nInstallation configuration: {install_config}\n\nIs this correct?'
    elif install_config == "Validator Client Only":
        message=f'\nConfirmation: Verify your settings\n\nNetwork: {eth_network.upper()}\nInstallation configuration: {install_config}\nConsensus client (beacon node) address: {BN_ADDRESS}\n\nIs this correct?'
    else:
        print(f"\nError: Unknown install_config")
        exit(1)

    answer=PromptUtils(Screen()).prompt_for_yes_or_no(f'{message}')

    if not answer:
        file_name = os.path.basename(sys.argv[0])
        print(f'\nInstall cancelled by user. \n\nWhen ready, re-run install command:\npython3 {file_name}')
        exit(0)

# Initialize sync urls for selected network
if eth_network == "mainnet":
    sync_urls = mainnet_sync_urls
elif eth_network == "holesky":
    sync_urls = holesky_sync_urls
elif eth_network == "sepolia":
    sync_urls = sepolia_sync_urls

# Use a random sync url
sync_url = random.choice(sync_urls)[1]

if not VALIDATOR_ONLY:
    print(f'Using Sync URL: {sync_url}')


def install_mevboost():
    if MEVBOOST_ENABLED == True and not VALIDATOR_ONLY:
        # Step 1: Create mevboost service account
        os.system("sudo useradd --no-create-home --shell /bin/false mevboost")

        # Step 2: Install mevboost
        # Change to the home folder
        os.chdir(os.path.expanduser("~"))

        # Define the Github API endpoint to get the latest release
        url = 'https://api.github.com/repos/flashbots/mev-boost/releases/latest'

        # Send a GET request to the API endpoint
        response = requests.get(url)
        global mevboost_version
        mevboost_version = response.json()['tag_name']

        # Search for the asset with the name that ends in {platform_arch}_{binary_arch}.tar.gz
        assets = response.json()['assets']
        download_url = None
        for asset in assets:
            if asset['name'].endswith(f'{platform_arch.lower()}_{binary_arch}.tar.gz'):
                download_url = asset['browser_download_url']
                break

        if download_url is None:
            print("Error: Could not find the download URL for the latest release.")
            exit(1)

        try:
            # Download the file
            response = requests.get(download_url, stream=True)
            response.raise_for_status()  # Raise an exception for HTTP errors

            # Save the binary to the home folder
            with open("mev-boost.tar.gz", "wb") as f:
                for chunk in response.iter_content(1024):
                    if chunk:
                        f.write(chunk)

            print(f">> Successfully downloaded: {asset['name']}")

        except requests.exceptions.RequestException as e:
            print(f"Error: Unable to download file. Try again later. {e}")
            exit(1)

        # Extract the binary to the home folder
        with tarfile.open('mev-boost.tar.gz', 'r:gz') as tar:
            tar.extractall()

        # Move the binary to /usr/local/bin using sudo
        os.system(f"sudo mv mev-boost /usr/local/bin")

        # Remove files
        os.system(f"rm mev-boost.tar.gz LICENSE README.md")

        ##### MEV Boost Service File
        mev_boost_service_file_lines = [
        '[Unit]',
        f'Description=MEV-Boost Service for {eth_network.upper()}',
        'Wants=network-online.target',
        'After=network-online.target',
        'Documentation=https://www.nodebridge.africa',
        '',
        '[Service]',
        'User=mevboost',
        'Group=mevboost',
        'Type=simple',
        'Restart=always',
        'RestartSec=5',
        'ExecStart=/usr/local/bin/mev-boost \\',
        f'    -{eth_network} \\',
        f'    -min-bid {MEV_MIN_BID} \\',
        '    -relay-check \\',
        ]

        if eth_network == 'mainnet':
            relay_options=mainnet_relay_options
        elif eth_network == 'holesky':
            relay_options=holesky_relay_options
        else:
            relay_options=sepolia_relay_options

        for relay in relay_options:
            relay_line = f'    -relay {relay["url"]} \\'
            mev_boost_service_file_lines.append(relay_line)

        # Remove the trailing '\\' from the last relay line
        mev_boost_service_file_lines[-1] = mev_boost_service_file_lines[-1].rstrip(' \\')

        mev_boost_service_file_lines.extend([
            '',
            '[Install]',
            'WantedBy=multi-user.target',
        ])
        mev_boost_service_file = '\n'.join(mev_boost_service_file_lines)

        mev_boost_temp_file = 'mev_boost_temp.service'
        global mev_boost_service_file_path
        mev_boost_service_file_path = '/etc/systemd/system/mevboost.service'

        with open(mev_boost_temp_file, 'w') as f:
            f.write(mev_boost_service_file)

        os.system(f'sudo cp {mev_boost_temp_file} {mev_boost_service_file_path}')
        os.remove(mev_boost_temp_file)

def download_nimbus():
    if consensus_client == 'nimbus':
        # Change to the home folder
        os.chdir(os.path.expanduser("~"))

        # Define the Github API endpoint to get the latest release
        url = 'https://api.github.com/repos/status-im/nimbus-eth2/releases/latest'

        # Send a GET request to the API endpoint
        response = requests.get(url)
        global nimbus_version
        nimbus_version = response.json()['tag_name']

        # Adjust binary name
        if binary_arch == "amd64":
          _arch="amd64"
        elif binary_arch == "arm64":
          _arch="arm64v8"
        else:
           print("Error: Unknown binary architecture.")
           exit(1)

        # Search for the asset appropriate for this system architecture and platform
        assets = response.json()['assets']
        download_url = None
        for asset in assets:
            if f'_{platform_arch}_{_arch}' in asset['name'] and asset['name'].endswith('.tar.gz'):
                download_url = asset['browser_download_url']
                break

        if download_url is None:
            print("Error: Could not find the download URL for the latest release.")
            exit(1)

        # Download the latest release binary
        print(f"Download URL: {download_url}")

        try:
            # Download the file
            response = requests.get(download_url, stream=True)
            response.raise_for_status()  # Raise an exception for HTTP errors

            # Save the binary to the home folder
            with open("nimbus.tar.gz", "wb") as f:
                for chunk in response.iter_content(1024):
                    if chunk:
                        f.write(chunk)

            print(f">> Successfully downloaded: {asset['name']}")

        except requests.exceptions.RequestException as e:
            print(f"Error: Unable to download file. Try again later. {e}")
            exit(1)

        # Extract the binary to the home folder
        with tarfile.open('nimbus.tar.gz', 'r:gz') as tar:
            tar.extractall()

        # Find the extracted folder
        extracted_folder = None
        for item in os.listdir():
            if item.startswith(f'nimbus-eth2_{platform_arch}_{_arch}'):
                extracted_folder = item
                break

        if extracted_folder is None:
            print("Error: Could not find the extracted folder.")
            exit(1)

        # Copy the binary to /usr/local/bin using sudo
        os.system(f"sudo cp {extracted_folder}/build/nimbus_beacon_node /usr/local/bin")
        os.system(f"sudo cp {extracted_folder}/build/nimbus_validator_client /usr/local/bin")

        # Remove the nimbus.tar.gz file and extracted folder
        os.remove('nimbus.tar.gz')
        os.system(f"rm -r {extracted_folder}")

def install_nimbus():
    if consensus_client == 'nimbus' and not VALIDATOR_ONLY:
        # Create data paths, service user, assign ownership permissions
        subprocess.run(['sudo', 'mkdir', '-p', '/var/lib/nimbus'])
        subprocess.run(['sudo', 'chmod', '700', '/var/lib/nimbus'])
        subprocess.run(['sudo', 'useradd', '--no-create-home', '--shell', '/bin/false', 'consensus'])
        subprocess.run(['sudo', 'chown', '-R', 'consensus:consensus', '/var/lib/nimbus'])

        if MEVBOOST_ENABLED == True:
            _mevparameters='--payload-builder=true --payload-builder-url=http://127.0.0.1:18550'
        else:
            _mevparameters=''

        if VALIDATOR_ENABLED == True and FEE_RECIPIENT_ADDRESS:
            _feeparameters=f'--suggested-fee-recipient={FEE_RECIPIENT_ADDRESS}'
        else:
            _feeparameters=''

        ########### NIMBUS SERVICE FILE #############
        nimbus_service_file = f'''[Unit]
Description=Nimbus Beacon Node Consensus Client service for {eth_network.upper()}
Wants=network-online.target
After=network-online.target
Documentation=https://www.nodebridge.africa

[Service]
Type=simple
User=consensus
Group=consensus
Restart=on-failure
RestartSec=3
KillSignal=SIGINT
TimeoutStopSec=900
ExecStart=/usr/local/bin/nimbus_beacon_node --network={eth_network} --data-dir=/var/lib/nimbus --tcp-port={CL_P2P_PORT} --udp-port={CL_P2P_PORT} --max-peers={CL_MAX_PEER_COUNT} --rest-port={CL_REST_PORT} --enr-auto-update=true --web3-url=http://127.0.0.1:8551 --rest --metrics --metrics-port=8008 --jwt-secret={JWTSECRET_PATH} --non-interactive --status-bar=false --in-process-validators=false {_feeparameters} {_mevparameters}

[Install]
WantedBy=multi-user.target
'''
        nimbus_temp_file = 'consensus_temp.service'
        global nimbus_service_file_path
        nimbus_service_file_path = '/etc/systemd/system/consensus.service'

        with open(nimbus_temp_file, 'w') as f:
            f.write(nimbus_service_file)

        os.system(f'sudo cp {nimbus_temp_file} {nimbus_service_file_path}')
        os.remove(nimbus_temp_file)

def run_nimbus_checkpoint_sync():
    if sync_url is not None and not VALIDATOR_ONLY:
        print("Running Checkpoint Sync")
        db_path = "/var/lib/nimbus/db"
        os.system(f'sudo rm -rf {db_path}')
        subprocess.run([
            'sudo', '/usr/local/bin/nimbus_beacon_node', 'trustedNodeSync',
            f'--network={eth_network}', '--data-dir=/var/lib/nimbus',
            f'--trusted-node-url={sync_url}', '--backfill=false'
        ])
        os.system(f'sudo chown -R consensus:consensus {db_path}')

def install_nimbus_validator():
    if MEVBOOST_ENABLED == True:
        _mevparameters='--payload-builder=true'
    else:
        _mevparameters=''

    if VALIDATOR_ENABLED == True and FEE_RECIPIENT_ADDRESS:
        _feeparameters=f'--suggested-fee-recipient={FEE_RECIPIENT_ADDRESS}'
    else:
        _feeparameters=''

    if BN_ADDRESS:
        _beaconnodeparameters=f'--beacon-node={BN_ADDRESS}'
    else:
        _beaconnodeparameters=f'--beacon-node=http://{CL_IP_ADDRESS}:{CL_REST_PORT}'

    if consensus_client == 'nimbus' and VALIDATOR_ENABLED == True:
        # Create data paths, service user, assign ownership permissions
        subprocess.run(['sudo', 'mkdir', '-p', '/var/lib/nimbus_validator'])
        subprocess.run(['sudo', 'chmod', '700', '/var/lib/nimbus_validator'])
        subprocess.run(['sudo', 'useradd', '--no-create-home', '--shell', '/bin/false', 'validator'])
        subprocess.run(['sudo', 'chown', '-R', 'validator:validator', '/var/lib/nimbus_validator'])

        nimbus_validator_file = f'''[Unit]
Description=Nimbus Validator Client service for {eth_network.upper()}
Wants=network-online.target
After=network-online.target
Documentation=https://www.nodebridge.africa

[Service]
Type=simple
User=validator
Group=validator
Restart=on-failure
RestartSec=3
KillSignal=SIGINT
TimeoutStopSec=900
ExecStart=/usr/local/bin/nimbus_validator_client --data-dir=/var/lib/nimbus_validator --metrics --metrics-port=8009 --non-interactive --doppelganger-detection=off --graffiti={GRAFFITI} {_beaconnodeparameters} {_feeparameters} {_mevparameters}

[Install]
WantedBy=multi-user.target
'''
        nimbus_temp_file = 'validator_temp.service'
        global nimbus_validator_file_path
        nimbus_validator_file_path = '/etc/systemd/system/validator.service'

        with open(nimbus_temp_file, 'w') as f:
            f.write(nimbus_validator_file)

        os.system(f'sudo cp {nimbus_temp_file} {nimbus_validator_file_path}')
        os.remove(nimbus_temp_file)

def finish_install():
    # Reload the systemd daemon
    subprocess.run(['sudo', 'systemctl', 'daemon-reload'])

    print(f'##########################\n')
    print(f'## Installation Summary ##\n')
    print(f'##########################\n')

    print(f'Installation Configuration: \n{install_config}\n')

    if execution_client == 'nethermind':
        print(f'Nethermind Version: \n{nethermind_version}\n')

    if consensus_client == 'nimbus':
        print(f'Nimbus Version: \n{nimbus_version}\n')

    if MEVBOOST_ENABLED and not VALIDATOR_ONLY:
        print(f'Mevboost Version: \n{mevboost_version}\n')

    print(f'Network: {eth_network.upper()}\n')

    if not VALIDATOR_ONLY:
        print(f'CheckPointSyncURL: {sync_url}\n')

    if VALIDATOR_ONLY and BN_ADDRESS:
        print(f'Beacon Node Address: {BN_ADDRESS}\n')
        os.chdir(os.path.expanduser("~/git/nodesynth"))
        os.system(f'cp .env.overrides.example .env.overrides')

    if NODE_ONLY == False:
        print(f'Validator Fee Recipient Address: {FEE_RECIPIENT_ADDRESS}\n')

    print(f'Systemd service files created:')
    if not VALIDATOR_ONLY:
        print(f'\n{nimbus_service_file_path}\n{nethermind_service_file_path}')
    if VALIDATOR_ENABLED == True:
        print(f'{nimbus_validator_file_path}')
    if MEVBOOST_ENABLED == True and not VALIDATOR_ONLY:
        print(f'{mev_boost_service_file_path}')

    if args.skip_prompts:
        print(f'\nNon-interactive install successful! Skipped prompts.')
        exit(0)

    # Prompt to start services
    if not VALIDATOR_ONLY:
        answer=PromptUtils(Screen()).prompt_for_yes_or_no(f"\nInstallation successful!\nSyncing a Nimbus/Nethermind node for validator duties can be as quick as a few hours.\nWould you like to start syncing now?")
        if answer:
            os.system(f'sudo systemctl start execution consensus')
            if MEVBOOST_ENABLED == True:
                os.system(f'sudo systemctl start mevboost')

    answer=PromptUtils(Screen()).prompt_for_yes_or_no(f"\nConfigure node to autostart:\nWould you like this node to autostart when system boots up?")

    # Prompt to enable autostart services
    if answer:
        if not VALIDATOR_ONLY:
            os.system(f'sudo systemctl enable execution consensus')
        if VALIDATOR_ENABLED == True:
            os.system(f'sudo systemctl enable validator')
        if MEVBOOST_ENABLED == True and not VALIDATOR_ONLY:
            os.system(f'sudo systemctl enable mevboost')

    # Ask CSM staker if they to manage validator keystores
    if install_config == 'Lido CSM Staking Node':
        answer=PromptUtils(Screen()).prompt_for_yes_or_no(f"\nWould you like to generate or import new Lido CSM validator keys now?\nReminder: Set the Lido withdrawal address to: {CSM_WITHDRAWAL_ADDRESS}")
        if answer:
            os.chdir(os.path.expanduser("~/git/nodesynth"))
            command = './manage_validator_keys.sh'
            subprocess.run(command)

    # Ask solo staker if they to manage validator keystores
    if install_config == 'Solo Staking Node' or install_config == 'Validator Client Only':
        answer=PromptUtils(Screen()).prompt_for_yes_or_no(f"\nWould you like to generate or import validator keys now?\nIf not, resume at: nodesynth > Validator Client ")
        if answer:
            os.chdir(os.path.expanduser("~/git/nodesynth"))
            command = './manage_validator_keys.sh'
            subprocess.run(command)

    # Failover staking node reminders
    if install_config == 'Failover Staking Node':
        print(f'\nReminder for Failover Staking Node configurations:\n1. Consensus Client: Expose consensus client RPC port\n2. UFW Firewall: Update to allow incoming traffic on port {CL_REST_PORT}\n3. UFW firewall: Whitelist the validator(s) IP address.')

    # Validator Client Only overrides
    if install_config == 'Validator Client Only':
        answer=PromptUtils(Screen()).prompt_for_yes_or_no(f"Would you like update your EL/CL override settings now?\nYour validator client needs to know EL/CL settings.\nIf not, update later at\nNodeSynth > System Administration > Override environment variables.")
        if answer:
            command = ['nano', '~/git/nodesynth/.env.overrides']
            subprocess.run(command)


pre_setup_client(args, not VALIDATOR_ONLY)

install_mevboost()
if execution_client == 'nethermind':
    nethermind_version, nethermind_service_file_path = download_and_install_nethermind(
        network=eth_network,
        command_args=f'--config {eth_network} --datadir="/var/lib/nethermind" --Network.DiscoveryPort {EL_P2P_PORT} --Network.P2PPort {EL_P2P_PORT} --Network.MaxActivePeers {EL_MAX_PEER_COUNT} --JsonRpc.Port {EL_RPC_PORT} --Metrics.Enabled true --Metrics.ExposePort 6060 --JsonRpc.JwtSecretFile {JWTSECRET_PATH} --Pruning.Mode=Hybrid --Pruning.FullPruningTrigger=VolumeFreeSpace --Pruning.FullPruningThresholdMb=300000'
    )
download_nimbus()
install_nimbus()
run_nimbus_checkpoint_sync()
install_nimbus_validator()
finish_install()
