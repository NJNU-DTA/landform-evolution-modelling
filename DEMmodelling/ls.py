'''
the LS factor: length slope factor of USLE model
Created by Ke Wang at 2016.11.18
!!!Attention: DEM must be filled!!!
flow direcrion
32 64 128
16 00  1
 8  4  2

'''
import numpy as np
import math
from _direction import *
from _dem import outofIndex

def cumuL_cell(slope_matrix, direction_matrix, cumuL_matrix, cutoff, r, c, height, width, res, nodata_mask):
    '''
    calculate the L value at matrix[r,c] position
    before using, the cumuL_matrix must be generated by init_cumuL_matrix (the initial values are all -1).
    nodata will be -1
    :param slope_matrix: the numpy array of slope
    :param direction_matrix: the numpy array of direction matrix
    :param cumuL_matrix: the output cumulative length matrix, is will be written.
    :param r: the row number of current cell
    :param c: the column number of current cell
    :param height: the height of whole extent (how many rows)
    :param width: tge width of whole extent (how many columns)
    :param res: the resolution of cell
    :param direction_nodata: nodata value of direction raster
    :return: cumulative length value of this current cell at (r,c)
    '''
    global DCS
    global MUTUALDCS
    global DIAGDIREC

    if(cumuL_matrix[r][c]==-1): # has not set the cumulative length value then calculate
        slopeValue = slope_matrix[r][c]
        direcValue = slope_matrix[r][c]
        highPointValue = res*(ROOT2 if direcValue in DIAGDIREC else 1)/2.0
        cumuL = 0
        downCoor = step(r,c,direction_matrix[r][c]) #the downhill cell where this cell flow to
        if((not outofIndex(downCoor,height,width)) and (slopeValue-slope_matrix[downCoor]) >  cutoff * slopeValue):# slope cutoff
            cumuL = highPointValue
        else:
            for d in DCS:
                upCoor = step(r,c,d)
                if(outofIndex(upCoor,height,width) or nodata_mask[upCoor]):
                    continue # the cell in this direction is out of index or nodata
                if (d + direction_matrix[upCoor]) in MUTUALDCS:
                    upL = cumuL_cell(slope_matrix,
                                     direction_matrix,
                                     cumuL_matrix,
                                     cutoff,
                                     upCoor[0], upCoor[1],
                                     height, width,
                                     res, nodata_mask)
                    cumuL += ((ROOT2 if d in DIAGDIREC else 1)*res + upL)
            if cumuL==0: cumuL = highPointValue
        cumuL_matrix[r][c] = cumuL
        return cumuL
    else: # has calculate the L at this cell, then directly return this value
        return cumuL_matrix[r][c]

def LS(slope_matrix, direction_matrix, cutoff, res, nodata_mask):
    cumuL_matrix = np.zeros_like(slope_matrix,dtype=np.float32)-1
    LS_matrix = np.zeros_like(slope_matrix,dtype=np.float32)-1
    height,width = slope_matrix.shape
    for h in xrange(height):
        #if h%50==0: print "LS",h,height
        for w in xrange(width):
            if nodata_mask[h][w]: continue
            cumuLValue = cumuL_cell(slope_matrix,
                                    direction_matrix,
                                    cumuL_matrix,
                                    cutoff,h,w,
                                    height,width,
                                    res,nodata_mask)
            slopeValue = slope_matrix[h][w]
            if (slopeValue <= 1): m = 0.2
            elif (slopeValue <= 3): m = 0.3
            elif (slopeValue <= 5): m = 0.4
            else: m = 0.5
            Lvalue = (cumuLValue / 22.1) ** m

            if slopeValue < 5: Svalue = 10.8 * math.sin(math.radians(slopeValue)) + 0.036
            elif slopeValue >= 10: Svalue = 21.9 * math.sin(math.radians(slopeValue)) - 0.96
            else: Svalue = 16.8 * math.sin(math.radians(slopeValue)) - 0.5

            LS_matrix[h][w] = Lvalue*Svalue
    return LS_matrix

