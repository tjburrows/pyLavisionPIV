from pivCheckCfgData import pivCheckCfgData
from pivCalcInstAndAvg import pivCalcInstAndAvg
from pivExportTecplot import pivExportTecplot
import time

def pivGetCfgData():
    # .vc7 files are located in basePath/sets/pivPath/*.pivExtension, such that multiple sets can be iterated through.
    
    #   Initialization
    cfgData = dict();
    cfgData['sets'] = list();
    
    # Parameters
    cfgData['basePath']         = r'P:\Travis\PIV\bc\plane_1\corner m0.5\Date=20200211_Time=175420_BC_Plane1'
    cfgData['savePath']         = r'P:\Travis\PIV\bc\plane_1\corner m0.5';
    cfgData['pivPath']          = r'SubOverTimeButterworth_cL=7\StereoPIV_MP(3x32x32_50%ov_ImgCorr)\PostProc';
    cfgData['pivExtension']     = 'vc7';
    cfgData['numFilesLimit']    = 6000
    
    # Stereo or planar
    cfgData['is3D'] = True
    
    #   Set information
    cfgData['sets'].append(r'Time=182351_M0.5_2kHz_1.8us')
#    cfgData['sets'].append(r'Time=170143_2kHz_1us')
#    cfgData['sets'].append(r'Time=162612_M0.6_2kHz_1.5us_USE')
    
    #   Tecplot preplot.exe path (if not installed, assign blank string)
    cfgData['preplot']   = r'C:\Program Files\Tecplot\Tec360 2013R1\bin\preplot.exe';
    
    #   Parse cfgData
    cfgData = pivCheckCfgData(cfgData);
    
    return cfgData

def main():
    
    #   Get Case Info
    cfgData = pivGetCfgData()
    
    #   Calculate Instantaneous and Average Fields
    start = time.time()
    pivCalcInstAndAvg(cfgData,0)
    stop = time.time()
    print('Time: %.1f s' % (stop-start))
    
    #   Export to Tecplot file
    avg  = 1        #   Export Tecplot file for average field
    inst = 0       #   Export Tecplot file for instantaneous field
    pivExportTecplot(cfgData, avg, inst)

if __name__ == '__main__':
    main()