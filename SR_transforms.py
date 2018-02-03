"""
Created on Fri Jan 12 11:27:40 2018

@author: jason
"""
import numpy as np


class Transform():
    """Produces appropriate transformations at given speed in
        3 dimensions, as well as transformations due to SR doppler
    """
    def __init__(self, beta):
        """ 
        Parameters
        ----------
        beta = (-1,1)
        """
        self.beta = beta
        if self.beta >= 1 or self.beta <= -1:
            raise ValueError("Well that just exceeds the speed of light!")

        self.gamma = 1 / (1 - self.beta**2)**(1/2)

    def LT(self):
        """Standard Lorrentz transformation

            Returns
            -------
            Lorrentz matrix : (4, 4) array
            beta            : scalar (-1,1)
            gamma           : scalar (inf, 1)
        """
        np.set_printoptions(precision=4)
        Lmatrix = np.array([[self.gamma, - self.gamma * self.beta, 0, 0],
                            [- self.gamma * self.beta, self.gamma, 0, 0],
                            [0, 0, 1.0, 0],
                            [0, 0, 0, 1.0]])
        return Lmatrix, self.beta, self.gamma

    def DT(self, pos, d, side):
        """Transformation due to SR Doppler || to motion

        Parameters
        ----------
        pos : (dimension^2, N, 3) array

        Returns
        -------
        """
        x = pos[side][:, 0]
        y = pos[side][:, 1]
        z = pos[side][:, 2]
        result = self.gamma*((x + self.beta * self.gamma * d) -
                             self.beta * ((x + self.beta * self.gamma * d)**2
                             + (y + d)**2 + z**2) ** (1/2))  # maybe should be
        # (y + d) and not (y - d)
        return result

    def DTslope(self, pos, d):

        x = pos[1][:, 0]
        y = pos[1][:, 1]
        z = pos[1][:, 2]

        result = (((x + self.beta * self.gamma * d) ** 2 + (y - d) ** 2 +
                       z ** 2) ** (1/2)) / (self.gamma * self.beta * 
                        (y - d) ** 2 + x * (((x + self.beta * self.gamma * d) ** 2) + (y - d) ** 2
                        + z ** 2) ** 2)
        return result
#    def DTx(self, pos)
#        """Transformation due to SR Doppler || to motion
#
#        Parameters
#        ----------
#        pos : (dimension^2, N, 3) array
#
#        Returns
#        -------
#        x : (N,) array (transformed)
#        """
#        x = pos[0][:, 0]
#        result = x * self.gamma * (1 - self.beta)
#        return result
#
#    def DTz(self, pos):
#        """Transformation due to SR Doppler z-dir
#
#        Parameters
#        ----------
#        pos : (N,) array
#        
#        returns
#        -------
#        x : (N,) array (transformed)
#        """
#        result_x = - self.gamma * self.beta * pos[1][:, 2]
#        return result_x
    
