from pivReadIMX import pivReadIMX
from pivCalcVorticityFV import pivCalcVorticityFV
from os.path import isdir,join,exists
from os import makedirs
import numpy as np
from pivIO import savePIV
import warnings

def processFile(filePath, is3D, instVort):            
    
    if not exists(filePath):
        raise ValueError('File %s doesn\'t exist!' % (filePath))
        
    if is3D:
        rawX, rawY, rawZ, rawU, rawV, rawW, rawCHC, attributes = pivReadIMX(filePath)
        rawX = np.squeeze(rawX)
        rawY = np.squeeze(rawY)
        rawZ = np.squeeze(rawZ)
        rawU = np.squeeze(rawU)
        rawV = np.squeeze(rawV)
        rawW = np.squeeze(rawW)
        rawCHC = np.squeeze(rawCHC)
    else:
        rawX, rawY, rawU, rawV, rawCHC, _, _, attributes = pivReadIMX(filePath)
        
    # Initialize 
    I        = np.size(rawX,0)
    J        = np.size(rawX,1)
    x        = np.flip(rawX,1)
    y        = np.flip(rawY,1)
    sourceFile = filePath
    u = np.flip(rawU,1)
    v = np.flip(rawV,1)
    chc = np.flip(rawCHC,1)
    
    if is3D:
        w = np.flip(rawW, 1)
        vmag = np.sqrt(u ** 2 + v ** 2 + w ** 2)
    else:
        vmag = np.sqrt(u ** 2 + v ** 2)
        
    if instVort==1:
        vort, vortCHC = pivCalcVorticityFV(I, J, x, y, u, v, chc)
        
    elif instVort != 0:
        raise ValueError('instvort must be 0 or 1 to toggle instantaneous vorticity')
    
    

def pivCalcInstAndAvg(cfgData, instvort):
    is3D = cfgData['is3D']
    lens = len(cfgData['sets'])
    
    if not isdir(cfgData['savePath']):
        makedirs(cfgData['savePath'])
    
    #   Loop over sets
    for i in range(0,lens):
        
        # Current set information
        currentSet = cfgData['sets'][i]
        currentNumFiles = cfgData['numFiles'][i];
        currentFolder = cfgData['setPath'][i]
        
        print('Processing Set %d/%d: %s ... ' % (i+1, lens, currentSet))
        
        # Initialize vecData dictionary
        vecData={}
        vecData['sourceFiles'] = list()
        vecData['units'] = {}
        
        #   Loop over files
        for j in range(0,currentNumFiles):
            print("Processing Frame %d/%d" % (j+1, currentNumFiles))
            
            # current file path
            fileName = 'B%05d.%s' % (j+1, cfgData['pivExtension'])
            filePath = join(currentFolder,fileName)
            
            if not exists(filePath):
                raise ValueError('File %s doesn\'t exist!' % (filePath))
                
            if is3D:
                rawX, rawY, rawZ, rawU, rawV, rawW, rawCHC, attributes = pivReadIMX(filePath)
                rawX = np.squeeze(rawX)
                rawY = np.squeeze(rawY)
                rawZ = np.squeeze(rawZ)
                rawU = np.squeeze(rawU)
                rawV = np.squeeze(rawV)
                rawW = np.squeeze(rawW)
                rawCHC = np.squeeze(rawCHC)
            else:
                rawX, rawY, rawU, rawV, rawCHC, _, _, attributes = pivReadIMX(filePath)
                
            # Initialize 
            if j == 0:
                vecData['units']['x'] = attributes['UnitX']
                vecData['units']['y'] = attributes['UnitY']
                vecData['units']['u'] = attributes['UnitI']
                    
                vecData['I']        = np.size(rawX,0)
                vecData['J']        = np.size(rawX,1)
                vecSize = (currentNumFiles, vecData['I'], vecData['J'])
                
                vecData['x']        = np.flip(rawX,1)
                vecData['y']        = np.flip(rawY,1)
                vecData['u']        = np.zeros(vecSize)
                vecData['v']        = np.zeros(vecSize)
                vecData['chc']      = np.zeros(vecSize)
                vecData['vmag']     = np.zeros(vecSize)
                
                if is3D:
                    vecData['w']    = np.zeros(vecSize)
                    vecData['z']    = np.flip(rawZ,1)
                    
                if instvort==1:
                    vecData['vort']     = np.zeros(vecSize)
                    vecData['chcVort'] = np.zeros(vecSize)
                    
            vecData['sourceFiles'].append(filePath)    
            vecData['u'][j,:] = np.flip(rawU,1)
            vecData['v'][j,:] = np.flip(rawV,1)
            vecData['chc'][j,:] = np.flip(rawCHC,1)
            
            if is3D:
                vecData['w'][j,:] = np.flip(rawW, 1)
                vecData['vmag'][j, :] = np.sqrt(vecData['u'][j, :] ** 2 + vecData['v'][j, :] ** 2 + vecData['w'][j, :] ** 2)
            else:
                vecData['vmag'][j, :] = np.sqrt(vecData['u'][j, :] ** 2 + vecData['v'][j, :] ** 2)
                
            if instvort==1:
                vecDataVort, vecDataVortCHC = pivCalcVorticityFV(vecData['I'], vecData['J'], vecData['x'], vecData['y'], vecData['u'][j, :], vecData['v'][j, :], vecData['chc'][j, :])
                vecData['vort'][j, :]      = vecDataVort
                vecData['chcvort'][j, :]  = vecDataVortCHC
                
            elif instvort != 0:
                raise ValueError('instvort must be 0 or 1 to toggle instantaneous vorticity')
                
        pathVecData = join(cfgData['savePath'], currentSet + '.pkl')
        
        print('DONE\nSaving %s...' % pathVecData, end='')
        
        savePIV(vecData, pathVecData)
        
        print('DONE\nAveraging...',end='')
        pivCalcAvg(cfgData, vecData, currentSet)
        
        print('DONE')


