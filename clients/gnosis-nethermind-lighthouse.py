# Author: nodebridgeafrica.eth | nodebridge.africa
# License: GNU GPL
# Source: https://github.com/nodebridgeafrica/nodesynth
#
# Validator-Install: Standalone  Nethermind EL + Lighthouse CL
# Quickstart :: Minority Client :: Docker-free
#
# Made for home and solo stakers 🏠🥩
#
# Acknowledgments
# Validator-Install is branched from validator-install written by Accidental-green: https://github.com/accidental-green/validator-install
# The groundwork for this project was established through their previous efforts.

import os
from consolemenu import *
from consolemenu.items import *
import argparse
from utils import *

clear_screen()  # Call the function to clear the screen

NETWORKS = ["GNOSIS", "CHIADO", "GNOSIS_ARCHIVE"]
EXEC_CLIENTS = ["NETHERMIND"]
CONSENSUS_CLIENTS = ["LIGHTHOUSE"]

CHECKPOINTS = {
    "gnosis": "https://checkpoint.gnosischain.com/",
    "chiado": "https://checkpoint.chiadochain.net/",
    "gnosis_archive": "https://checkpoint.gnosischain.com/",
}



# Set options to parsed arguments
EL_LOG_LEVEL=os.getenv('EL_LOG_LEVEL', 'INFO')
EL_ENABLE_SNAPSYNC=os.getenv('EL_ENABLE_SNAPSYNC', False)
EL_RPC_PORT=os.getenv('EL_RPC_PORT', 8545)
EL_MODULES=os.getenv('EL_MODULES', '[Web3,Eth,Subscribe,Net]')
JWTSECRET_PATH=os.getenv('JWTSECRET_PATH')
EL_ENGINE_PORT=os.getenv('EL_ENGINE_PORT', 8551)
EL_P2P_PORT=os.getenv('EL_P2P_PORT', 30303)
EL_HEALTHCHECKS=os.getenv('EL_HEALTHCHECKS', False)
CL_HTTP_PORT=os.getenv("CL_HTTP_PORT", 4000)
CL_PORT=os.getenv("CL_PORT", 9000)

# Create argparse options
parser = argparse.ArgumentParser(description='Validator Install Options :: nodebridge.africa',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--network", type=str, help="Sets the Ethereum network", choices=NETWORKS, default='')
parser.add_argument("--el_log_level", type=str,help="Sets the Execution client's log level", default=EL_LOG_LEVEL)
parser.add_argument("--el_enable_snapsync", type=bool, help="Whether to enable snapSync on the Execution Client or not", default=EL_ENABLE_SNAPSYNC)
parser.add_argument("--el_rpc_port", type=int, help="Sets the Execution client's RPC port", default=EL_RPC_PORT)
parser.add_argument("--el_modules", type=str, help="Sets the modules to load in the Execution client", default=EL_MODULES)
parser.add_argument("--jwtsecret", type=str,help="Sets the jwtsecret file", default=JWTSECRET_PATH)
parser.add_argument("--el_engine_port", type=int, help="Sets the Execution client's Engine port", default=EL_ENGINE_PORT)
parser.add_argument("--el_p2p_port", type=int, help="Sets the Execution client's P2P port", default=EL_P2P_PORT)
parser.add_argument("--el_healthchecks", type=bool, help="Whether to enable healthcheck on the Execution client or not", default=EL_P2P_PORT)
parser.add_argument("--cl_http_port", type=int, help="Sets the Consensus clients HTTP port", default=CL_HTTP_PORT)
parser.add_argument("--cl_port", type=int, help="Sets the Consensus clients port", default=CL_PORT)
parser.add_argument("--skip_prompts", type=bool, help="Performs non-interactive installation. Skips any interactive prompts if set to true", default=False)

args = parser.parse_args()

# Change to the home folder
os.chdir(os.path.expanduser("~"))

network = select_network(
    args=args,
    networks=NETWORKS,
    subtitle='Installs Nethermind EL / LIGHTHOUSE CL\nSelect Gnosis network:'
)

execution_client = EXEC_CLIENTS[0].lower()
consensus_client = CONSENSUS_CLIENTS[0].lower()

pre_setup_client(args)
if execution_client == 'nethermind':
    nethermind_command_args = " ".join([
        f"--config={network}",
        "--datadir=/var/lib/nethermind",
        f"--log={args.el_log_level}",
        f"--Sync.SnapSync={args.el_enable_snapsync}",
        "--JsonRpc.Enabled=true",
        "--JsonRpc.Host=0.0.0.0",
        f"--JsonRpc.Port={args.el_rpc_port}",
        f"--JsonRpc.JwtSecretFile={args.jwtsecret}",
        "--JsonRpc.EngineHost=0.0.0.0",
        f"--JsonRpc.EnginePort={args.el_engine_port} ",
        f"--Network.DiscoveryPort={args.el_p2p_port} ",
        f"--HealthChecks.Enabled={args.el_healthchecks}",
        "--Pruning.CacheMb=2048",
        f"--JsonRpc.EnabledModules={args.el_modules}",
    ])
    nethermind_version, nethermind_service_file_path = download_and_install_nethermind(
        network=network,
        command_args=nethermind_command_args
    )

if consensus_client == 'lighthouse':
    if network.lower() == "gnosis_archive":
        network = "gnosis"

    lighthouse_command_args = " ".join([
        "beacon_node",
        f"--network={network}",
        "--disable-upnp",
        f"--datadir=/var/lib/lighthouse",
        f"--port={args.cl_port}",
        "--http",
        "--http-address=0.0.0.0",
        f"--http-port={args.cl_http_port}",
        f"--execution-endpoint=http://127.0.0.1:{args.el_engine_port}",
        f"--execution-jwt={args.jwtsecret}",
        f"--checkpoint-sync-url={CHECKPOINTS[network.lower()]}",
    ])
    lighthouse_version, lighthouse_service_file_path = download_and_install_lighthouse(
        network=network,
        command_args=lighthouse_command_args
    )
