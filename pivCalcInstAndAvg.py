from pivReadIMX import pivReadIMX
from pivCalcVorticityFV import pivCalcVorticityFV
from os.path import isdir,join,exists
from os import makedirs
import numpy as np
from pivIO import savePIV

def pivCalcInstAndAvg(cfgData, instvort):
    is3D = cfgData['is3D']
    lens = len(cfgData['sets'])
    
    # Define variables based on number of dimensions
    if is3D:
        varList = ['u','v','w','vMag']
    else:
        varList = ['u','v','vMag']
    
    if not isdir(cfgData['savePath']):
        makedirs(cfgData['savePath'])
    
    #   Loop over sets
    for i in range(0,lens):
        
        # Current set information
        currentSet = cfgData['sets'][i]
        currentNumFiles = cfgData['numFiles'][i];
        currentFolder = cfgData['setPath'][i]
        
        print('Processing Set %d/%d: %s ... ' % (i+1, lens, currentSet),end='')
        
        # Initialize vecData dictionary
        vecData={}
        vecData['sourceFiles'] = list()
        vecData['units'] = {}
        
        #   Loop over files
        for j in range(0,currentNumFiles):
            print(j)
            # current file path
            fileName = 'B%05d.%s' % (j+1, cfgData['pivExtension'])
            filePath = join(currentFolder,fileName)
            
            if not exists(filePath):
                raise ValueError('File %s doesn\'t exist!' % (filePath))
                
            if is3D:
                rawX, rawY, rawZ, rawU, rawV, rawW, rawCHC, attributes = pivReadIMX(filePath)
            else:
                rawX, rawY, rawU, rawV, rawCHC, _, _, attributes = pivReadIMX(filePath)
                
            # Initialize 
            if i == 0 and j == 0:
                vecData['units']['x'] = attributes['UnitX']
                vecData['units']['y'] = attributes['UnitY']
                
                for i in range(0,len(varList)):
                    vecData['units'][varList[i]] = attributes['UnitI']
                    
                vecData['I']        = np.size(rawX,0)
                vecData['J']        = np.size(rawX,1)
                vecSize = [vecData['I'],vecData['J'],currentNumFiles]
                
                vecData['x']        = np.flip(rawX,1)
                vecData['y']        = np.flip(rawY,1)
                vecData['u']        = np.zeros(vecSize)
                vecData['v']        = np.zeros(vecSize)
                vecData['chc']      = np.zeros(vecSize)
                vecData['vMag']     = np.zeros(vecSize)
                
                if is3D:
                    vecData['w']    = np.zeros(vecSize)
                    vecData['z']    = np.flip(rawZ,1)
                    
                if instvort==1:
                    vecData['vort']     = np.zeros(vecSize)
                    vecData['chcVort'] = np.zeros(vecSize)
                    
            vecData['sourceFiles'].append(filePath)    
            vecData['u'][:,:,j] = np.flip(rawU,1)
            vecData['v'][:,:,j] = np.flip(rawV,1)
            vecData['chc'][:,:,j] = np.flip(rawCHC,1)
            
            if is3D:
                vecData['w'][:,:,j] = np.flip(rawW,1)
                vecData['z']        = np.flip(rawZ,1)
                vecData['vMag'][:,:,j] = np.sqrt(vecData['u'][:,:,j]**2 + vecData['v'][:,:,j]**2 + vecData['w'][:,:,j]**2)
            else:
                vecData['vMag'][:,:,j] = np.sqrt(vecData['u'][:,:,j]**2 + vecData['v'][:,:,j]**2)
                
            if instvort==1:
                vecDataVort, vecDataVortCHC = pivCalcVorticityFV(vecData['I'],vecData['J'],vecData['x'],vecData['y'],vecData['u'][:,:,j],vecData['v'][:,:,j],vecData['chc'][:,:,j])
                vecData['vort'][:,:,j]      = vecDataVort
                vecData['chcVort'][:,:,j]  = vecDataVortCHC
            elif instvort != 0:
                raise ValueError('instvort must be 0 or 1 to toggle instantaneous vorticity')
                
        pathVecData = join(cfgData['savePath'], currentSet + '.pkl')
        
        print('DONE\nSaving %s...' % pathVecData, end='')
        
        savePIV(vecData, pathVecData)
        
        print('DONE\nAveraging...',end='')
        pivCalcAvg(cfgData, vecData, currentSet, currentNumFiles)
        
        print('DONE')
        

