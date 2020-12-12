import random
import numpy as np


class EG():
    """
    Epsilon-Greedy modulation selection strategy
    """

    def __init__(self, eps, alpha):
        # constants
        self.eps = eps
        self.alpha = alpha
        # Expected values
        self.Q = {"FSK": 1, "OQPSK": 1, "OFDM": 1}


    def get_modulation(self):
        """
        Select the best modulation accordingly to the available knowledge of the system
        """
        # epsilon-greedy algorithm - modulation choice
        trial = random.random()
        if(trial > self.eps):
            # Greedy choice
            modulation = max(self.Q.items(), key=lambda x : x[1])[0]
        else:
            # Random choice
            modulation = random.choice(list(self.Q.keys()))

        return modulation


    def update(self, modulation, tx_status, **kwargs):
        """
        Update metrics on the basis of the received reward
        """
        reward = int(tx_status["ack"])
        # Update estimated values
        self.Q[modulation] += self.alpha*(reward - self.Q[modulation])



class BE():
    """
    Boltzmann Exploration (aka softmax) modulation selection strategy
    """

    def __init__(self, tau, alpha):
        # constants
        self.tau = tau
        self.alpha = alpha
        # Expected values
        self.Q = {"FSK": 1, "OQPSK": 1, "OFDM": 1}


    def get_modulation(self):
        """
        Select the best modulation accordingly to the available knowledge of the system
        """
        # Defines probabilities for each modulation
        boltzmann_p = [np.exp(self.Q[a]/self.tau) for a in self.Q.keys()]
        boltzmann_p = boltzmann_p/np.sum(boltzmann_p)
        # Extract a modulation from the probability
        modulation = np.random.choice(list(self.Q.keys()), p=boltzmann_p)

        return modulation


    def update(self, modulation, tx_status, **kwargs):
        """
        Update metrics on the basis of the received reward
        """
        reward = int(tx_status["ack"])
        # Update estimated values
        self.Q[modulation] += self.alpha*(reward - self.Q[modulation])



class DUCB():
    """
    Discounted Upper Confidence Bound modulation selection strategy
    """
    def __init__(self, gamma, xi, B):
        # constants
        self.gamma = gamma
        self.tau = xi
        self.B = B
        # Expected values
        self.Q = {"FSK": 1, "OQPSK": 1, "OFDM": 1}
        # Discounted number of used modulations
        self.N = {"FSK": 1, "OQPSK": 1, "OFDM": 1}


    def get_modulation(self):
        """
        Select the best modulation accordingly to the available knowledge of the system
        """
        P = {}

        # Sum of discounted modulation counts
        n = np.sum(list(self.N.values()))
        # Greedy choice
        for a in self.Q:
            # If the modulation has not been exploreed, chose it
            if self.N[a] == 0:
                P[a] = np.inf
            else:
                # Define the padding function
                c = np.sqrt(2*np.log(n)/self.N[a])
                # Define the probability of chosing a
                P[a] = self.Q[a] + c
        # Select the modulation maximizing P
        modulation = max(P.items(), key=lambda x : x[1])[0]

        return modulation


    def update(self, modulation, tx_status, **kwargs):
        """
        Update metrics on the basis of the received reward
        """
        reward = int(tx_status["ack"])
        for a in self.N:
            # Update the number of used modulations
            self.N[a] = self.gamma*self.N[a] + int(a == modulation)
            # Update estimated values
            self.Q[a] = self.gamma*self.Q[a] + reward*int(a == modulation)
