import random
import numpy as np

class ThreeM():
    """
    3M modulation selection strategy
    """

    def __init__(self, w, tau):
        # constants
        self.w = w
        self.tau = tau
        # Expected values
        self.A = {"FSK": [], "OQPSK": [], "OFDM": []}
        # "forbidden" modulation -> modulation failed in the last attemp
        self.a_bad = None


    def get_modulation(self):
        """
        Select the best modulation accordingly to the available knowledge of the system
        """
        ARR = {}
        # Defines probabilities for each modulation
        for a in self.A:
            # Check if the retrasmission has not failed in the last attempt
            if a != self.a_bad:
                # If a has never been explored, try it
                if len(self.A[a]) == 0:
                    return a
                # Compute the ARR over the window
                ARR[a] = np.mean(self.A[a])

        # Normalization factor
        P_den = sum([(1 + ARR[a])**self.w for a in ARR.keys()])
        # Compute P
        P = [(1 + ARR[a])**self.w / P_den for a in ARR.keys()]

        # Extract a modulation from the probability
        modulation = np.random.choice(list(ARR.keys()), p=P)

        return modulation


    def update(self, modulation, tx_status, **kwargs):
        """
        Update metrics on the basis of the received reward
        """
        # Insert the last value
        self.A[modulation].append(int(tx_status["ack"]))
        # Remove eldest stored value
        if len(self.A[modulation]) > self.tau:
            self.A[modulation].pop(0)

        # If transmission failed, return the "forbidden modulation"
        if tx_status["ack"] == 0:
            self.a_bad = modulation
        else:
            self.a_bad = None



class Rand():
    """
    Random modulation selection strategy
    """

    def __init__(self):
        # List of possible modulations
        self.modulations = ["FSK", "OQPSK", "OFDM"]


    def get_modulation(self):
        """
        Randomly select a modulation
        """
        return random.choice(self.modulations)


    def update(self, modulation, tx_status, **kwargs):
        """
        Nothing to be updated
        """
        pass



class Best():
    """
    SID - Understand how to merge this within the general MAB structure
    """

    def __init__(self):
        # PDR
        self.pdr = {"FSK": 1/3, "OQPSK": 1/3, "OFDM": 1/3}


    def get_modulation(self):
        """
        Select the modulation with highest pdr
        """
        return max(self.pdr.items(), key=lambda x : x[1])[0]


    def update(self, pdr, **kwargs):
        """
        Get new pdr values for the next transmission attempt
        """
        self.pdr = pdr
