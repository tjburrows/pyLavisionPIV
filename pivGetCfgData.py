from pivCheckCfgData import pivCheckCfgData

def pivGetCfgData():
    # .vc7 files are located in basePath/sets/pivPath/*.pivExtension, such that multiple sets can be iterated through.
    
    #   Initialization
    cfgData = dict();
    cfgData['sets'] = list();
    
    # Parameters
    cfgData['basePath']         = r'P:\Travis\PIV\plane_1\Date=20200130_Time=112226_S3_Plane1'
    cfgData['savePath']         = r'P:\Travis\PIV\plane_1\pkl\m0.4';
    cfgData['pivPath']          = r'SubOverTimeButterworth_cL=7\StereoPIV_MP(3x32x32_50%ov_ImgCorr)\PostProc_02';
    cfgData['pivExtension']     = 'vc7';
    cfgData['numFilesLimit']    = 6000
    
    # Stereo or planar
    cfgData['is3D'] = True
    
    # Windows information
    
    #   Set information
    cfgData['sets'].append(r'Time=150255_S3_M0.4_2kHz_1.75us_USE')
    
    #   Tecplot preplot.exe path (if not installed, assign blank string)
    cfgData['preplot']   = r'C:\Program Files\Tecplot\Tec360 2013R1\bin\preplot.exe';
    
    #   Parse cfgData
    cfgData = pivCheckCfgData(cfgData);
    
    return cfgData