def pivCalcAvg(cfgData, vecData, currentSet, currentNumFiles):
    is3D = cfgData['is3D']
    if is3D:
        varList = ['u','v','w','uu','vv','ww','uv','uw','vw']
    else:
        varList = ['u','v','uu','vv','uv']
    
    #   Load Instantaneous Data
    I = vecData['I']
    J = vecData['J']
    
    #   Initialize phase-average fields to zero
    avgdata = {}
    for var in varList:
        avgdata[var] = np.zeros([I,J])
    avgdata['div'] = np.zeros([I,J])
    
    #   Running sums    
    for nn in range(0,currentNumFiles):
        isGoodVector = (vecData['chc'][:,:,nn] != 0).astype(int)
        
        #    Mean Velocity
        avgdata['u'] += vecData['u'][:,:,nn] * isGoodVector
        avgdata['v'] += vecData['v'][:,:,nn] * isGoodVector
        if is3D:
            avgdata['w'] += vecData['w'][:,:,nn] * isGoodVector
        
        #    Second moments of velocity (these will be converted to Reynolds stresses later)
        avgdata['uu'] += vecData['u'][:,:,nn]**2 * isGoodVector
        avgdata['uv'] += vecData['u'][:,:,nn] * vecData['v'][:,:,nn] * isGoodVector
        avgdata['vv'] += vecData['v'][:,:,nn]**2 * isGoodVector
        if is3D:
            avgdata['uw'] += vecData['u'][:,:,nn] * vecData['w'][:,:,nn] * isGoodVector
            avgdata['vw'] += vecData['v'][:,:,nn] * vecData['w'][:,:,nn] * isGoodVector
            avgdata['ww'] += vecData['w'][:,:,nn**2] * isGoodVector
        avgdata['div'] += isGoodVector
        
    #   Divide
    divisorIsZero = avgdata['div'] == 0
    divisorIsNotZero = np.logical_not(divisorIsZero)
    for var in varList:
        avgdata[var][divisorIsNotZero] /= avgdata['div'][divisorIsNotZero]

    #    Convert second velocity moments to Reynolds stresses
    avgdata['uu'] -= avgdata['u']**2
    avgdata['vv'] -= avgdata['v']**2
    avgdata['uv'] -= avgdata['u']*avgdata['v']
    if is3D:
        avgdata['ww'] -= avgdata['w']**2
        avgdata['uw'] -= avgdata['u'] * avgdata['w']
        avgdata['vw'] -= avgdata['v'] * avgdata['w']
        
    #   Assume all files in set have the same grid (I, J, x, y) and units
    avgdata['I']            = I
    avgdata['J']            = J
    avgdata['firstFile']   = vecData['sourceFiles'][0]
    avgdata['units']        = vecData['units']
    avgdata['x']            = vecData['x']
    avgdata['y']            = vecData['y']
    avgdata['chc']          = divisorIsNotZero.astype(int)
    
    #   Calculate phase-averaged vorticity
    avgdata['vort'], avgdata['chcVort'] = pivCalcVorticityFV(I,J,avgdata['x'],avgdata['y'],avgdata['u'],avgdata['v'],avgdata['chc'])
    
    #   RMS & TKE
    avgdata['uRms'] = np.sqrt(avgdata['uu'])
    avgdata['vRms'] = np.sqrt(avgdata['vv'])
    avgdata['tke']   = 0.5 * (avgdata['uu'] + avgdata['vv'])
    
    #   Velocity magnitude
    if is3D:
        avgdata['vMag'] = np.sqrt(avgdata['u']**2 + avgdata['v']**2 + avgdata['w']**2)
    else:
        avgdata['vMag'] = np.sqrt(avgdata['u']**2 + avgdata['v']**2)
    
    #   Save phase-averaged data
    path_avgdata = join(cfgData['savePath'], currentSet + '_avg.pkl')
    savePIV(avgdata, path_avgdata)    