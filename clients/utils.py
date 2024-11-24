import os
import re
import subprocess
import tarfile
import tempfile
import zipfile
import requests
from consolemenu import *
from consolemenu.items import *


from dotenv import load_dotenv
import platform

def clear_screen():
    if os.name == 'posix':  # Unix-based systems (e.g., Linux, macOS)
        os.system('clear')
    elif os.name == 'nt':   # Windows
        os.system('cls')

current_dir = os.path.dirname(os.path.realpath(__file__))
# Load environment variables from env file
load_dotenv(os.path.join(current_dir, "..", "env"))

def get_machine_architecture():
  machine_arch=platform.machine()
  if machine_arch == "x86_64":
    return "amd64"
  elif machine_arch == "aarch64":
    return "arm64"
  else:
    print(f'Unsupported machine architecture: {machine_arch}')
    exit(1)

def get_computer_platform():
  platform_name=platform.system()
  if platform_name == "Linux":
    return platform_name
  else:
    print(f'Unsupported platform: {platform_name}')
    exit(1)

# Validates an eth address
def is_valid_eth_address(address):
    pattern = re.compile("^0x[a-fA-F0-9]{40}$")
    return bool(pattern.match(address))

def select_network(args, networks, subtitle):
    if not args.network and not args.skip_prompts:
        # Ask the user to select network
        index = SelectionMenu.get_selection(networks,title='Validator Install Quickstart :: nodebridge.africa',subtitle=subtitle)

        # Exit selected
        if index == 3:
            exit(0)

        # Set network
        network=networks[index]
        network=network.lower()
    else:
        network=args.network.lower()
    return network

def pre_setup_client(args, gen_jwt=True):
    if gen_jwt:
        # Create JWT directory
        subprocess.run([f'sudo mkdir -p $(dirname {args.jwtsecret})'], shell=True)

        # Generate random hex string and save to file
        rand_hex = subprocess.run(['openssl', 'rand', '-hex', '32'], stdout=subprocess.PIPE)
        subprocess.run([f'sudo tee {args.jwtsecret}'], input=rand_hex.stdout, stdout=subprocess.DEVNULL, shell=True)

    # Update and upgrade packages
    subprocess.run(['sudo', 'apt', '-y', '-qq', 'update'])
    subprocess.run(['sudo', 'apt', '-y', '-qq', 'upgrade'])

    # Autoremove packages
    subprocess.run(['sudo', 'apt', '-y', '-qq' , 'autoremove'])

    # Chrony timesync package
    subprocess.run(['sudo', 'apt', '-y', '-qq', 'install', 'chrony'])

def create_user_and_path(user_name, folder_name):
    user_name = user_name.lower()
    folder = f"/var/lib/{folder_name.lower()}"
    # Create User and directories
    subprocess.run(["sudo", "useradd", "--no-create-home", "--shell", "/bin/false", user_name])
    subprocess.run(["sudo", "mkdir", "-p", folder])
    subprocess.run(["sudo", "chown", "-R", f"{user_name}:{user_name}", folder])
    return folder

