# -*- coding: utf-8 -*-
import numpy as np

def pivCalcVorticityFV(I,J,x,y,u,v,chc):
    
    dx = ( x[1,1] - x[0,0] ) / 1000
    dy = ( y[1,1] - y[0,0] ) / 1000
    
    ii = np.arange(1,I-1,1)
    jj = np.arange(1,J-1,1)
    
    gamma1 = + 0.5*dx*( u[np.ix_(ii-1,jj-1)] + 2*u[np.ix_(ii,jj-1)] + u[np.ix_(ii+1,jj-1)] ) \
             + 0.5*dy*( v[np.ix_(ii+1,jj-1)] + 2*v[np.ix_(ii+1,jj)] + v[np.ix_(ii+1,jj+1)] ) \
             - 0.5*dx*( u[np.ix_(ii+1,jj+1)] + 2*u[np.ix_(ii,jj+1)] + u[np.ix_(ii-1,jj+1)] ) \
             - 0.5*dy*( v[np.ix_(ii-1,jj+1)] + 2*v[np.ix_(ii-1,jj)] + v[np.ix_(ii-1,jj-1)] )
            
    gamma = np.zeros([I,J])
    gamma[np.ix_(ii,jj)] = gamma1
    
    vorticity = gamma / (4 * dx * dy)
    
    #   Boundaries
    #   Left Boundary
    vorticity[0,jj] = ((v[1,jj] - v[0,jj]) / dx) - (( u[0,jj+1] - u[0,jj-1]) / (2*dy))
    
    #   Right Boundary
    vorticity[I-1, jj] = ((v[I-1,jj] - v[I-2,jj])/dx) - ((u[I-1,jj+1] - u[I-1,jj-1]) / (2*dy))
    
    #   Bottom Boundary
    vorticity[ii,0] = (( v[ii+1,0] - v[ii-1,0] ) / (2*dx)) - (( u[ii,1] - u[ii,1] ) / dy);
    
    #   Top Boundary
    vorticity[ii,J-1] = (( v[ii+1,J-1] - v[ii-1,J-1] ) / (2*dx)) - (( u[ii,J-1] - u[ii,J-2] ) / dy);
    
    #   Corners
    #   Bottom Left
    vorticity[0,0] = (( v[1,0] - v[0,0] ) / dx) - (( u[0,1] - u[0,0] ) / dy);
    
    #   Bottom Right
    vorticity[I-1,0] = (( v[I-1,0] - v[I-2,0]) / dx) - (( u[I-1,1] - u[I-1,0]) / dy);
    
    #   Top Left
    vorticity[0,J-1] = ((v[1,J-1] - v[0,J-1] ) / dx) - (( u[0,J-1] - u[0,J-2] ) / dy);
    
    #   Top Right
    vorticity[I-1,J-1] = ((v[I-1,J-1] - v[I-2,J-1] ) / dx) - (( u[I-1,J-1] - u[I-1,J-2] ) / dy);
    
    #   Interior
    vorticityChoiceCode = np.ones([I,J],dtype=int)
    logic = np.zeros([I,J])
    logic[np.ix_(ii,jj)] =  (chc[np.ix_(ii-1,jj-1)]<1) + (chc[np.ix_(ii-1,jj)]<1)+(chc[np.ix_(ii-1,jj+1)]<1) + \
                    (chc[np.ix_(ii,jj-1)]<1) + (chc[np.ix_(ii,jj+1)]<1) + \
                    (chc[np.ix_(ii+1,jj-1)]<1) + (chc[np.ix_(ii+1,jj)]<1) + (chc[np.ix_(ii+1,jj+1)]<1)
    
    #   Left Boundary
    logic[0,jj] = logic[0,jj]+(chc[0,jj-1]<1)+(chc[0,jj]<1)+(chc[0,jj+1]<1)+(chc[1,jj]<1);
    
    #   Right Boundary
    logic[I-1,jj] = logic[I-1,jj]+(chc[I-1,jj-1]<1)+(chc[I-1,jj]<1)+(chc[I-1,jj+1]<1)+(chc[I-2,jj]<1);
    
    #   Bottom Boundary
    logic[ii,0] = logic[ii,0]+(chc[ii-1,0]<1)+(chc[ii,0]<1)+(chc[ii+1,0]<1)+(chc[ii,1]<1);
    
    #   Top Boundary
    logic[ii,J-1] = logic[ii,J-1]+(chc[ii-1,J-1]<1)+(chc[ii,J-1]<1)+(chc[ii+1,J-1]<1)+(chc[ii,J-2]<1);
    
    #   Corners
    #   Bottom Left
    logic[0,0] = logic[0,0]+(chc[0,0]<1)+(chc[0,1]<1)+(chc[1,0]<1);
    
    #   Bottom Right
    logic[I-1,0] = logic[I-1,0]+(chc[I-1,0]<1)+(chc[I-1,1]<1)+(chc[I-2,0]<1);
    
    #   Top Left
    logic[0,J-1] = logic[0,J-1]+(chc[0,J-1]<1)+(chc[1,J-1]<1)+(chc[0,J-2]<1);
    
    #   Top Right
    logic[I-1,J-1] = logic[I-1,J-1]+(chc[I-1,J-1]<1)+(chc[I-2,J-1]<1)+(chc[I-1,J-2]<1);
    
    vorticity[logic>0] = 0
    vorticityChoiceCode[logic>0] = 0
    return vorticity, vorticityChoiceCode