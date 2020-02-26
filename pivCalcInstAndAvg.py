from pivReadIMX import pivReadIMX
from pivCalcVorticityFV import pivCalcVorticityFV
from os.path import isdir,join,exists
from os import makedirs
import numpy as np
from pivIO import savePIV
import warnings
from multiprocessing import RawArray
from multiprocessing import Pool

vecDataShared={}

def processFile(cfgData, i, j, instVort):    
    is3D = cfgData['is3D']
    currentFolder = cfgData['setPath'][i]
    
     # Current set information
    fileName = 'B%05d.%s' % (j+1, cfgData['pivExtension'])
    filePath = join(currentFolder,fileName)
    
    if not exists(filePath):
        raise ValueError('File %s doesn\'t exist!' % (filePath))
    
    print("Processing Frame %d" % (j+1))
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
    
    u = np.flip(rawU,1)
    v = np.flip(rawV,1)
    chc = np.flip(rawCHC,1)
    
    if is3D:
        w = np.flip(rawW, 1)
        wShared = np.frombuffer(vecDataShared['w']).reshape(vecDataShared['shape'])
        wShared[j,:] = w
        vmag = np.sqrt(u ** 2 + v ** 2 + w ** 2)
    else:
        vmag = np.sqrt(u ** 2 + v ** 2)
    
    vmagShared = np.frombuffer(vecDataShared['vmag']).reshape(vecDataShared['shape'])
    vmagShared[j,:] = vmag
    
    uShared = np.frombuffer(vecDataShared['u']).reshape(vecDataShared['shape'])
    uShared[j,:] = u
    
    vShared = np.frombuffer(vecDataShared['v']).reshape(vecDataShared['shape'])
    vShared[j,:] = v
    
    chcShared = np.frombuffer(vecDataShared['chc']).reshape(vecDataShared['shape'])
    chcShared[j,:] = chc
    
    if instVort:
        I = np.size(rawX,0)
        J = np.size(rawX,1)
        x = np.flip(rawX,1)
        y = np.flip(rawY,1)
        vort, chcvort = pivCalcVorticityFV(I, J, x, y, u, v, chc)
        
        vortShared = np.frombuffer(vecDataShared['vort']).reshape(vecDataShared['shape'])
        vortShared[j,:] = vort
        
        chcvortShared = np.frombuffer(vecDataShared['chcvort']).reshape(vecDataShared['shape'])
        chcvortShared[j,:] = chcvort

def init_worker(dictionary):
    if type(dictionary) == list:
        dictionary = dictionary[0]
    for key,val in dictionary.items():
        vecDataShared[key] = val
    
def pivCalcInstAndAvg(cfgData, instVort):
    
    if instVort != 0 and instVort != 1:
        raise ValueError('instVort must be 0 or 1 to toggle instantaneous vorticity')
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
        
        vecData['units'] = {}
        
        # First file setup
        fileName = 'B%05d.%s' % (1, cfgData['pivExtension'])
        filePath = join(currentFolder,fileName)
        rawX,rawY,rawZ, _, _, _, _, attributes = pivReadIMX(filePath)
        if is3D:
            rawX = np.squeeze(rawX)
            rawY = np.squeeze(rawY)
            rawZ = np.squeeze(rawZ)
        vecData['units']['x'] = attributes['UnitX']
        vecData['units']['y'] = attributes['UnitY']
        vecData['units']['u'] = attributes['UnitI']
        vecData['sourceFiles'] = [filePath]
        vecData['I']        = np.size(rawX,0)
        vecData['J']        = np.size(rawX,1)
        vecData['x']        = np.flip(rawX,1)
        vecData['y']        = np.flip(rawY,1)
        if is3D:
            vecData['z']    = np.flip(rawZ,1)
        
        vecShape = (currentNumFiles, vecData['I'], vecData['J'])
        vecSize = vecShape[0] * vecShape[1] * vecShape[2]
        
        if __name__ == 'pivCalcInstAndAvg':
            vecDataSharedLocal={}
            vecDataSharedLocal['shape']    = vecShape
            vecDataSharedLocal['u']        = RawArray('d',vecSize)
            vecDataSharedLocal['v']        = RawArray('d',vecSize)
            vecDataSharedLocal['chc']      = RawArray('d',vecSize)
            vecDataSharedLocal['vmag']     = RawArray('d',vecSize)
            
            if is3D:
                vecDataSharedLocal['w']    = RawArray('d',vecSize)
                
            if instVort==1:
                vecDataSharedLocal['vort']     = RawArray('d',vecSize)
                vecDataSharedLocal['chcvort']  = RawArray('d',vecSize)
            
            init_worker(vecDataSharedLocal)
            with Pool(initializer=init_worker, initargs=[vecDataSharedLocal]) as p:
                 p.starmap(processFile, zip([cfgData]*currentNumFiles, [i]*currentNumFiles, range(currentNumFiles), [instVort] * currentNumFiles))
    
                
            for key,val in vecDataShared.items():
                if not key == 'shape':
                    vecData[key] = np.frombuffer(val).reshape(vecDataShared['shape'])
        
            pathVecData = join(cfgData['savePath'], currentSet + '.pkl')
            
            print('DONE\nSaving %s...' % pathVecData, end='')
            
            savePIV(vecData, pathVecData)
            
            print('DONE\nAveraging...',end='')
            pivCalcAvg(cfgData, vecData, currentSet)
            
            print('DONE')

def atan(x1,x2):
    return np.arctan2(x1,x2) * (180.0/np.pi)


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
        
        # Calculate Angle
        avgData['yxangle'] = atan(avgData['v'], avgData['u'])
        
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
            
            # Calculate Angles
            avgData['zxangle'] = atan(avgData['w'], avgData['u'])
            avgData['zyangle'] = atan(avgData['w'], avgData['v'])
            
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