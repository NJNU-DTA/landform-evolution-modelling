import numpy as np
import math

def slope_Horn(input_dem_matrix, xRes, yRes, z_factor, nodata_mask):
    height = len(input_dem_matrix)
    width = len(input_dem_matrix[0])
    output_slope_matrix = np.zeros_like(input_dem_matrix, dtype=np.float32)+0.1
    for h in xrange(height):
        #if h % 50 == 0: print h, height
        for w in xrange(width):
            if nodata_mask[h][w]: continue
            slope_cell_Horn(input_dem_matrix, output_slope_matrix, h, w, height, width, xRes, yRes, z_factor)
    return output_slope_matrix

def slope_cell_Horn(dem_matrix, slope_matrix, r, c, height, width, xRes, yRes, z_factor):

    nbr = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]],dtype=np.float32)
    for dh in [-1, 0, 1]:
        for dw in [-1, 0, 1]:
            nextCoor = (r+dh,c+dw)
            if outofIndex(nextCoor,height,width): nbr[dh+1][dw+1]=dem_matrix[r][c]
            else: nbr[dh+1][dw+1]=dem_matrix[nextCoor]
    dx = _dx(nbr, xRes, z_factor)
    dy = _dy(nbr, yRes, z_factor)
    slopeValue = math.atan(math.sqrt(dx**2 + dy**2)) * 57.29578
    slope_matrix[r][c] = slopeValue
    return slopeValue

def getSlopeValueHorn(dem_matrix,r,c,height,width,xRes,yRes,z_factor):
    nbr = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]],dtype=np.float32)
    for dh in [-1, 0, 1]:
        for dw in [-1, 0, 1]:
            nextCoor = (r+dh,c+dw)
            if outofIndex(nextCoor,height,width): nbr[dh+1][dw+1]=dem_matrix[r][c]
            else: nbr[dh+1][dw+1]=dem_matrix[nextCoor]
    dx = ((nbr[0][2]+nbr[1][2]*2+nbr[2][2])-(nbr[0][0]+nbr[1][0]*2+nbr[2][0]))*z_factor/(8*xRes)
    dy = ((nbr[2][0]+nbr[2][1]*2+nbr[2][2])-(nbr[0][0]+nbr[0][1]*2+nbr[0][2]))*z_factor/(8*yRes)
    slopeValue = math.atan(math.sqrt(dx**2 + dy**2)) * 57.29578
    return slopeValue

def outofIndex(coords,height,width):
    if( 0<=coords[0]<height and 0<=coords[1]<width):return 0
    else: return 1

def _dx(nbr, xRes, z_factor, method="Horn"):
    if method=="Horn":
        return ((nbr[0][2] + nbr[1][2] * 2 + nbr[2][2]) - (nbr[0][0] + nbr[1][0] * 2 + nbr[2][0])) * z_factor / (8 * xRes)
def _dy(nbr, yRes, z_factor,method="Horn"):
    if method == "Horn":
        return ((nbr[2][0] + nbr[2][1] * 2 + nbr[2][2]) - (nbr[0][0] + nbr[0][1] * 2 + nbr[0][2])) * z_factor / (8 * yRes)
def _dxdy(nbr, xRes, yRes, z_factor,method="Horn"):
    if method == "Horn":
        return _dx(nbr, xRes, z_factor), _dy(nbr, yRes, z_factor)

