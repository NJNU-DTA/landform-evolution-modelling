DCS = [1,2,4,8,16,32,64,128] # D8: eight direction codes
MUTUALDCS = [17,34,68,136] # mutual direction, eg. 1+16=17
DIAGDIREC = [2,8,32,128]
ROOT2 = 1.41421356

def step(r,c,code):
    if(code==1): return r,c+1
    elif(code==2): return r+1,c+1
    elif(code==4): return r+1,c
    elif(code==8): return r+1,c-1
    elif(code==16): return r,c-1
    elif(code==32): return r-1,c-1
    elif(code==64): return r-1,c
    elif(code==128): return r-1,c+1
    else:
        print("wk: step function error code")
        return r,c
