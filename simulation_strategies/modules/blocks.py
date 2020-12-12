import os
import random

class Energy_allocator:

    """
    Keeps track of the number of transmission attempts done and stores
    the information about how many extra transmission could be done
    without exceeding the power constraint
    """

    def __init__(self, n_avg, n_max=9):
        # Define the average and maximum number of retries allowed
        self.n_avg = n_avg
        self.n_max = n_max
        # Init the counter of available extra transmissions
        self.n_extra = 0


    def get_tx_number(self):
        # Return the number of retransmission allowed for a specific packet
        return self.n_avg + min(self.n_max, self.n_extra)
        # return self.n_avg # To test the consistency of the new formulation


    def update(self, n_used):
        # Update the value of available extra transmissions
        self.n_extra += (self.n_avg - n_used)



class Transmission_simulator():

    def __init__(self, file_path):
        # Open the file stream (with read only permission???)
        self.file = open(file_path)
        # Initialize window size, number of transmission per window and pdr
        self.window_size = 0
        self.cont_window = 0
        self.pdr = {"FSK": 0, "OQPSK": 0, "OFDM": 0}
        # Indicates if the last transmission is succesful or not
        # and if the ACK has been received or not
        self.last_tx_status = {"pkt": False, "ack": False}
        # Indicates if the end of the trace file has been reached
        self.new_tx_available = True # Find a better name


    def update_pdr(self, verbose=False):

        """
        Update the pdr values for the three modulations as well as the value
        describing the window size. Return True if the update has been successful
        False otherwise.
        """

        # If the window size has not been reached, increase the window counter
        if self.cont_window < self.window_size:
            self.cont_window += 1

        # If the window size has been reached, get the next one
        else:
            # Restart the counter over the window
            self.cont_window = 0
            # if self.cont_window >= self.window_size:
            # Loop until the window size is small
            while True:

                # Read a new line from the input file
                line = self.file.readline() # Read the line
                ent = line.split('\t') # Parse values

                # Exit once the last line has been reached
                if len(ent) == 1:
                    self.new_tx_available = False
                    break

                # Get the new window size
                self.window_size = int(ent[1])
                # Get updated pdr values
                self.pdr = {"FSK": float(ent[2]),
                            "OQPSK": float(ent[3]),
                            "OFDM": float(ent[4])}

                # If the window size meets the requirements, break
                if self.window_size < 75:
                    break
                else:
                    if verbose:
                        print("Dropped window")

        if(verbose and self.new_tx_available):
            print("PDR FSK: ", self.pdr["FSK"])
            print("PDR OQPSK: ", self.pdr["OQPSK"])
            print("PDR OFDM", self.pdr["OFDM"])


    def transmit(self, modulation):

        """
        Given the channel transmission probability transmit the packet and the ACK.
        A transmission is considered to be succesful if the ACK is received.
        """

        # Find PDR corresponding to the selected modulation
        pdr_transmission = self.pdr[modulation]

        # Packet transmission attempt
        trial = random.random()
        # If packet has been delivered
        if(trial <= pdr_transmission):
            self.last_tx_status["pkt"] = True

            # Sending ACK
            trial = random.random()
            # If ACK has been received
            if(trial <= pdr_transmission):
                # The packet has been transmitted successfully
                self.last_tx_status["ack"] = True
            # If ACK has not been received
            else:
                # The packet has NOT been transmitted successfully
                self.last_tx_status["ack"] = False

        # If packet has NOT been delivered
        else:
            # The packet has NOT been transmitted successfully
            self.last_tx_status["pkt"] = False
            self.last_tx_status["ack"] = False



class Packet_counter():

    def __init__(self, max_retry, log_path, out_path):
        # Number of distinct packets, received ones and retransmitted ones
        self.counter = {"packet": 0, "received": 0, "retry": 0}
        self.pkt_counter = {"received": False, "retry": 0, "max_retry": max_retry}
        # Tell if the current transmission is the last one for the current packet
        self.end_pkt = False
        # Specify the output path of the log info and of final metrics
        self.log_path = log_path
        self.out_path = out_path


    def init_new_pkt(self):
        # Initialize the next packet
        self.counter["packet"] += 1
        self.pkt_counter["retry"] = 0
        self.pkt_counter["received"] = False
        self.end_pkt = False


    def update(self, tx_status):
        # Transmission attempt done
        self.counter["retry"] += 1
        self.pkt_counter["retry"] += 1

        # If the packet has been received for the first time
        if tx_status["pkt"] and self.pkt_counter["received"] == False:
            # Increase the number of received packets
            self.counter["received"] += 1
            # Flag the packet as received
            self.pkt_counter["received"] = True

        # If the ACK has been received
        if tx_status["ack"]:
            self.end_pkt = True
        # If the ACK has not been received
        else:
            # If this is the last retransmission
            if(self.pkt_counter["retry"] >= self.pkt_counter["max_retry"]):
                self.end_pkt = True


    def set_max_tx(self, max_tx):
        self.pkt_counter["max_retry"] = max_tx


    def print_log(self, modulation):
        """
        Print metrics on the log file (one row for each packet).
        Increase significantly the global running time!
        """
        if self.log_path:
            # If file is empty, print header
            if not os.path.exists(self.log_path):
                with open(self.log_path, "a+") as file:
                    line = "{}\t{}\t{}\n".format("a_phy", "PDR", "RNT")
                    file.write(line)
                    file.close()
            # Get partial metrics
            if self.counter["packet"] != 0:
                PDR = self.counter["received"]/self.counter["packet"]
                RNP = self.counter["retry"]/self.counter["packet"]
            else:
                PDR = None
                RNP = None
            # Format the line
            line = "{}\t{}\t{}\n".format(modulation, PDR, RNP)
            # Write on file
            with open(self.log_path, "a+") as file:
                file.write(line)
                file.close()


    # def print_log_PEWASUN(self, energy_allocator, packet_counter, modulation):
    #     """
    #     Print metrics on the log file (one row for each packet).
    #     Increase significantly the global running time!
    #     """
    #     if self.log_path:
    #         # If file is empty, print header
    #         if not os.path.exists(self.log_path):
    #             with open(self.log_path, "a+") as file:
    #                 line = "{}\t{}\t{}\t{}\t{}\n".format("a_phy", "PDR", "RNT", "n_extra", "n_used")
    #                 file.write(line)
    #                 file.close()
    #         # Get partial metrics
    #         if self.counter["packet"] != 0:
    #             PDR = self.counter["received"]/self.counter["packet"]
    #             RNP = self.counter["retry"]/self.counter["packet"]
    #         else:
    #             PDR = None
    #             RNP = None
    #         # Get extra metrics
    #         n_extra = energy_allocator.n_avg + min(energy_allocator.n_max, energy_allocator.n_extra)
    #         n_used = packet_counter.pkt_counter["retry"]
    #         # Format the line
    #         line = "{}\t{}\t{}\t{}\t{}\n".format(modulation, PDR, RNP, n_extra, n_used)
    #         # Write on file
    #         with open(self.log_path, "a+") as file:
    #             file.write(line)
    #             file.close()


    def print_metrics(self):
        """
        Print metrics on the output file (one row for each node-strategy-repetition combination)
        """
        PDR = self.counter["received"]/self.counter["packet"]
        RNP = self.counter["retry"]/self.counter["packet"]

        with open(self.out_path, "a+") as file:
            file.write(str(PDR)+"\t"+str(RNP)+"\n")

        return PDR, RNP
