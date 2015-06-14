#!/usr/bin/env python

import wave, sys
import numpy, numpy.fft
import math, cmath, random


def vocode_(vWav, freq):
    N = vWav.getnframes()/33
    M = vWav.getsampwidth()*vWav.getnchannels()*N

    framerate = vWav.getframerate()
    sampwidth = vWav.getsampwidth()
    window = numpy.blackman(N*vWav.getnchannels())
    vBytes = vWav.readframes(N)
    oBytes = []
    currentT = 0.0
    iAmp = 2**14

    while (len(vBytes) == M):
        vFloats = numpy.array(wave.struct.unpack("%dh"%(len(vBytes)/sampwidth), vBytes))*window

        tFloats = []
        for i in range(len(vFloats)):
            #y = iAmp*math.sin(2*cmath.pi*freq*currentT/framerate)
            y = 2*iAmp*(currentT/framerate*freq-math.floor(0.5+currentT/framerate*freq))
            y = 2*abs(y)-iAmp
            tFloats.append(y)
            currentT += 1.0
        tFloats = numpy.array(tFloats)*window

        # Take the full (complex) fft
        tFftData=numpy.fft.fft(tFloats)
        vFftData=numpy.fft.fft(vFloats)

        ## cartesian to polar
        tFftPolar = [cmath.polar(z) for z in tFftData]
        vFftPolar = [cmath.polar(z) for z in vFftData]

        ## multiply magnitudes
        oFftPolar = [(r0*r1, p0) for ((r0,p0), (r1,p1)) in zip(tFftPolar, vFftPolar)]

        ## polar to cartesian
        oFftData = [cmath.rect(r,p) for (r,p) in oFftPolar]

        ## ifft(mult-mags, tPhase)
        oFloats = numpy.fft.ifft(oFftData)
        oFloatsR = [numpy.round(z.real) for z in oFloats]

        oAmp = max(oFloatsR)
        oBytes += [(o/oAmp*iAmp).astype('int16') for o in oFloatsR]

        vBytes = vWav.readframes(N)

    return oBytes

def vocode(tWav, vWav):
    N0 = 512
    N = N0
    M = tWav.getsampwidth()*tWav.getnchannels()*N
    window = numpy.blackman(N*tWav.getnchannels())
    tBytes = tWav.readframes(N)
    vBytes = vWav.readframes(N)
    oBytes = []

    ## TODO: implement overlapping windows
    while (len(tBytes) == M) and (len(vBytes) == M):
        tFloats = numpy.array(wave.struct.unpack("%dh"%(len(tBytes)/tWav.getsampwidth()), tBytes))*window
        vFloats = numpy.array(wave.struct.unpack("%dh"%(len(vBytes)/vWav.getsampwidth()), vBytes))*window

        iAmp = max(max(tFloats), max(vFloats))
        vFloatSum = sum(map(abs, vFloats))

        # Take the full (complex) fft
        tFftData=numpy.fft.fft(tFloats)
        vFftData=numpy.fft.fft(vFloats)

        ## cartesian to polar
        tFftPolar = [cmath.polar(z) for z in tFftData]
        vFftPolar = [cmath.polar(z) for z in vFftData]

        ## multiply magnitudes
        oFftPolar = [(r0*r1, p1) for ((r0,p0), (r1,p1)) in zip(tFftPolar, vFftPolar)]

        ## polar to cartesian
        oFftData = [cmath.rect(r,p) for (r,p) in oFftPolar]

        ## ifft(mult-mags, tPhase)
        oFloats = numpy.fft.ifft(oFftData)
        oFloatsR = [numpy.round(z.real) for z in oFloats]

        oAmp = max(oFloatsR)
        oBytes += [(o/oAmp*iAmp).astype('int16') for o in oFloatsR]
        #oBytes += [(o/oAmp*iAmp).astype('int16') if vFloatSum>2*N else 0 for o in oFloatsR]

        N = int(random.uniform(0.8*N0,1.2*N0))
        M = tWav.getsampwidth()*tWav.getnchannels()*N
        window = numpy.blackman(N*tWav.getnchannels())

        tBytes = tWav.readframes(N)
        vBytes = vWav.readframes(N)

    return oBytes

if len(sys.argv) > 2:
    tune = sys.argv[1]
    voice = sys.argv[2]
else:
    print "Please provide tune and voice wav files"
    sys.exit(0)

ob = vocode(wave.open(tune), wave.open(voice))
of = wave.open(tune.replace(".wav", ".vox.wav"), 'w')
of.setparams((1, 2, 44100, 8, 'NONE', 'NONE'))

for (x,y) in zip(ob[0::2], ob[1::2]):
    of.writeframes(wave.struct.pack("hh", x,y))

of.close()
