#!/usr/bin/env python3
import subprocess
import sys
import os

def main():
    # install deps
    subprocess.call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    # run CLI reconciliation
    subprocess.call([sys.executable, "reconciliation.py"])
    # launch UI
    subprocess.call([sys.executable, "-m", "streamlit", "run", "app.py"])

if __name__ == '__main__':
    main()