# Ideal modulation selection streategy that always choose the modulation with higher PDR
import os
import sys
import random
import argparse
# Local application imports
from modules.nonMAB_strategies import Rand
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

    args = parser.parse_args()

    if args.log_path:
        # Remove the output file if exists
        if os.path.exists(args.log_path):
            os.remove(args.log_path)

    # Initialize modulation selection strategy
    strategy = Rand()

    return run_simulation(args, strategy)


if __name__ == "__main__":
    main()
