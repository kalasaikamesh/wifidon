#!/bin/bash

# Update system packages
echo "Updating system..."
sudo pacman -Syu --noconfirm

# Ensure yay is installed
if ! command -v yay &> /dev/null
then
    echo "Installing yay (AUR helper)..."
    sudo pacman -S --noconfirm yay
fi

# Install Kali tool categories
echo "Installing Kali Linux tool categories..."

# Common tool categories
yay -S --noconfirm kali-tools-top10 kali-tools-information-gathering kali-tools-password-attacks kali-tools-vulnerability kali-tools-web kali-tools-database kali-tools-exploitation kali-tools-forensics kali-tools-reporting kali-tools-reverse-engineering kali-tools-social-engineering kali-tools-wireless kali-tools-sniffing-spoofing kali-tools-post-exploitation kali-tools-privilege-escalation kali-tools-stego kali-tools-voip kali-tools-password-recovery kali-tools-windows-resources

# Install virtualization tools for running Kali instances or other VMs
echo "Installing virtualization tools (VirtualBox and QEMU)..."
sudo pacman -S --noconfirm virtualbox virtualbox-host-dkms qemu libvirt virt-manager

# Enable and start libvirt service
sudo systemctl enable libvirtd.service
sudo systemctl start libvirtd.service

# Install Docker for Kali Linux containers
echo "Installing Docker for isolated Kali Linux environments..."
sudo pacman -S --noconfirm docker
sudo systemctl start docker
sudo systemctl enable docker
sudo docker pull kalilinux/kali-rolling

# Install Linux headers and firmware (for better compatibility with wireless adapters)
echo "Installing Linux headers and firmware..."
sudo pacman -S --noconfirm linux-headers

# Completion message
echo "Installation of Kali Linux tools on Garuda Linux is complete!"