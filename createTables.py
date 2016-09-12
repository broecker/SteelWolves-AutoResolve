#!/usr/bin/env python3

# The MIT License (MIT)
# Copyright (c) 2016 Markus Broecker <mbrckr@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sys
import dieroller

class Result:
	def __init__(self, data):
		self.name = data[0]
		self.tgtSunk = data[1]
		self.tgtTons = data[2]
		self.subsDamaged = data[3]
		self.subsSunk = data[4]
		self.subsSpotted = data[5]
		self.subsRTB =data[6]
		self.subsPromoted = data[7]


	def printSummary(self):
		print('Sub',self.name, 'sunk', self.tgtSunk, 'ships for', self.tgtTons, 'tons. Status:', self.subsDamaged, 'damaged', self.subsSpotted, 'spotted', self.subsSunk, 'sunk', self.subsRTB, 'RTB', 'promoted', self.subsPromoted)





def loadFile(filename):
	result = []

	file = open(filename, 'r')
	for line in file:
		toks = line.split(',')

		if toks[0][0] == '#':
			continue

		for i in range(1,len(toks)):
			toks[i] = int(toks[i])

		r = Result(toks)
		result.append(r)

	return result



class Histogram:
	def __init__(self, name, data):
		self.name = name

		if len(data) == 0:
			print('Not enough data!')

		# create histogram here
		histo = {}

		for r in data:
			key = str(r)
			try:
				histo[key] += 1
			except KeyError:
				histo[key] = 1

		HUGE = 1000000

		self.minKey = HUGE
		self.maxKey = -HUGE - 1

		for r in histo.keys():
	 		k = int(r)
	 		self.minKey = min(self.minKey, k)
	 		self.maxKey = max(self.maxKey, k)

		# Mip mapping normal maps
		sortedArray = []
		for key in range(self.minKey, self.maxKey):

	 		try:
	 			val = histo[str(key)]
	 			sortedArray.append((key, val))
	 		except KeyError:
	 			pass

		self.values = sortedArray
		self.findPeak()

	def findPeak(self):

	 	# find the peak
		sa2 = sorted(self.values, key=lambda x: x[1])
		self.peak = sa2[-1]
		
		if self.peak[0] == 0 and len(sa2) > 1:
			nlf = float(self.peak[1]) / len(self.values)
			
			#print('zero-peak:', self.peak[1], '(%0.2f)' % nlf)
			while self.peak[0] == 0:
				sa2.pop()
				self.peak = sa2[-1]	


	def printData(self):
		print(self.name + ' histogram:')
		print('Peak: ' + str(self.peak))
		print('Keys: [' + str(self.minKey) + ' -> ' + str(self.maxKey) + ']')
		print('Distribution:')
		for t,c in self.values:
			s = int(round(float(c) / self.peak[1] * 10))
			s = s * '*'

			if c == self.peak[1]:
				s += ' <- Peak'

			print(t,c,s)

	def saveFile(self, filename):
		file = open(filename, 'w')

		for t,c in self.values:
			file.write(str(t) + ',' + str(c) + '\n')


	def loadFile(self, filename):
		file = open(filename, 'r')

		self.values = []

		for line in file:
			vals = line.split(',')
			self.values.append((int(vals[0]), int(vals[1])))


		HUGE = 1000000
		self.minKey = HUGE
		self.maxKey = -HUGE - 1

		for r in self.values:
	 		k = r[0]
	 		self.minKey = min(self.minKey, k)
	 		self.maxKey = max(self.maxKey, k)

		self.findPeak()

	def findValue(self, val):
		for i in self.values:
			if val == i[0]:
				return i
		else:
			return None



	def resample(self, newRange):

	 	print('Resampling to new key range:', newRange)

	 	newHisto = []

	 	# 1. Fill in existing values
	 	for i in range(newRange[0], newRange[1]):
	 		newHisto.append(self.findValue(i))

	 	# 2. interpolate for missing values
	 	for i in range(newRange[0]+1, newRange[1]-1):
	 		if newHisto[i] == None:
	 			val = int((newHisto[i-1][1] + newHisto[i+1][1]) * 0.5)
	 			newHisto[i] = (i, val)

	 	# 3. Handle edge cases - TODO
	 	if newHisto[0] == None:
	 		newHisto[0] = newHisto[1]
	 	if newHisto[-1] == None:
	 		newHisto[-1] = newHisto[-2]

	 	self.values = newHisto

	def getCompressed(self):
		maxLength = 10
		result = []

		for v in self.values:
			u = int(round(float(v[1]) / self.peak[1] * 10))
			u = min(u, 10)

			result.append((v[0], u))


		print(result)
		return result


	def findD10DRM(self):

		scores = []

		for drm in range(-20, 20):
			result = dieroller.dieRoller(2, 10, drm, 2000, False)

			# subtract result from current and build a score
			score = 0

			peak = 0
			for r in result:
				v = self.findValue(r[0])
				if v:
					score += abs(v[0] - r[1])
				else:
					score += r[1]

				if r[1] > peak:
					peak = r[0]

			scores.append((drm, score, peak))


		bestResult = dieroller.dieRoller(2, 6, 0, 2000, False, False)


		print('compressing ... ')
		self.getCompressed()


		def findValueInResult(val):
			for i in bestResult:
				if i[0] == val:
					return i
			return None

		resultPeak = 0
		for i in bestResult:
			resultPeak = max(resultPeak, i[1])

		# print both distributions in the form
		# [original] [roll] [reconstructed]
		# *** [0000] [roll] [0000] ***
		for roll in range(min(bestResult[0][0], self.minKey), max(bestResult[-1][0], self.maxKey)):
			pass


			leftValue = self.findValue(roll)
			if leftValue:
				leftValue = leftValue[1]
			else:
				leftValue = 0

			rightValue = findValueInResult(roll)
			if rightValue:
				rightValue = rightValue[1]
			else:
				rightValue = 0


			sl = int(round(float(leftValue) / self.peak[1] * 10))
			sl = min(sl, 10)
			sl = sl * '*'

			sr = int(round(float(rightValue) / resultPeak * 10))
			sr = sr * '*'

			

			print( '% 10s' % sl + ' %4d' % leftValue + ' %02d ' % roll + '%4d ' % rightValue + sr)










