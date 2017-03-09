#!/usr/bin/python
import picoscope
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import time
import math
from ctypes import *
import scipy.optimize

picoscope = reload(picoscope)
from picoscope import ps3000a
ps3000a = reload(ps3000a)

ps = ps3000a.PS3000a()

def setFreq(freq):
	offsetVoltage = 0.0
	pkToPk = 3.2
	m = ps.lib.ps3000aSetSigGenBuiltInV2(
		c_int16(ps.handle),
		c_int32(int(offsetVoltage * 1000000)),
		c_int32(int(pkToPk        * 1000000)),
		c_int16(0),
		c_double(freq), c_double(freq),
		c_double(0.0), c_double(0.0), c_uint(0), c_uint(0),
		c_uint32(0xFFFFFFFF), c_uint32(0),	#shots, sweeps
		#c_uint32(100), c_uint32(0),	#shots, sweeps
		c_uint(0), c_uint(0),
		c_int16(0))
	if m!= 0:
		raise Exception("error setting freq: " + str(m) + "at freq" + str(freq))

def sine(t, a, f, phi, b):
	return a * np.sin(f * 2 * np.pi * t - phi) + b

def fitsine(X, Y, freq):
	maxY = np.max(np.abs(Y))
	if maxY == 0:
		maxY = 0.01
	guess = [maxY, freq, 0, 0]		#amplitude, frequency, phase
	(a, f, p, b), pconv = scipy.optimize.curve_fit(sine, X, Y, guess,
	bounds=(
	[0, freq * 0.8, 0, -2],
	[maxY * 1.1, freq * 1.2, 2*np.pi, 2]))
	return a, f, p, b

vranges = [50e-3, 100e-3, 200e-3, 500e-3, 1.0, 2.0, 5.0, 10.0, 20.0]
rangeA = 5
rangeB = 5

ps.setChannel(channel="A", coupling="AC", VRange=vranges[rangeA], probeAttenuation=1.0)
ps.setChannel(channel="B", coupling="AC", VRange=vranges[rangeB], probeAttenuation=1.0)
ps.setSimpleTrigger("A", threshold_V=0)
ps.setNoOfCaptures(1)

samples = 10000

fmin = 0.1e3
fmax = 1000e3
fnum = 200

flogmin = np.log(fmin)
flogmax = np.log(fmax)

floglist = np.linspace(flogmin, flogmax, fnum)

flist = np.exp(floglist)
gain = np.zeros(fnum)
phase = np.zeros(fnum)
err = np.zeros(fnum)

for i in range(0, len(flist)):
	f = flist[i]
	setFreq(f)
	time.sleep(0.01)
	sf = ps.setSamplingFrequency(f * 250, samples)[0]

	repeat = True
	count = 0

	while repeat and count < len(vranges) + 1:
		repeat = False
		count = count + 1
		ps.runBlock()
		ps.waitReady()

		dataA = ps.getDataV("A")
		dataB = ps.getDataV("B")
		T = np.arange(len(dataA)) / sf

		aA, fA, pA, bA = fitsine(T, dataA, f)
		aB, fB, pB, bB = fitsine(T, dataB, f)

		if(rangeA > 0 and aA < 0.6 * vranges[rangeA - 1]):
			rangeA = rangeA - 1
			ps.setChannel(channel="A", coupling="AC", VRange=vranges[rangeA], probeAttenuation=1.0)
			repeat = True

		if(rangeB > 0 and aB < 0.6 * vranges[rangeB - 1]):
			rangeB = rangeB - 1
			ps.setChannel(channel="B", coupling="AC", VRange=vranges[rangeB], probeAttenuation=1.0)
			repeat = True

		if(rangeA < (len(vranges) - 1) and aA > 0.95 * vranges[rangeA]):
			rangeA = rangeA + 1
			ps.setChannel(channel="A", coupling="AC", VRange=vranges[rangeA], probeAttenuation=1.0)
			repeat = True

		if(rangeB < (len(vranges) - 1) and aB > 0.95 * vranges[rangeB]):
			rangeB = rangeB + 1
			ps.setChannel(channel="B", coupling="AC", VRange=vranges[rangeB], probeAttenuation=1.0)
			repeat = True


		gain[i] = aB/aA
		phase[i] = pB - pA

		print str(i) + "/" + str(fnum), "\tF:", f, "\tA:", vranges[rangeA], "\tB:", vranges[rangeB], "\tG:", gain[i], "\tP:", phase[i]#, "\toffset:", bB


ps.close()

fig = plt.figure()
ax = fig.add_subplot(111)

lns1 = ax.loglog(flist, gain, '-b', label = 'Amplitude')
ax2 = ax.twinx()
lns2 = ax2.semilogx(flist, phase, '-r', label = 'Phase')

ax.set_xlabel("f")
ax.set_ylabel("gain")
ax2.set_ylabel("phase")

ax2.set_ylim(-2, 2)

lns = lns1+lns2
labs = [l.get_label() for l in lns]
l=ax.legend(lns, labs, loc='upper left')

plt.show()
