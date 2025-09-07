#!/usr/bin/env python3
import os
import sys
import subprocess
import venv

def create_virtualenv(venv_path=".venv"):
    if not os.path.exists(venv_path):
        print(f"Creating virtual environment at {venv_path}...")
        venv.create(venv_path, with_pip=True)
        print("Virtual environment created.")
    else:
        print("Virtual environment already exists.")

def main():
    venv_path = ".venv"
    create_virtualenv(venv_path)

    print("Hello, World!")

if __name__ == "__main__":
    main()