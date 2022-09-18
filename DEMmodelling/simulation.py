'''
Author: Ke Wang
Topographic Simulation
'''
import sys
import random
import numpy as np
import arcpy as ap
import arcpy.sa as sa
ap.CheckOutExtension("3D")
ap.CheckOutExtension("spatial")
import ls
import gc

ZFACTOR = 1
DELEV = 0.1
CUTOFF= 0.5

def main():
    #iter= int(sys.argv[1])
    #iters = int(sys.argv[2])
    iter=  0 #the initial iteration time
    iters = 4001 #the maximum iteration

    #the dem_path should be the intial dem path and the initial dem name shoulc be dem0 and dem0.tif
    dem_path = (r"G:\WangkeResult\Soil0p1Results\dem%d.tif" % iter)
    #the workspace where the output data save in
    ap.env.workspace = r"G:\WangkeResult\Soil0p1Results"
    ap.env.overwriteOutput = True

    dem_matrix = ap.RasterToNumPyArray(dem_path)
    dem_raster = ap.Raster(dem_path)

    des = ap.Describe(dem_path)
    dem_nodata = dem_raster.noDataValue
    nodata_mask = dem_matrix==dem_nodata
    xRes = dem_raster.meanCellWidth
    yRes = dem_raster.meanCellHeight
    height = dem_raster.height
    width = dem_raster.width



    while(iter < iters):
        print "##Iter: ", iter

        
        #Here, the up two lines can combine to one step:       
        fill_raster = sa.Fill(dem_path)
        dem_matrix = ap.RasterToNumPyArray(fill_raster)

        #TDDO:Must use the filled dem to add DELEV
        direction_raster = sa.FlowDirection(fill_raster, "NORMAL")
        accumulation_raster = sa.FlowAccumulation(direction_raster)
        slope_raster = sa.Slope(fill_raster,"DEGREE",1)
        ls_matrix = ls.ls_quick(ap.RasterToNumPyArray(accumulation_raster),
                     ap.RasterToNumPyArray(slope_raster),
                     ap.RasterToNumPyArray(direction_raster),
                     height,width,CUTOFF,xRes,nodata_mask)
        #ls_matrix = ls.LS(ap.RasterToNumPyArray(slope_raster), ap.RasterToNumPyArray(direction_raster), CUTOFF, xRes, nodata_mask)
        save_raster_like(ls_matrix, parse("ls", iter, "tif"), des, nodata_mask, -1)
        ls_matrix = normalize(ls_matrix,nodata_mask)

        #Sim by stochastic factor
        #np.random.seed(np.random.randint(9999999))
        dem_matrix[np.random.rand(height,width)<=ls_matrix]+=DELEV
        # for h in range(height):
        #     for w in range(width):
        #         if(nodata_mask[h][w]): continue
        #         if roulette(ls_matrix[h][w]):
        #             dem_matrix[h][w]+=DELEV
        iter += 1
        dem_path = parse("dem",iter,"tif")
        save_raster_like(dem_matrix,dem_path,des,nodata_mask,dem_nodata)
        
        if iter % 50 == 0 :
            del fill_raster
            del dem_matrix
            del direction_raster
            del accumulation_raster
            del slope_raster
            del ls_matrix

            gc.collect()

def roulette(p):
    return random.random() <= p

def normalize(matrix,nodata_mask):
    theMax = np.max(matrix)
    theMin = np.min(matrix)
    ###matrix = (matrix-theMin)*1.0/(theMax-theMin) //TODO:must consider nodata mask?
    for r in range(len(matrix)):
        for c in range(len(matrix[0])):
            if nodata_mask[r][c]: continue
            else: matrix[r][c] = (matrix[r][c]-theMin)*1.0/(theMax-theMin)
    return matrix

def parse(name,iter,ext):
    return r"%s%d.%s" % (name,iter,ext)

def save_raster_like(input_matrix, output_path, des, nodata_mask, nodata_value=None):
    '''None'''
    res = des.meanCellHeight
    llc = des.extent.lowerLeft
    ref = des.spatialReference
    if nodata_value!=None: input_matrix[nodata_mask]=nodata_value
    output_raster = ap.NumPyArrayToRaster(input_matrix,llc,res,res,nodata_value) #!!!!! TODO: nodata must be figured out
    output_raster.save(output_path)
    ap.DefineProjection_management(output_path,ref)
    return output_path

if __name__ == "__main__":
    main()
