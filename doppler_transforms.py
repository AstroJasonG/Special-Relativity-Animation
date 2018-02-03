"""
Created on Fri Jan 12 11:27:40 2018

@author: jason
"""
import numpy as np

class Transform():
    def __init__(self, beta):
        self.beta = beta
        if self.beta > 1 or self.beta < -1:
            raise ValueError("Well that just exceeds the speed of light!")
        self.gamma = 1 / (1 - self.beta**2)**(1/2)
