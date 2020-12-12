# Dumb modulation selection streategy that always choose a random modulation
import os
import sys
import random
import argparse
import numpy as np
# Local application imports
from modules.MAB_strategies import BE
from modules.run_simulation import run_simulation


def main():

    # 1. Import constants
    parser = argparse.ArgumentParser()
    # Input and output file paths
    parser.add_argument('--in_path', type=str, required=True)
    parser.add_argument('--out_path', type=str, required=True)
    parser.add_argument('--log_path', type=str, default=None)
    # Average and maximum number of retries
    parser.add_argument('--avg_retry', type=int, default=3)
    parser.add_argument('--max_retry', type=int, default=9)
    # Verbose (int, can be 0 (False) or 1 (True))
    parser.add_argument('--verbose', type=int, default=0)
    # Parameters
    parser.add_argument('--alpha', type=float, default=0.1)
    parser.add_argument('--tau', type=float, default=0.1)

    args = parser.parse_args()

    if args.log_path:
        # Remove the output file if exists
        if os.path.exists(args.log_path):
            os.remove(args.log_path)

    # Initialize modulation selection strategy
    strategy = BE(args.tau, args.alpha)

    return run_simulation(args, strategy)



if __name__ == "__main__":
    main()
