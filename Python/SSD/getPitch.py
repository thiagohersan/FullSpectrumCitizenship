#!/usr/bin/env python

import wave
import numpy, numpy.fft

# given a wav object, returns estimated pitch in Hz
# based on: # http://stackoverflow.com/questions/2648151/python-frequency-detection
def getPitchHz(wavObject):
    wavBytes = wavObject.readframes(wavObject.getnframes())
    wavFloats = numpy.array(wave.struct.unpack("%dh"%(len(wavBytes)/wavObject.getsampwidth()), wavBytes))

    # Take the fft and square each value
    fftData=abs(numpy.fft.rfft(wavFloats))**2

    # find the maximum (less than 500Hz: ok for finding formants in voice)
    cutOffFreq = 500*wavObject.getnframes()/wavObject.getframerate()
    which = fftData[1:cutOffFreq].argmax() + 1

    # use quadratic interpolation around the max
    y0,y1,y2 = numpy.log(fftData[which-1:which+2:])
    x1 = (y2 - y0) * .5 / (2 * y1 - y2 - y0)
    # find the frequency and output it
    freqHz = (which+x1)*wavObject.getframerate()/wavObject.getnframes()
    return freqHz
