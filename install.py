#!/usr/bin/env python3
"""
Installation script for the Shopping Assistant.

This script helps users install the required dependencies based on their preference.
"""

import os
import sys
import subprocess

def print_header():
    """Print the header."""
    print("\n" + "=" * 80)
    print("Shopping Assistant - Installation Script")
    print("=" * 80)

def print_footer():
    """Print the footer."""
    print("\n" + "=" * 80)
    print("Installation completed!")
    print("=" * 80 + "\n")

def install_dependencies(requirements_file):
    """
    Install dependencies from a requirements file.
    
    Args:
        requirements_file: Path to the requirements file
    """
    print(f"\nInstalling dependencies from {requirements_file}...")
    
    try:
        # Use pip to install dependencies
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
        print("Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {str(e)}")
        return False

def main():
    """Main function."""
    print_header()
    
    print("This script will help you install the required dependencies for the Shopping Assistant.")
    print("\nPlease choose an installation option:")
    print("1. Full Installation (all features)")
    print("2. Minimal Installation (basic features only)")
    
    choice = input("\nEnter your choice (1 or 2): ")
    
    if choice == "1":
        requirements_file = "requirements.txt"
        print("\nYou have chosen the Full Installation.")
        print("This will install all dependencies required for all features of the Shopping Assistant.")
    elif choice == "2":
        requirements_file = "requirements_minimal.txt"
        print("\nYou have chosen the Minimal Installation.")
        print("This will install only the basic dependencies required for the simple web interface.")
    else:
        print("\nInvalid choice. Please run the script again and enter 1 or 2.")
        return
    
    # Install dependencies
    success = install_dependencies(requirements_file)
    
    if success:
        print_footer()
        
        if choice == "1":
            print("You can now use all features of the Shopping Assistant:")
            print("- Command Line Interface: python main.py --product \"laptop\" --budget 50000")
            print("- Web Interface: python web_interface.py")
            print("- Simple Web Interface: python simple_web_interface.py")
        else:
            print("You can now use the basic features of the Shopping Assistant:")
            print("- Simple Web Interface: python simple_web_interface.py")
            print("\nNote: Some features may be limited with the minimal installation.")
    else:
        print("\nInstallation failed. Please try again or install dependencies manually:")
        print(f"pip install -r {requirements_file}")

if __name__ == "__main__":
    main()
