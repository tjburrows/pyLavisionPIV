# -*- coding: utf-8 -*-
from ReadIM.extra import get_Buffer_andAttributeList as readimx, buffer_as_array, buffer_mask_as_array, att2dict
from ReadIM import DestroyBuffer, DestroyAttributeListSafe
import numpy as np

def extractUnits(attrib, rawString):
    scaleRaw = attrib[rawString]
    scale = np.zeros(2)
    ind1 = str.find(scaleRaw, ' ')
    ind2 = str.find(scaleRaw, '\n')
    scale[0] = float(scaleRaw[0 : ind1])
    scale[1] = float(scaleRaw[ind1 : ind2])
    ind3 = str.find(scaleRaw,'\n',ind2 + 1)
    return scaleRaw[(ind2 + 1) : ind3], scale

#   Combination of readimx and showimx_noplot functions
def pivReadIMX(filepath):
        
    buffer, attrib   = readimx(filepath)
    v_array, buffer  = buffer_as_array(buffer)
    mask, buffer     = buffer_mask_as_array(buffer)
    attrib2          = att2dict(attrib)
    
    #   Data dimensions
    nx = buffer.nx
    ny = buffer.ny
    nz = buffer.nz
    
    #    Set Data Range
    drngX = np.arange(0, nx) + 1
    drngY = np.arange(0, ny) + 1
    drngZ = np.arange(0, nz) + 1
    
    #   Extracting scales from attributes
    attributes={}
    attributes['UnitX'], scaleX = extractUnits(attrib2, '_SCALE_X')
    attributes['UnitY'], scaleY = extractUnits(attrib2, '_SCALE_Y')
    attributes['UnitZ'], scaleZ = extractUnits(attrib2, '_SCALE_Z')
    attributes['UnitI'], scaleI = extractUnits(attrib2, '_SCALE_I')
    
    #   Iniitialize lefthand size values
    lhs1 = (drngX - 0.5) * buffer.vectorGrid * scaleX[0] + scaleX[1] # x-range
    lhs2 = (drngY - 0.5) * buffer.vectorGrid * scaleY[0] + scaleY[1] # y-range
    lhs3 = 0
    lhs4 = 0
    lhs5 = 0
    lhs6 = 0
    lhs7 = 0
    
    Data = np.reshape(np.transpose(v_array,(2, 0, 1)), [nx, ny * np.size(v_array, 0)])
    
    itype = buffer.image_sub_type
    
    # Buffer Types:
    # 0: 'BUFFER_FORMAT_IMAGE',
    # 1: 'BUFFER_FORMAT_VECTOR_2D_EXTENDED',
    # 2: 'BUFFER_FORMAT_VECTOR_2D',
    # 3: 'BUFFER_FORMAT_VECTOR_2D_EXTENDED_PEAK',
    # 4: 'BUFFER_FORMAT_VECTOR_3D',
    # 5: 'BUFFER_FORMAT_VECTOR_3D_EXTENDED_PEAK'

    #   Grayvalue image format
    if itype <= 0: 
        lhs3 = Data[:, drngY - 1].T
        
    #   simple 2D vector format (vx,vy)
    elif itype == 2: 
        #   calculate vector position and components
        lhs1, lhs2 = np.meshgrid(lhs1, lhs2)
        lhs1 = lhs1.T
        lhs2 = lhs2.T
        lhs3 = Data[:, drngY - 1     ] * scaleI[0] + scaleI[1]
        lhs4 = Data[:, drngY + ny - 1] * scaleI[0] + scaleI[1]
        if scaleY[0] < 0:
            lhs4 = -lhs4
    
    #   normal 2D vector format + peak: sel+4*(vx,vy) (+peak)
    elif itype == 3 or itype == 1:    
        
        #   calculate vector position and components
        lhs1, lhs2 = np.meshgrid(lhs1, lhs2)
        lhs1 = lhs1.T
        lhs2 = lhs2.T
        lhs3 = lhs1 * 0
        lhs4 = lhs2 * 0
        
        #   Get choice code
        lhs5 = Data[:, drngY - 1]
        
        #   Build best vectors from choice field
        for i in range(0,6):
            mask = lhs5 == (i + 1)
            
            if i < 4:   #   get best vectors
                lhs3[mask] = Data[:, drngY + (2 * i + 1) * ny - 1][mask]
                lhs4[mask] = Data[:, drngY + (2 * i + 2) * ny - 1][mask]
                
            else:   #   get interpolated vectors
                lhs3[mask] = Data[:, drngY + 7 * ny - 1][mask]
                lhs4[mask] = Data[:, drngY + 8 * ny - 1][mask]
                
        lhs3 = lhs3 * scaleI[0] + scaleI[1]
        lhs4 = lhs4 * scaleI[0] + scaleI[1]
        
        if scaleY[0] < 0:
            lhs4 = -lhs4

    elif itype == 4:
        #   Calculate vector position and components
        lhs3 = drngZ-0.5 * buffer.vectorGrid    * scaleY[0] + scaleY[1]
        lhs4 = Data[:,drngY - 1]                * scaleI[0] + scaleI[1]
        lhs5 = Data[:,drngY + ny - 1]           * scaleI[0] + scaleI[1]
        lhs6 = Data[:, drngY + 2 * ny - 1]      * scaleI[0] + scaleI[1]
        lhs1, lhs2, lhs3 = np.meshgrid(lhs1, lhs2, lhs3)
        lhs1 = lhs1.T
        lhs2 = lhs2.T
        lhs3 = lhs3.T

    # stereo vector format
    elif itype == 5:
        lhs3 = (drngZ - 0.5) * buffer.vectorGrid * scaleZ[0] + scaleZ[1]
        lhs4 = np.zeros((nx, ny, nz))
        lhs5 = np.zeros((nx, ny, nz))
        lhs6 = np.zeros((nx, ny, nz))
        
        for iz in range(0 ,nz):
            pX = np.zeros((nx, ny))
            pY = np.zeros((nx, ny))
            pZ = np.zeros((nx, ny))
            pRange = drngY + (iz * 14 * ny) - 1
            
            #   Build best vectors from best choice field
            lhs7 = Data[:, pRange] # choice code
            
            # Loop over each possible choice code value
            for i in range(0,6):
                
                # Mask by current choice code value
                mask = (lhs7 == (i + 1))
                
                # If choice code = 1,2,3
                if i < 4:   #   Get best vectors
                    pX[mask] = Data[:, pRange + (3 * i + 1) * ny][mask]
                    pY[mask] = Data[:, pRange + (3 * i + 2) * ny][mask]
                    pZ[mask] = Data[:, pRange + (3 * i + 3) * ny][mask]
                    
                # If choice code = 5,6
                else:   #   get interpolated vectors
                    pX[mask] = Data[:, pRange + 10 * ny][mask]
                    pY[mask] = Data[:, pRange + 11 * ny][mask]
                    pZ[mask] = Data[:, pRange + 12 * ny][mask]
                    
            lhs4[:, :, iz] = pX
            lhs5[:, :, iz] = pY
            lhs6[:, :, iz] = pZ
        
        if scaleY[0] < 0:
            lhs5 = -lhs5
            
        lhs1, lhs2, lhs3 = np.meshgrid(lhs1, lhs2, lhs3)
        lhs1 = lhs1.T
        lhs2 = lhs2.T
        lhs3 = lhs3.T
        lhs4 = lhs4 * scaleI[0] + scaleI[1]
        lhs5 = lhs5 * scaleI[0] + scaleI[1]
        lhs6 = lhs6 * scaleI[0] + scaleI[1]
    
    
    DestroyBuffer(buffer)
    DestroyAttributeListSafe(attrib)
    del(buffer)
    del(attrib)
    
    return lhs1,lhs2,lhs3,lhs4,lhs5,lhs6,lhs7,attributes

