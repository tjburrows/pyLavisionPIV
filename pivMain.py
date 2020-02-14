from pivCheckCfgData import pivCheckCfgData
from pivCalcInstAndAvg import pivCalcInstAndAvg
from pivCalcInstAndAvgParallel import pivCalcInstAndAvgParallel
from pivExportTecplot import pivExportTecplot
import time

def pivGetCfgData():
    # .vc7 files are located in basePath/sets/pivPath/*.pivExtension, such that multiple sets can be iterated through.
    
    #   Initialization
    cfgData = dict();
    cfgData['sets'] = list();
    
    # Parameters
    cfgData['basePath']         = r'P:\Travis\PIV\bc\plane_3\Date=20200207_Time=114252_BC_Plane3'
    cfgData['savePath']         = r'P:\Travis\PIV\bc\plane_3';
    cfgData['pivPath']          = r'SubOverTimeButterworth_cL=7\StereoPIV_MP(3x32x32_50%ov_ImgCorr)\PostProc';
    cfgData['pivExtension']     = 'vc7';
    cfgData['numFilesLimit']    = 6000
    
    # Stereo or planar
    cfgData['is3D'] = True
    
    #   Set information
    cfgData['sets'].append(r'Time=115329_M0.4_2kHz_1.6us')
#    cfgData['sets'].append(r'Time=155826_M0.5_2kHz_1.75us_USE')
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
#    pivCalcInstAndAvg(cfgData,0)
    pivCalcInstAndAvgParallel(cfgData,0)
    stop = time.time()
    print('Time: %.1f s' % (stop-start))
    #   Export to Tecplot file
    avg  = 1        #   Export Tecplot file for average field
    inst = 0       #   Export Tecplot file for instantaneous field
    pivExportTecplot(cfgData, avg, inst)

if __name__ == '__main__':
    main()