def install_client_from_github(name, url):
    binary_arch=get_machine_architecture()
    platform_arch=get_computer_platform()

    # Send a GET request to the API endpoint
    response = requests.get(url)
    version = response.json()['tag_name']

    # Adjust binary name, regex tested with nethermind and lighthouse
    if binary_arch == "amd64":
        pattern=re.compile(r"(?=.*linux.*)(^https:\/\/.*x(86_)?64.*(tar\.gz|zip)$)")
    elif binary_arch == "arm64":
        pattern=re.compile(r"(?=.*linux.*)(^https:\/\/.*(aarch64|arm64).*(tar\.gz|zip)$)")
    else:
        print("Error: Unknown binary architecture.")
        exit(1)

    # Search for the asset with the name that ends in {platform_arch}-{_arch}.zip
    assets = response.json()['assets']
    
    asset = next((asset for asset in assets if re.match(pattern, asset["browser_download_url"])))
    download_url = asset.get('browser_download_url')
    filename = asset.get('name', "")

    if download_url is None or filename is None:
        print("Error: Could not find the download URL for the latest release.")
        exit(1)

    suffix = None
    if filename.endswith(".zip"):
        suffix = ".zip"
    elif filename.endswith(".tar.gz"):
        suffix = ".tar.gz"
    else:
        print("Error: unrecognized archive format")
        exit(1)
    # Download the latest release binary
    print(f"Download URL: {download_url}")

    try:
        # Download the file
        response = requests.get(download_url, stream=True)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Save the binary to a temporary file
        with tempfile.NamedTemporaryFile('wb', suffix=suffix, delete=False) as temp_file:
            for chunk in response.iter_content(1024):
                if chunk:
                    temp_file.write(chunk)
            temp_path = temp_file.name

        print(f">> Successfully downloaded: {filename}")

    except requests.exceptions.RequestException as e:
        print(f"Error: Unable to download file. Try again later. {e}")
        exit(1)

    # Create a temporary directory for extraction
    with tempfile.TemporaryDirectory() as temp_dir:
        # Extract the binary to the temporary directory
        if suffix == '.zip':
            with zipfile.ZipFile(temp_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
        elif suffix == '.tar.gz':
            with tarfile.open(temp_path, 'r:gz') as tar_ref:
                tar_ref.extractall(temp_dir)
        else:
            raise Exception(f"Can't unarchive {temp_path}, not implemented")
        
        # Copy the contents of the temporary directory to install_path using sudo
        install_path = f"/usr/local/bin/{name}"
        subprocess.run(["sudo", "cp", "-a", f"{temp_dir}/.", install_path])

    # Remove the temporary archived file
    os.remove(temp_path)
    return version, install_path

def setup_client(install_path, user_path, client_name, client_type, network, command_args):
    valid_client_type = ["execution", "consensus", "validator"]
    if client_type not in valid_client_type:
        print(f"Invalid Client Type: {client_type}")
        exit(1)

    subprocess.run(["sudo", "chmod", "a+x", f"{install_path}/{client_name}"])
    subprocess.run(['sudo', 'chown', '-R', f'{client_type}:{client_type}', install_path])
    
        ##### NETHERMIND SERVICE FILE ###########
    client_service_file = f'''[Unit]
Description={client_name.title()} {client_type.title()} Layer Client service for {network.upper()}
After=network-online.target
Wants=network-online.target
Documentation=https://www.nodebridge.africa

[Service]
Type=simple
User={client_type}
Group={client_type}
Restart=on-failure
RestartSec=3
KillSignal=SIGINT
TimeoutStopSec=900
WorkingDirectory={user_path}
Environment="DOTNET_BUNDLE_EXTRACT_BASE_DIR={user_path}"
ExecStart={install_path}/{client_name} {command_args}

[Install]
WantedBy=multi-user.target
'''

    client_temp_file = f'{client_type}_temp.service'
    global client_service_file_path
    client_service_file_path = f'/etc/systemd/system/{client_type}.service'

    with open(client_temp_file, 'w') as f:
        f.write(client_service_file)

    os.system(f'sudo cp {client_temp_file} {client_service_file_path}')

    os.remove(client_temp_file)
    return client_service_file_path

def download_and_install_nethermind(network, command_args):

    client_name = "nethermind"
    client_type = "execution"
    user_path = create_user_and_path(user_name=client_type, folder_name=client_name)
    subprocess.run(["sudo", "apt-get", '-qq', "install", "libsnappy-dev", "libc6-dev", "libc6", "unzip", "-y"], check=True)

    # Define the Github API endpoint to get the latest release
    url = 'https://api.github.com/repos/NethermindEth/nethermind/releases/latest'

    # global nethermind_version
    nethermind_version, install_path = install_client_from_github(client_name, url)

    nethermind_service_file_path = setup_client(
        install_path=install_path,
        user_path=user_path,
        client_name=client_name,
        client_type=client_type,
        network=network,
        command_args=command_args
    )
    return nethermind_version, nethermind_service_file_path

def download_and_install_lighthouse(network, command_args):

    client_name = "lighthouse"
    client_type = "consensus"
    user_path = create_user_and_path(user_name="consensus", folder_name=client_name)

    url = "https://api.github.com/repos/sigp/lighthouse/releases/latest"
    
    lighthouse_version, install_path = install_client_from_github("lighthouse", url)
    lighthouse_service_file_path = setup_client(
        install_path=install_path,
        user_path=user_path,
        client_name=client_name,
        client_type=client_type,
        network=network,
        command_args=command_args
    )

    return lighthouse_version, lighthouse_service_file_path
