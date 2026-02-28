#!/usr/bin/env python
import sys
import subprocess

if __name__ == "__main__":
    sys.argv = ["streamlit", "run", "src/trader/dashboard.py"]
    subprocess.run(sys.argv)
