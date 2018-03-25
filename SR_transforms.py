"""
SR_transforms.py
Relativistic transforms
@author: jason
dependencies: Numpy
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

    def PT(self, pos, d, side):
        """Transformation due to light travel time

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
                             + (y + d)**2 + z**2) ** (1/2))
        # Note: (y + d) not (y - d) because of awkward axes locations in
        # animate_shape.py
        return result
