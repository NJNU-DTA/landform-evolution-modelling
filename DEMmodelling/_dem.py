NODATA = -9999

def outofIndex(coords,height,width):
    if( 0<=coords[0]<height and 0<=coords[1]<width):return 0
    else: return 1

def index1d(r,c,height,width):
    return r*width+c
def index2d(n,height,width):
    r = n/width
    c = n-r*width
    return (r,c)

def save_raster_like(input_matrix, input_path, des, nodata_mask, nodata_value=None):
    '''
    save the input_matrix as raster with the environment of des
    :param input_matrix: the input matrix need be saved
    :param input_path: the path to save
    :param des: the arcpy Describe object contains raster info
    :param nodata_mask: the mask of nodata area
    :param nodata_value: the nodata value
    :return:
    '''
    import arcpy as ap
    res = des.meanCellHeight
    llc = des.extent.lowerLeft
    ref = des.spatialReference

    if nodata_value!=None: input_matrix[nodata_mask]=nodata_value

    output_raster = ap.NumPyArrayToRaster(input_matrix,llc,res,res,nodata_value) #!!!!! TODO: nodata must be figured out
    output_raster.save(input_path)
    ap.DefineProjection_management(input_path,ref)

    return input_path
