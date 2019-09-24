from pivCheckCfgData import pivCheckCfgData

def pivGetCfgData():
    # .vc7 files are located in basePath/sets/pivPath/*.pivExtension, such that multiple sets can be iterated through.
    
    #   Initialization
    cfgData = dict();
    cfgData['sets'] = list();
    
    # Parameters
    cfgData['basePath']         = r'P:'
    cfgData['savePath']         = r'P:\Travis\PIV\test_piv_data\PostProc_01\save';
    cfgData['pivPath']          = r'PIV\test_piv_data\PostProc_01';
    cfgData['pivExtension']     = 'vc7';
    cfgData['numFilesLimit'] = 100
    
    # Windows information
    
    #   Set information
    cfgData['sets'].append('Travis')
    
    #   Tecplot preplot.exe path (if not installed, assign blank string)
    cfgData['preplot']   = r'C:\Program Files\Tecplot\Tec360 2013R1\bin\preplot.exe';
    
    #   Parse cfgData
    cfgData = pivCheckCfgData(cfgData);
    
    return cfgData