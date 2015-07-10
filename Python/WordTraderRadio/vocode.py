#!/usr/bin/env python

import wave, sys
import numpy, numpy.fft
import math, cmath, random

## Maybe useful:
# iAmp = 2**14
# sine wave: y = iAmp*math.sin(2*cmath.pi*freq*currentT/framerate)
# saw wave:  y = 2*iAmp*(currentT/framerate*freq-math.floor(0.5+currentT/framerate*freq))
# triangle:  y = 2*abs(saw)-iAmp

def vocode(tWav, vWav):
    N = 1024
    M = 3
    H = N/M
    H_ = H/4
    i = 0
    window = numpy.blackman(N)
    tBytes = tWav.readframes(tWav.getnframes())
    vBytes = vWav.readframes(vWav.getnframes())
    tFloats = numpy.array(wave.struct.unpack("%dh"%(len(tBytes)/tWav.getsampwidth()), tBytes))
    vFloats = numpy.array(wave.struct.unpack("%dh"%(len(vBytes)/vWav.getsampwidth()), vBytes))

    oFloats = [0] * max(len(tFloats), len(vFloats))

    ## with overlapping windows
    while (i+N < len(tFloats)) and (i+N < len(vFloats)):
        tFloatWin = tFloats[i:i+N]*window
        vFloatWin = vFloats[i:i+N]*window

        iAmp = max(max(tFloatWin), max(vFloatWin))
        vFloatSum = sum(map(abs, vFloatWin))

        # Take the full (complex) fft
        tFftData=numpy.fft.fft(tFloatWin)
        vFftData=numpy.fft.fft(vFloatWin)

        ## cartesian to polar
        tFftPolar = [cmath.polar(z) for z in tFftData]
        vFftPolar = [cmath.polar(z) for z in vFftData]

        ## multiply magnitudes
        oFftPolar = [(r0*r1, p0) for ((r0,p0), (r1,p1)) in zip(tFftPolar, vFftPolar)]

        ## polar to cartesian
        oFftData = [cmath.rect(r,p) for (r,p) in oFftPolar]

        ## ifft(mult-mags, tPhase)
        oFloatsZ = numpy.fft.ifft(oFftData)

        ## convert back to real
        oFloatsR = numpy.round([z.real for z in oFloatsZ])

        ## scale and ignore parts of song without words
        oAmp = max(oFloatsR)
        oFloatsO = [(v/oAmp*iAmp).astype('int16') for v in oFloatsR] if vFloatSum>H_ else numpy.zeros(N)

        ## sum into output array
        oFloats[i:i+N] = [(x+y/M) for (x,y) in zip(oFloats[i:i+N], oFloatsO)]

        i += H

    return oFloats

if len(sys.argv) > 2:
    tune = sys.argv[1]
    voice = sys.argv[2]
else:
    print "Please provide tune and voice wav files"
    sys.exit(0)

ob = vocode(wave.open(tune), wave.open(voice))
of = wave.open(tune.replace(".wav", ".vox.wav"), 'w')
of.setparams((1, 2, 44100, 8, 'NONE', 'NONE'))

print "writing to disk"
of.writeframes(wave.struct.pack("%dh"%len(ob), *ob))
of.close()
