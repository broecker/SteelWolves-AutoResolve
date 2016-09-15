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
import math

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
	 	self.minKey = newRange[0]
	 	self.maxKey = newRange[1]

	def getCompressed(self):
		maxLength = 10
		result = []

		for v in self.values:
			u = int(round(float(v[1]) / self.peak[1] * 10))
			u = min(u, 10)

			result.append((v[0], u))

		return result


	def findD10DRM(self):

		scores = []

		ownCompressed = self.getCompressed()

		for drm in range(-10, 10):
			result = dieroller.dieRoller(2, 10, drm, 2000, False)

			# compress the result
			compressedResult = []
			peakR = 0
			for r in result:
				peakR = max(peakR, r[1])

			for r in result:
				u = int(round(float(r[1]) / peakR * 10))
				u = min(u, 10)
				compressedResult.append((r[0], u))
			
			#print(compressedResult)

			# now compare the compressed results

			# first, make sure that the results start at the same offset
			score = 0
			for i, j in zip(compressedResult, ownCompressed): 
				val = abs(i[1] -j[1])
				score += val


			scores.append((drm, score))


		scores.sort(key=lambda x:x[1])
		print(scores)




		bestResult = dieroller.dieRoller(2, 10, -4, 2000, False, False)

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


	def compare(self, other):
		print('Comparing histograms ' + self.name + ' and ' + other.name)

		# print both distributions in the form
		#     [self] [roll] [other]
		# *** [0000] [roll] [0000] ***
		for roll in range(min(other.minKey, self.minKey), max(other.maxKey, self.maxKey)):


			leftValue = self.findValue(roll)
			if leftValue:
				leftValue = leftValue[1]
			else:
				leftValue = 0

			rightValue = other.findValue(roll)
			if rightValue:
				rightValue = rightValue[1]
			else:
				rightValue = 0


			sl = int(round(float(leftValue) / self.peak[1] * 10))
			if sl > 10:
				sl = '+' + 9*'*'
			else:
				sl = sl * '*'

			sr = int(round(float(rightValue) / other.peak[1] * 10))
			if sr > 10:
				sr = 9*'*' + '+'
			else:
				sr = sr*'*'

			print( '% 10s' % sl + ' %4d' % leftValue + ' %02d ' % roll + '%4d ' % rightValue + sr)






	def findLinearRange(self, count=10):
		totalSum = sum(t[1] for t in self.values)
		divider = int(totalSum / count)
		
		# reverse tuples
		valueRange = []
		for v in self.values:
			valueRange.append((v[1], v[0]))
		#valueRange.sort(key=lambda x:x[0], reverse=True)
		
		table = []

		# split values that are larger than the divider and combine values that
		# are smaller
		i = 0
		currentSum = valueRange[0][0]
		try:
			while i < len(valueRange):
				
				if currentSum > divider:
					table.append(i)
					currentSum -= divider
				else:
					i += 1
					currentSum += valueRange[i][0] 
		except IndexError:
			pass

		print(self.name + ' linear range:')
		#print(table)

		# calculate average values for the table 
		# TODO: should be weighted? 
		for i in range(len(table)-1, 1, -1):

			if table[i] == 0:
				break;

			val = table[i] + table[i-1]
			val = int(math.ceil(val / 2))
			table[i] = val


		print(table)
		return table



def calculateScore(t0, t1):
	score = 0

	for p in zip(t0,t1):
		score += abs(p[0] - p[1])

	return score


def alignTables(table1, table2):
	print('Table 1 (reference):', table1)
	print('Table 2 (target)   :', table2)

	results = []

	for drm in range(-8, 8):
		tcp = table2[:]

		if drm > 0:
			# drm > 0 -> shift right
			for k in range(0, drm):
				tcp.insert(0, 0)
				tcp.pop()

		if drm < 0:
			for k in range(0, -drm):
				# drm < 0 -> shift left
				tcp.append(tcp[-1])
				tcp.pop(0)

		#print('DRM ' + str(drm))
		#print('Table 1 (reference):', table1)
		#print('Table 2 (target)   :', tcp)

		score = calculateScore(table1, tcp)
		#print('DRM ' + str(drm) + ', score: ' + str(score) )
		
		results.append((drm, score))		

	# pick the best == lowest score
	results.sort(key=lambda x: x[1])
	print('Tables aligned with DRM: ' + str(results[0][0]) )





if __name__ == '__main__':
	filename ='c1-wp1.csv'

	if len(sys.argv) > 1:
		filename =sys.argv[1]

	data1 = loadFile('c1-332+0-wp1.csv')
	tons1 = [r.tgtTons for r in data1]
	tons1.sort
	
	data2 = loadFile('c1-332+1-wp1.csv')
	tons2 = [r.tgtTons for r in data2]
	tons2.sort()

	data3 = loadFile('c1-332+2-wp1.csv')
	tons3 = [r.tgtTons for r in data3]
	tons3.sort()

	histo1 = Histogram('Tonnage 332+0', tons1)
	histo2 = Histogram('Tonnage 332+1', tons2)
	histo3 = Histogram('Tonnage 332+2', tons3)

	histo1.compare(histo2)

	t0 = histo1.findLinearRange(10)
	t1 = histo2.findLinearRange(10)
	t2 = histo3.findLinearRange(10)


	damaged1 = [r.subsDamaged for r in data1]
	damaged1.sort()

	damaged2 = [r.subsDamaged for r in data2]
	damaged2.sort()

	histo1d = Histogram('Damaged subs 332+0', damaged1)
	histo1d.findLinearRange(10)

	histo2d = Histogram('Damaged subs 332+1', damaged2)
	histo1d.compare(histo2d)

	lost1 = [r.subsSunk for r in data1]
	lost1.sort()



	alignTables(t0, t1)
	alignTables(t0, t2)
