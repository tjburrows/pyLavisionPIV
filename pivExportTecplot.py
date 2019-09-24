import numpy as np
from os.path import join, isfile
from pivIO import loadPIV
from subprocess import check_output

def pivExportTecplot(cfgData, average, instantaneous):
    preplotPath =  cfgData['preplot'];
    
    if average:
        for currentSet in cfgData['sets']:
            avgPath = join(cfgData['savePath'], currentSet + '_avg.pkl')
            datPath = avgPath[:-3] + 'dat'
            print('Exporting %s ...' % (datPath),end='')
            pivTecWriteUniversalAvg(avgPath, datPath)
            print('DONE')
            print('Converting to Binary...', end='')
            if isfile(preplotPath):
                command = '"' + preplotPath + '" "' + datPath + '"'
                check_output(command)
            else:
                print("Warning: Tecplot file not converted to binary.  Invalid path to executable.")
                print(preplotPath)
            print('DONE')
            
    if instantaneous:
        instPath = join(cfgData['savePath'], currentSet + '.pkl')
        datPath = instPath[:-4] + '_inst.dat'
        print('Exporting %s ...' % (datPath),end='')
        pivTecWriteUniversalInst(instPath, datPath)
        print('DONE')
        print('Converting to Binary...', end='')
        if isfile(preplotPath):
            command = '"' + preplotPath + '" "' + datPath + '"'
            check_output(command)
        print('DONE')

            
def pivTecWriteUniversalAvg(avgPath, datPath):
    avgData = loadPIV(avgPath)
    I = avgData['I']
    J = avgData['J']
    N = I * J
    dontInclude = list()
    for key,_ in avgData.items():
        if not np.shape(avgData[key]) == (I,J):
            dontInclude.append(key)
    for string in dontInclude:
        if string in avgData:
            avgData.pop(string)
    temp = list(avgData.keys())
    V = len(temp)
    varList = ['x','y','u','v']
    for vn in range(0,V):
        if not temp[vn] in ['x','y','u','v']:
            varList.append(temp[vn])
    varNames = ''
    for ii in range(0,V-1):
        varNames += '"' + varList[ii] + '", '
    varNames += '"' + varList[V-1] + '"'
    headerString = 'TITLE="%s" VARIABLES= %s, ZONE T="%s" I=%d, J=%d F=POINT' % (avgPath, varNames, avgPath, I, J)
    for vn in range(0,V):
        avgData[varList[vn]] = np.reshape(avgData[varList[vn]].T,N)
    outData = np.zeros([N,V])
    for vn in range(0,V):
        outData[:,vn] = avgData[varList[vn]]
    with open(datPath, 'wb') as outfile:
        np.savetxt(outfile, outData, fmt='%f', delimiter = ', ', header = headerString, comments='')
        
def pivTecWriteUniversalInst(instPath, datPath):
    vecData = loadPIV(instPath)
    I = vecData['I']
    J = vecData['J']
    N = I * J
    frames = np.size(vecData['u'],2)
    dontInclude = list()
    for key,_ in vecData.items():
        if not (np.shape(vecData[key]) == (I,J,frames) or np.shape(vecData[key]) == (I,J)):
            dontInclude.append(key)
    for string in dontInclude:
        if string in vecData:
            vecData.pop(string)
    temp = list(vecData.keys())
    V = len(temp)
    varList = ['x','y','u','v']
    for vn in range(0,V):
        if not temp[vn] in ['x','y','u','v']:
            varList.append(temp[vn])
    varNames = ''
    for ii in range(0,V-1):
        varNames += '"' + varList[ii] + '", '
    varNames += '"' + varList[V-1] + '"'
    headerString = 'TITLE="%s" VARIABLES= %s, ZONE T="%s" I=%d, J=%d F=POINT' % (instPath[:-4]+'_0.dat', varNames, instPath[:-4]+'_0.dat', I, J)
    outDict = {}
    for ii in range(0,frames):
        for vn in range(0,V):
            if np.ndim(vecData[varList[vn]]) == 3:
                outDict[varList[vn]] = np.reshape(vecData[varList[vn]][:,:,ii].T,N)
            else:
                if ii == 0:
                    outDict[varList[vn]] = np.reshape(vecData[varList[vn]].T,N)
        outData = np.zeros([N,V])
        for vn in range(0,V):
            outData[:,vn] = outDict[varList[vn]]
        if ii == 0:
            with open(datPath, 'wb') as outfile:
                np.savetxt(outfile, outData, fmt='%f', delimiter = ', ', header = headerString, comments='')
        else:
            zoneString = '\nZONE T="%s" I=%d, J=%d F=POINT' % ( (instPath[:-4]+('_%d.dat'%ii)), I, J)
            with open(datPath, 'ab') as outfile:
                np.savetxt(outfile, outData, fmt='%f', delimiter = ', ', header = zoneString , comments='')