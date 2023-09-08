#! python

import sys
import numpy as np
try:
    import cupy as cp
except ModuleNotFoundError:
    cp = None
import fftx

if (len(sys.argv) < 2) or (sys.argv[1] == "?"):
    print("python test-mdrfsconv-mine.py sz [ d|s  [ GPU|CPU ]]")
    print("  sz = N")
    print("  d = double (default), s = single precision")
    sys.exit()

#Cube Size
N = 81
if len(sys.argv) > 1:
    N = int ( sys.argv[1] )

src_type = np.double
if len(sys.argv) > 2:
    if sys.argv[2] == "s":
        src_type = np.single

forGPU = (cp != None)
if len ( sys.argv ) > 3:
    if sys.argv[3] == "CPU":
        forGPU = False

strPU = "CPU"
if forGPU:
    strPU = "GPU"

print('Free-space convolution kernel size ' + str(N) + ' ' + str(src_type) + ' on ' + strPU)

dims = [N, N, N]
dimsDouble = [2*N, 2*N, 2*N]
dimsTuple = tuple(dims)
dimsDoubleTuple = tuple(dimsDouble)

#build test input in numpy (cupy does not have itemset)
src = np.ones(dimsTuple, dtype=src_type)
for  k in range (np.size(src)):
    src.itemset(k, np.random.random()*10.0)

sym = np.zeros(dimsDoubleTuple, dtype=src_type)
for k in range (np.size(sym)):
    sym.itemset(k, np.random.random()*10.0)

xp = np
if forGPU:
    xp = cp
    #convert from NumPy to CuPy array
    src = cp.asarray(src)
    sym = cp.asarray(sym)

testSymCube = xp.fft.fftn(sym)

fftx_result = fftx.convo.mdrfsconv(src, testSymCube)

#original spinifel calculation
ugrid_ups = xp.zeros((2*N,)*3, dtype=src.dtype)
ugrid_ups[:N, :N, :N] = src
F_ugrid_ups = xp.fft.fftn(xp.fft.ifftshift(ugrid_ups))
F_ugrid_conv_out_ups = F_ugrid_ups * testSymCube
ugrid_conv_out_ups = xp.fft.fftshift(xp.fft.ifftn(F_ugrid_conv_out_ups))
ugrid_conv_out = ugrid_conv_out_ups[:N, :N, :N]
spinifel_result = ugrid_conv_out

max_spinifel = xp.max(xp.absolute(spinifel_result))
max_diff = xp.max(xp.absolute(spinifel_result - fftx_result))
print ('Relative diff between spinifel and FFTX kernels =  ' + str(max_diff/max_spinifel) )
