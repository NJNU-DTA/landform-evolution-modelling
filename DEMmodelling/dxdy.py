'''
Author: Ke Wang
Creation Date: 2016.11.16
the rate of change in x direction and y direction

|a|b|c|
|d|e|f|
|g|h|l|

Horn's Algorithm:
dx = ((c+2f+l)-(a+2d+g)) * z_factor / (8*x_resolution)
dy = ((g+2h+l)-(a+2b+c)) * z_factor / (8*y_resolution)

'''