if __name__ == '__main__':
	filename ='c1-wp1.csv'

	print(dir(sys))
	print(sys.version)

	if len(sys.argv) > 1:
		filename =sys.argv[1]


	if False:
		data = loadFile(filename)

		for r in data:
			#r.printSummary()
			pass

		count = len(data)
		print('Subs')
		print('-----------------------')

		damaged = sum(r.subsDamaged for r in data if r.subsDamaged > 0)
		print('Damaged : %4d'  % damaged + '/' + str(count))

		sunk = sum(r.subsSunk for r in data if r.subsSunk > 0)
		print('Sunk    : %4d' % sunk + '/' + str(count))

		rtb = sum(r.subsRTB for r in data if r.subsRTB > 0)
		print('RTB     : %4d' % rtb + '/' + str(count))

		spotted = sum(r.subsSpotted for r in data if r.subsSpotted > 0)
		print('Spotted : %4d' % spotted + '/' + str(count))

		promoted = sum(r.subsPromoted for r in data if r.subsPromoted > 0)
		print('Promoted: %4d' %promoted + '/' + str(count))


	if False:

		data1 = loadFile('c1-wp1-1sub.csv')
		data4 = loadFile('c1-wp1-4sub.csv')

		tons1 = [r.tgtTons for r in data1]
		tons1.sort

		tons4 = [r.tgtTons for r in data4]
		tons4.sort


		histo1 = Histogram('Tonnage 1', tons1)
		histo1.printData()

		histo4 = Histogram('Tonnage 4', tons4)
		histo4.printData()

	data1 = loadFile('c1-wp1-1sub.csv')
	tons1 = [r.tgtTons for r in data1]
	tons1.sort
	histo1 = Histogram('Tonnage 1', tons1)
	histo1.printData()
	histo1.resample([0,19])
	histo1.printData()

	histo1.findD10DRM()
