import os
import time
import random

from .blocks import Energy_allocator, Transmission_simulator, Packet_counter

energy_policy = True

def run_simulation(args, strategy):

    # Initialize energy allocator
    # if energy_policy:
    #     energy_allocator = Energy_allocator(n_avg=args.avg_retry, n_max=9)
    # else:
    #     energy_allocator = args.avg_retry
    energy_allocator = Energy_allocator(n_avg=args.avg_retry, n_max=args.max_retry)

    # Initialize transmission simulator
    tx_simulator = Transmission_simulator(args.in_path)
    # Initialize packet counter
    packet_counter = Packet_counter(args.avg_retry, args.log_path, args.out_path)

    # Initialize the transmission probability for each modulation
    tx_simulator.update_pdr()

    # Loop until there is no more data available
    while tx_simulator.new_tx_available:

        # Select the maximum number of transmission attempts for the current packet
        if energy_policy:
            packet_counter.set_max_tx(max_tx=energy_allocator.get_tx_number())
        # Initialize the next packet
        packet_counter.init_new_pkt()

        # Loop until the last of the current packet transmissions
        while packet_counter.end_pkt == False:
            # Select modulation using a modulation selection strategy
            modulation = strategy.get_modulation()

            # Transmit the packet with selected modulation
            tx_simulator.transmit(modulation)
            # Update strategy
            strategy.update(modulation=modulation,
                            tx_status=tx_simulator.last_tx_status,
                            pdr=tx_simulator.pdr) # Only used by BEST strategy
            # Update packets counter
            packet_counter.update(tx_status=tx_simulator.last_tx_status)

        # Update energy allocator
        if energy_policy:
            energy_allocator.update(packet_counter.pkt_counter["retry"])
        # Update the log file
        if args.log_path:
            # update_log_file(args.log_path, modulation, packet_counter.counter)
            packet_counter.print_log(energy_allocator, packet_counter, modulation)
        # Update the transmission probability for the next packet
        tx_simulator.update_pdr()

    # Print metrics
    # print_metrics_on_file(args.out_path, packet_counter.counter)
    return packet_counter.print_metrics()



if __name__ == "__main__":
    run_simulation(strategy)
