from os import listdir
from os.path import join

def pivCheckCfgData(cfgData):
    
    #   High Speed PIV
    if not 'isHspiv' in cfgData:
        cfgData['isHspiv'] = False
        
    #   Stereo PIV
    if not 'is3D' in cfgData:
        cfgData['is3D'] = False
    
    #   Normalize
    if not 'normalize' in cfgData:
        cfgData['normalize'] = False
    
    #   Vorticity Calculation Method (0 = FV, 1 = FD)
    if not 'vortMethod' in cfgData:
        cfgData['vortMethod'] = 0;
        
    #   Determine number of files
    cfgData['setPath'] = list()
    cfgData['numFiles'] = list()
    for i in range(0,len(cfgData['sets'])):
        setPath = join(r'/',cfgData['basePath'], cfgData['sets'][i], cfgData['pivPath'])
        numFiles = 0
        for file in listdir(setPath):
            if file.endswith(cfgData['pivExtension']):
                numFiles+=1
            if cfgData['numFilesLimit'] != 0 and numFiles == cfgData['numFilesLimit']:
                break
        if numFiles == 0:
            raise ValueError("Error: no .%s files in %s" % (cfgData['pivExtension'], setPath))
        cfgData['numFiles'].append(numFiles)
        cfgData['setPath'].append(setPath)
    return cfgData

