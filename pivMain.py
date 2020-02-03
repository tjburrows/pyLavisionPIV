import pivFunctions as piv

#   Get Case Info
cfgData = piv.pivGetCfgData()

#   Calculate Instantaneous and Average Fields
piv.pivCalcInstAndAvg(cfgData,0)

#   Export to Tecplot file
avg  = 1        #   Export Tecplot file for average field
inst = 0        #   Export Tecplot file for instantaneous field
piv.pivExportTecplot(cfgData, avg, inst)