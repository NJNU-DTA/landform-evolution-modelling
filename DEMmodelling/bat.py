import os
iter=0
step=1000
iters = iter+step

while(iters<=10000):
    os.system(r"python D:\ArcGISdata\mytoolbox\arcpy_wk\Geosimulation\DEMSimulationV4\simulation.py %d %d" % (iter,iters))
    iter = iters
    iters += step


