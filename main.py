import os
import sys
import time
import json
import random
import argparse
from statistics import stdev, mean

# Set random seed
random.seed(time.time)

# Parameters used in the current simulation
PARAMETERS_PATH = 'parameters.json'

## Initialize parameters
params = {}
# Load parameters
with open(PARAMETERS_PATH, 'r') as in_file:
    params = json.load(in_file)

## Load parameters stored in the json file
# Directory that contains all the strategy files
mod_path = params["strategies_path"]
# Sensors and strategies used
sensors = [sensor for sensor in params["sensors"].split()]
strategies = [strategy for strategy in params["strategies"].split()]
# Data folder path
input_path = params["input_path"]

## Load external parameters
parser = argparse.ArgumentParser(description='Run Simulation')

# Average and maximum number of retries allowed
parser.add_argument('--n_avg', type=int, default=int(params["avg_number_retries"]),
                    help='Average number of repetitions')
parser.add_argument('--n_max', type=int, default=int(params["max_number_retries"]),
                    help='Maximum number of extra repetitions')
# Number of replications to be made
parser.add_argument('--replications', type=int, default=int(params["replications"]),
                    help='Number of replications')
# Output folders
parser.add_argument('--out_name', type=str, default=params["out_name"],
                    help='Name of the output file')
parser.add_argument('--log_path', type=str, default=params["log_path"],
                    help='Folder to store log files')

# Define parameters
args = parser.parse_args()

avg_number_retries = args.n_avg
max_number_retries = args.n_max
replications = args.replications
# Output folder path
file_name = args.out_name
# Log folder path
log_path = args.log_path

### Set the output file
# Format the name of the output file
out_path = "{}_output_{}rep_{}rt.txt".format(file_name, replications, avg_number_retries)

# Remove the output file if exists
if os.path.exists(out_path):
  os.remove(out_path)

### Run the simulation
## Loops through sensors
for sensor in sensors:
    input_file = input_path+"pdr_phy_{}.txt".format(sensor)
    of = open(out_path, "a+")
    of.write(sensor+"\n")
    of.close()

    ## Loops through strategies
    for strategy in strategies:
        # Define the path to store log files
        if log_path:
            log_folder = log_path+strategy
            # Create folder to store sensor log files
            if not os.path.exists(log_folder):
                os.makedirs(log_folder)

        # Write strategy type on the output file
        of = open(out_path, "a+")
        of.write(strategy+"\n")
        of.close()

        ## Loops through replications
        for k in range(replications):
            # Define the command to run the single simulation
            command = "python {}{}.py".format(mod_path, strategy)
            parameters = "--in_path {} --out_path {} --avg_retry {} --max_retry {}".format(input_file,
                                                                                    out_path,
                                                                                    avg_number_retries,
                                                                                    max_number_retries)
            # Write the log file containing the transmission history
            if log_path:
                # Set the log file path
                log_file = "{}/{}_{}_{}.tsv".format(log_folder, strategy, sensor, k)
                # Remove the log file if already exists
                if os.path.exists(log_file):
                    os.remove(log_file)
                # Add to the call of the simulation the --log_path parameter
                parameters += (" --log_path {}".format(log_file))

            # Run the simulation
            print(command+" "+parameters)
            os.system(command+" "+parameters)