def S_cell(slope_matrix, S_matrix, r,c, nodata_mask):
    '''
    calcualte the S factor of LS at (r,c) cell

    :param slope_matrix:
    :param S_matrix:
    :param r:
    :param c:
    :param height:
    :param width:
    :param slope_nodata:
    :return:
    '''
    slopeValue = slope_matrix[r][c]
    if slopeValue < 5:  Svalue = 10.8*math.sin(math.radians(slopeValue))+0.036
    elif slopeValue >= 10: Svalue = 21.9*math.sin(math.radians(slopeValue))-0.96
    else: Svalue = 16.8*math.sin(math.radians(slopeValue))-0.5
    S_matrix[r][c] = Svalue
    return Svalue

def L_cell(slope_matrix, cumuL_matrix, L_matrix, r, c, nodata_mask):
    slopeValue = slope_matrix[r][c]
    if(slopeValue<=1): m=0.2
    elif(slopeValue<=3): m=0.3
    elif(slopeValue<=5): m=0.4
    else: m=0.5
    Lvalue = (cumuL_matrix[r][c]/22.1)**m
    L_matrix[r][c] = Lvalue
    return Lvalue

def ls_quick(accumulation_matrix,slope_matrix,direction_matrix,height,width,cutoff, res, nodata_mask):
    #TODO: cutoff value

    cumuL_matrix = np.zeros((height,width),dtype=np.float32)
    sortedAccumulationIndex = sortAccumulation(accumulation_matrix,height,width,nodata_mask)

    hightpointHV1 = res/2.0 #Direction is not dianonal
    hightpointROOT2 = res*ROOT2/2.0 #Direction is Dianonal
    for i in sortedAccumulationIndex:

        r,c = index2d(i,height,width) #the current r,c
        theDirection = direction_matrix[r,c] #direction
        slopeValue = slope_matrix[r,c]  # slope value
        dr,dc = step(r,c,theDirection)  # the downstream rowNo and colNo
        highPointValue = hightpointROOT2 if theDirection in DIAGDIREC else hightpointHV1

        # if this cell is hight point, set the cumuL value as hight point value
        if accumulation_matrix[r,c]==0:
            cumuL_matrix[r,c]=highPointValue

        #have the downstream cell
        if (not outofIndex((dr,dc),height,width)):
            # cutoff-sediment
            if (slopeValue-slope_matrix[dr,dc]) > cutoff*slopeValue:
                cumuL_matrix[dr,dc] += highPointValue*2
            # not cutoff
            else:
                cumuL_matrix[dr,dc] += (cumuL_matrix[r,c]+highPointValue*2)
    L_matrix = np.piecewise(cumuL_matrix,
                            [slope_matrix<=1,
                             np.logical_and(slope_matrix>1,slope_matrix<=3),
                             np.logical_and(slope_matrix>3,slope_matrix<=5)],
                            [lambda cl: (cl/22.1)**0.2,
                             lambda cl: (cl/22.1)**0.3,
                             lambda cl: (cl/22.1)**0.4,
                             lambda cl: (cl/22.1)**0.5])
    S_matrix = np.piecewise(slope_matrix,
                            [slope_matrix<5,
                             np.logical_and(slope_matrix>=5,slope_matrix<10),
                             slope_matrix>=10],
                            [lambda s: 10.8*np.sin(np.radians(s))+0.036,
                             lambda s: 16.8*np.sin(np.radians(s))-0.5,
                             lambda s: 21.9*np.sin(np.radians(s))-0.96])
    LS_matirx = L_matrix*S_matrix
    LS_matirx[nodata_mask] = -1
    return LS_matirx

def sortAccumulation(accumulation_matrix,height,width,nodata_mask):
    '''
    get the sorted index order by sort simulation matrix
    the purpose is get the order from upstream to downstream
    this method will prevent the recursion in LS algorithm
    '''
    # axis=None will use the flattened matrix
    sortedIndex=np.argsort(accumulation_matrix.flatten(),axis=None)
    return sortedIndex[~(nodata_mask.flatten()[sortedIndex])]

def index2d(n,height,width):
    r = n/width
    c = n-r*width
    return (r,c)