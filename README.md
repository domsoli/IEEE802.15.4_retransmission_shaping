# Optimize-LR-WPAN-Retransmissions

This repository provides the code to replicate the experiments presented in the paper CITE or to perform analogous simulations with different datasets.

This code simulates the transmission between the nodes of a IEEE 802.15.4g-based network, and computes the PDR (packet delivery ratio) and RNP (required number of packets). For each packet transmission, the best SUN modulation is estimated by using a variety of algorithms (strategies).

## Code Organization
`/parameters.json` contains the parameters used to run the simulation; it allows to specify the specific nodes to use, the strategies to explore, the path of input and output files and a bunch of other parameters whose meaning is explained in the paper. Some of this parameters can also be specified manually when running the main file.

Folder `/simulation_strategies` contains a few scripts that can be run individually and simulate a specific strategy. They are just a simple wrap-around to the actual strategy simulation code and contain the default values for the required parameters.

Folder `/simulation_strategies/modules` stores the files defining the transmission strategies and the simulation procedure.

## Input Data
For each node XXXX in the network, the corresponding trace file should be stored in `/data/traces/pdr_phy_XXXX.txt`. Each row of the trace file should contain the time of the transmission attempt (not used), the width of the window used to compute the probability (not used), and the probability of a successful transmission for each SUN modulation (SUN-FSK, SUN-OQPSK, SUN-OFDM) separated by a TAB.