def pivCalcAvg(cfgData, vecData, currentSet):
    is3D = cfgData['is3D']
    I = vecData['I']
    J = vecData['J'] 
    
    #   Initialize avgData dictionary
    avgData = {}
    avgData['I']            = I
    avgData['J']            = J
    avgData['firstFile']    = vecData['sourceFiles'][0]
    avgData['units']        = vecData['units']
    avgData['x']            = vecData['x']
    avgData['y']            = vecData['y']
    avgData['div']          = np.sum(vecData['chc'] > 0, axis=0)
    avgData['chc']          = np.greater(avgData['div'], 0, dtype=int)
    
    u = vecData['u']
    v = vecData['v']
    
    # Set bad values to nan
    # This might modify vecData but it is okay because vecData has already beens saved to disk
    u[vecData['chc'] == 0] = np.nan
    v[vecData['chc'] == 0] = np.nan
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        
        # NaN mean velocities
        avgData['u'] = np.nanmean(u, axis=0)
        avgData['v'] = np.nanmean(v, axis=0)
        
        # Calculate fluctuations
        uPrime = vecData['u'] - avgData['u']
        vPrime = vecData['v'] - avgData['v']
        
        # Calculate Reynolds stresses
        avgData['uu'] = np.nanmean(uPrime**2, axis=0)
        avgData['vv'] = np.nanmean(vPrime**2, axis=0)
        avgData['uv'] = np.nanmean(uPrime * vPrime, axis=0)
        
        # Calculate RMS
        avgData['urms'] = np.sqrt(avgData['uu'])
        avgData['vrms'] = np.sqrt(avgData['vv'])
        
        #   Calculate vorticity
        avgData['vort'], avgData['chcvort'] = pivCalcVorticityFV(I, J, avgData['x'], avgData['y'], avgData['u'], avgData['v'], avgData['chc'])
        
        if is3D:
            
            # Average W
            w = vecData['w']
            w[vecData['chc'] == 0] = np.nan
            avgData['w'] = np.nanmean(w, axis=0)
            
            # W fluctuations
            wPrime = vecData['w'] - avgData['w']
            
            # W Reynolds stresses
            avgData['ww'] = np.nanmean(wPrime**2, axis=0)
            avgData['uw'] = np.nanmean(uPrime * wPrime, axis=0)
            avgData['vw'] = np.nanmean(vPrime * wPrime, axis=0)
            
            avgData['tke']   = 0.5 * (avgData['uu'] + avgData['vv'] + avgData['ww'])
            avgData['vmag'] = np.sqrt(avgData['u'] ** 2 + avgData['v'] ** 2 + avgData['w'] ** 2)
            avgData['wrms'] = np.sqrt(avgData['ww'])
            
        else:
            
            avgData['tke']   = 0.5 * (avgData['uu'] + avgData['vv'])
            avgData['vmag'] = np.sqrt(avgData['u'] ** 2 + avgData['v'] ** 2)
    
    # Set NaNs to zeros
    for _, value in avgData.items():
        if np.shape(value) == (I, J):
            value[np.isnan(value)] = 0
    
    #   Save averaged data
    path_avgData = join(cfgData['savePath'], currentSet + '_avg.pkl')
    savePIV(avgData, path_avgData)