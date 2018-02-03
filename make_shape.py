#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 30 12:02:51 2017

@author: jason
"""
import numpy as np

pos = np.array([[0, 0, 0], [0.5, 0, 0], [0, 0.5, 0], [0.5, 0.5, 0],
               [0, 0, 0.5], [0.5, 0, 0.5], [0, 0.5, 0.5], [0.5, 0.5, 0.5]])


class Make_shape():
    """Makes a 1, 2, 3D shape object from preset cube vertices
    """
    def __init__(self, dimension):
        self.dimension = dimension
        if self.dimension > 3 or self.dimension < 0:
            raise ValueError("how many space dimensions can we display? Not"
                             "the number you chose!")
        self.pos = np.array([[0, 0, 0], [0.5, 0, 0], [0, 0.5, 0],
                             [0.5, 0.5, 0], [0, 0, 0.5],
                             [0.5, 0, 0.5], [0, 0.5, 0.5], [0.5, 0.5, 0.5]])

    def verts(self):
        """picks out apprppriate number of vertices for a n-dimensional shape
        """
        if self.dimension == 1:
            verts = np.array([pos[0], pos[1]])
        elif self.dimension == 2:
            verts = np.array([pos[0], pos[1], pos[4], pos[5]])
        elif self.dimension == 3:
            verts = pos
        self.verts = verts
        return self.verts

    def frame(self, verts, N):
        """vertices to connect for wireframe shape
        needs to call self.verts before frame so that frame is updated
        along with verts.
        
        Parameters
        ----------
        verts : array of shape verticesr
        N     : number of points to produce for each line in frame
        
        Returns
        -------
        (dimension^2, N, 3) array
        """
        if verts is None:
            vert = self.verts
        else:
            vert = verts
        vec = np.empty((0, 2, 3))
        for u in range(len(vert)):
            for v in range(0, u):
                result = np.array([vert[u], vert[v]])
                vec = np.append(vec, [result], axis=0)

        fvec = np.empty((0, 2, 3))
        dif = np.empty((0, 3))
        for i in range(len(vec)):
            result = np.abs(vec[i][1] - vec[i][0])
            dif = np.append(dif, [result], axis=0)
            if np.count_nonzero(dif[i]) == 1:
                results = vec[i]
                fvec = np.append(fvec, [results], axis=0)
        
        X = np.empty((0, N))
        for d in range(len(fvec)):
            for k in range(len(fvec[d][0])):
                f = fvec[d][0][k]
                s = fvec[d][1][k]
                result = np.array([np.linspace(f, s, N)])
                X=np.append(X, result, axis=0)
                X2 = np.transpose(X)
        X3 = np.hsplit(X2, len(fvec))
        return X3

        
        
