#!/bin/bash

# Author: nodebridgeafrica.eth | nodebridge.africa
# License: GNU GPL
# Source: https://github.com/nodebridgeafrica/nodesynth
#
# Made for home and solo stakers 🏠🥩

# 🫶 Make improvements and suggestions on GitHub:
#    * https://github.com/nodebridgeafrica/nodesynth
# 🙌 Ask questions on Discord:
#    * https://discord.gg/dEpAVWgFNB

set -u

# enable  command completion
set -o history -o histexpand

abort() {
  printf "%s\n" "$1"
  exit 1
}

getc() {
  local save_state
  save_state=$(/bin/stty -g)
  /bin/stty raw -echo
  IFS= read -r -n 1 -d '' "$@"
  /bin/stty "$save_state"
}

exit_on_error() {
    exit_code=$1
    last_command="${@:2}"
    if [ $exit_code -ne 0 ]; then
        >&2 echo "\"${last_command}\" command failed with exit code ${exit_code}."
        exit $exit_code
    fi
}

wait_for_user() {
  local c
  echo
  echo "Press RETURN to continue or any other key to abort"
  getc c
  # we test for \r and \n because some stuff does \r instead
  if ! [[ "$c" == $'\r' || "$c" == $'\n' ]]; then
    exit 1
  fi
}

shell_join() {
  local arg
  printf "%s" "$1"
  shift
  for arg in "$@"; do
    printf " "
    printf "%s" "${arg// /\ }"
  done
}

# string formatters
if [[ -t 1 ]]; then
  tty_escape() { printf "\033[%sm" "$1"; }
else
  tty_escape() { :; }
fi
tty_mkbold() { tty_escape "1;$1"; }
tty_underline="$(tty_escape "4;39")"
tty_blue="$(tty_mkbold 34)"
tty_red="$(tty_mkbold 31)"
tty_bold="$(tty_mkbold 39)"
tty_reset="$(tty_escape 0)"

ohai() {
  printf "${tty_blue}==>${tty_bold} %s${tty_reset}\n" "$(shell_join "$@")"
}

requirements_check() {
  # Check CPU architecture
  if ! [[ $(lscpu | grep -oE 'x86') || $(lscpu | grep -oE 'aarch64') ]]; then
    echo "This machine's CPU architecture is not yet unsuppported."
    echo "Recommend using Intel-AMD x86 or arm64 systems for best experience."
    exit 1
  fi

  # Check operating system
  if ! [[ "$(uname)" == "Linux" ]]; then
    echo "This operating system is not yet unsuppported."
    echo "Recommend installing Ubuntu Desktop 24.04+ LTS or Ubuntu Server 24.04+ LTS for best experience."
    exit 1
  fi
}

linux_install_pre() {
    sudo apt-get update
    sudo apt-get install --no-install-recommends --no-install-suggests -y curl git ccze bc tmux jq nano btop whiptail ufw
    exit_on_error $?
}

linux_install_installer() {
    ohai "Cloning nodesynth into ~/git/nodesynth"
    mkdir -p ~/git/nodesynth
    git clone https://github.com/nodebridgeafrica/nodesynth.git ~/git/nodesynth/ 2> /dev/null || (cd ~/git/nodesynth ; git fetch origin main ; git checkout main ; git pull)
    chmod +x ~/git/nodesynth/*.sh
    ohai "Installing nodesynth"
    if [ -f /usr/local/bin/nodesynth ]; then 
      sudo rm /usr/local/bin/nodesynth
    fi
    sudo ln -s ~/git/nodesynth/nodesynth.sh /usr/local/bin/nodesynth
    exit_on_error $?
}

# Check OS and CPU requirements
requirements_check

# Do install.
OS="$(uname)"
if [[ "$OS" == "Linux" ]]; then
    echo """
███    ██  ██████  ██████  ███████ ███████ ██    ██ ███    ██ ████████ ██   ██ 
████   ██ ██    ██ ██   ██ ██      ██       ██  ██  ████   ██    ██    ██   ██ 
██ ██  ██ ██    ██ ██   ██ █████   ███████   ████   ██ ██  ██    ██    ███████ 
██  ██ ██ ██    ██ ██   ██ ██           ██    ██    ██  ██ ██    ██    ██   ██ 
██   ████  ██████  ██████  ███████ ███████    ██    ██   ████    ██    ██   ██ 
                                                          
                                   - Blockchain Nodes Made Easy
                                   - nodebridge.africa
    """
    ohai "This script will install a node management tool called 'nodesynth'"

    wait_for_user
    linux_install_pre
    linux_install_installer

    echo ""
    echo ""
    echo "######################################################################"
    echo "##                                                                  ##"
    echo "##           INSTALL COMPLETE - To run, type \"nodesynth\"            ##"
    echo "##                                                                  ##"
    echo "######################################################################"
    echo ""
    echo ""
fi
