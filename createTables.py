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


verbose_output = False

# allowed values: 'text', 'latex' or 'html'
output = 'html'

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

		if verbose_output:
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
		if verbose_output:
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

			
			if verbose_output:
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

		
		# calculate average values for the table 
		# TODO: should be weighted? 
		for i in range(len(table)-1, 1, -1):

			if table[i] == 0:
				break;

			val = table[i] + table[i-1]
			val = int(math.ceil(val / 2))
			table[i] = val


		#print(self.name + ' linear range:')
		#print(table)
		return table



def calculateScore(t0, t1):
	score = 0

	for p in zip(t0,t1):
		score += abs(p[0] - p[1])

	return score


def shiftTable(table, drm, keepSize=True):
	'''Shifts a table left or right by drm columns'''
	tcp = table[:]

	if drm > 0:
		# drm > 0 -> shift right
		for k in range(0, drm):
			tcp.insert(0, 0)
			if keepSize:
				tcp.pop()

	if drm < 0:
		for k in range(0, -drm):
			# drm < 0 -> shift left
			tcp.append(tcp[-1])
			if keepSize:
				tcp.pop(0)
	return tcp


def alignTables(table1, table2):
	if verbose_output:
		print('Table 1 (reference):', table1)
		print('Table 2 (target)   :', table2)

	results = []

	for drm in range(-8, 8):
		tcp = shiftTable(table2, drm)

		#print('DRM ' + str(drm))
		#print('Table 1 (reference):', table1)
		#print('Table 2 (target)   :', tcp)

		score = calculateScore(table1, tcp)
		#print('DRM ' + str(drm) + ', score: ' + str(score) )
		
		results.append((drm, score))		

	# pick the best == lowest score
	results.sort(key=lambda x: x[1])
	if verbose_output:
		print('Tables aligned with DRM: %+d' % results[0][0] + ' (Error: %d)' % results[0][1])
	return results[0][0]


def combineTables(reference, table2, drm):
	t2 = shiftTable(table2, drm)

	result = []
	for p in zip(reference, t2):
		r = (p[0] + p[1]) / 2
		r = math.ceil(r)
		result.append(int(r))

	#print(result)
	return result


def getPercentageRolls(series, basenumber=0):
	n = getPercentageRollNumbers(series)
	try:
		if n == None:
			return '-/-'

		if type(n[1]) is tuple:
			return str(basenumber) + '/[' + str(n[1][0]) + '-' + str(n[1][1]) + ']'
		else:
			return '[0-' + str(n[1]) + ']'
	except TypeError:
		raise NotImplementedError

def getPercentageRollNumbers(series):
	# calculate probability
	p = float(sum(series)) / len(series) * 100

	if p < 10:
		if p < 1:
			return None
		else:
			d = int(p)
			return (0, (0,d))
	else:
		d = int(p/10)
		return (0, d)


def createFilenames(warperiod, subs, tgtType, wolfpack, torp_value):
	files = []
	for s in subs:

		section = []

		if not wolfpack:
			for i in range(0,3):
				f = tgtType.lower() + '.' + s 
				f += '.wp' + str(warperiod)
				f += '.torp' + str(torp_value)
				f += '.solo' + str(i)
				f += '.csv'
				section.append(f)
		else:

			if tgtType == 'loners':
				raise ValueError
			
			count = 12
			if tgtType == 'C1':
				count = 8

			for i in range(2,count,2):
				f = tgtType.lower() + '.' + s 
				f += '.wp' + str(warperiod)
				f += '.torp' + str(torp_value)
				f += '.wolfpack' + str(i)
				f += '.csv'
				section.append(f)

		files.append(section)

	return files


def compareTonnage(files):

	results = []

	for f in files:
		data = loadFile(f)
		tons =[r.tgtTons for r in data]
		tons.sort()

		histo = Histogram('Tonnage', tons)
		results.append(histo)

	tables = []
	for r in results:
		t = r.findLinearRange(10)
		tables.append(t)

	reference = tables[0]
	drms = [0]
	for i in range(1, len(tables)):
		t = tables[i]
		drm = alignTables(reference, t)
		t = shiftTable(t, drm, False)

		tables[i] = t
		drms.append(drm)

	if verbose_output:
		print('Result:')
		print('DRM\tTable')
		print('-'*79)


	maxlen = 0
	for i in zip(drms, tables):
		if verbose_output:
			print('%+d' % i[0] + '\t', i[1])
		maxlen = max(maxlen, len(i[1]))


	# expand the tables to the same length
	for t in tables:		
		d = maxlen - len(t)

		for i in range(0,d):
			t.append(t[-1])

	# add them up
	finalTable = []
	for i in range(0, maxlen):
		val = 0
		for t in tables:
			val += t[i]

		val = float(val)
		val /= len(tables)
		val = int(val)

		finalTable.append(val)

	if verbose_output:
		print('-'*79)
		print('Final:\t', finalTable)

	return finalTable, drms

def printTable(sub, table, drms):

	finalLine = sub[0] + '-' + sub[1] + '-' + sub[2]
	if output == 'latex':
		finalLine += '&'
		
		for r in table:
			finalLine += ' %2d' % r + '&'

		for d in drms:
			finalLine += '$%+2d$' % d 
			finalLine += '&'

		finalLine = finalLine[0:-1]
		finalLine += '\\\\'

	if output == 'html':
		finalLine = '<tr><th nowrap scope="row">' + finalLine + '</th>\n'
		for r in table:
			finalLine +='\t<td>%02d' % r + '</td>\n'

		for d in drms:
			finalLine += '\t<td>%+2d' % d + '</td>\n' 
		
		finalLine += '</tr>'

	if output == 'text':
		finalLine += ' '
		finalLine += ' ' + str(table).ljust(60, ' ') 

		for d in drms:
			finalLine += '%+2d, ' % d
		finalLine = finalLine[0:-1]

	return finalLine





def compareTonnageHarness(warperiod, subs, tgtType, wolfpack, torp_value):

	# create filenames	
	files = createFilenames(warperiod, subs, tgtType, wolfpack, torp_value)

	tables = []
	drms = []
	maxRolls = 0
	maxDrms = 0
	for f in files:
	
		t, d = compareTonnage(f)
		tables.append(t)
		drms.append(d)

		maxRolls = max(maxRolls, len(t))
		maxDrms = max(maxDrms, len(d))


	# make sure the are the same length!
	for i in range(0, len(tables)):
		if len(tables[i]) < maxRolls:
			pad = [tables[i][-1]] * (maxRolls - len(tables[i]))

			tables[i] += pad


	lines = []
	for t in zip(subs, tables, drms):
		lines.append(printTable(t[0], t[1], t[2]))

	if output == 'latex':
		print('\\begin{table}[htb]')
		targetStrings = {'c2' : 'Large Convoy', 'c1' : 'Small Convoy', 'loners' : 'Loners'}
		label = 'table:tonnage.' + tgtType + '.torp' + str(torp_value)
		print('\\caption{\\label{' + label + '} Tonnage Sunk;  WP ' + str(warperiod) + ' -- ' + targetStrings[tgtType.lower()] + ', torpedo rating: ' + str(torp_value) + ' }')

		print('\\begin{tabular}{|l|' + maxRolls * ' c ' + '|' + maxDrms * ' c ' + '|}')
		print('\\hline')

		drmLabel = 'Elite Skipper DRM'
		if wolfpack:
			drmLabel = 'Wolfpack size DRM'
		print('\\multirow{2}{*}{Sub} & \\multicolumn{' + str(maxRolls) + '}{|c|}{ 1D10 Roll } & \\multicolumn{' + str(maxDrms) + '}{|c|}{\\multirow{2}{*}{' + drmLabel + '}} \\\\')
		
		l = '&'
		for i in range(0, maxRolls):
			l += '%2d' % i
			l += '&'
		for i in range(0, maxDrms-1):
			l += '&'
		l += '\\\\'
		print(l)

		print('\\hline')
		for l in lines:
			print(l)
		print('\\hline')
		print('\\end{tabular}')

		print('\\end{table}')
	

	if output == 'html':
		pass

	if output == 'text':
		print('-'*79)

		if wolfpack:
			print('WP ' + str(warperiod)  + ' - ' + tgtType + ' Wolfpack' + ' Torpedo value: ' + str(torp_value) )
			print('Sub    Tonnage Table                                               Wolfpack DRM')

		else:
			print('WP ' + str(warperiod)  + ' - ' + tgtType  + ' Torpedo value: ' + str(torp_value))
			print('Sub    Tonnage Table                                                Skipper DRM')


		for l in lines:
			print(l)


def compareShipsSunk(files):

	results = []

	for f in files:
		data = loadFile(f)
		sunk =[r.tgtSunk for r in data]
		sunk.sort()

		histo = Histogram('Ships sunk', sunk)
		results.append(histo)

	tables = []
	for r in results:
		t = r.findLinearRange(10)
		tables.append(t)

	reference = tables[0]
	drms = [0]
	for i in range(1, len(tables)):
		t = tables[i]
		drm = alignTables(reference, t)
		t = shiftTable(t, drm, False)

		tables[i] = t
		drms.append(drm)

	if verbose_output:
		print('Result:')
		print('DRM\tTable')
		print('-'*79)


	maxlen = 0
	for i in zip(drms, tables):
		if verbose_output:
			print('%+d' % i[0] + '\t', i[1])
		maxlen = max(maxlen, len(i[1]))


	# expand the tables to the same length
	for t in tables:
		
		d = maxlen - len(t)
		#print(t, len(t))

		for i in range(0,d):
			t.append(t[-1])

	# add them up
	finalTable = []
	for i in range(0, maxlen):
		val = 0
		for t in tables:
			val += t[i]

		val = float(val)
		val /= len(tables)
		val = int(val)

		finalTable.append(val)

	if verbose_output:
		print('-'*79)
		print('Final:\t', finalTable)

	return finalTable, drms


def compareSunkHarness(warperiod, subs, tgtType, wolfpack, torp_value):
	# create filenames	
	files = createFilenames(warperiod, subs, tgtType, wolfpack, torp_value)

	tables = []
	drms = []
	maxRolls = 0
	maxDrms = 0
	for f in files:
	
		t, d = compareShipsSunk(f)
		tables.append(t)
		drms.append(d)

		maxRolls = max(maxRolls, len(t))
		maxDrms = max(maxDrms, len(d))


	# make sure the are the same length!
	for i in range(0, len(tables)):
		if len(tables[i]) < maxRolls:
			pad = [tables[i][-1]] * (maxRolls - len(tables[i]))

			tables[i] += pad


	lines = []
	for t in zip(subs, tables, drms):
		lines.append(printTable(t[0], t[1], t[2]))


	if latex_output:
		print('\\begin{table}[htb]')
		targetStrings = {'c2' : 'Large Convoy', 'c1' : 'Small Convoy', 'loners' : 'Loners'}
		label = 'table:sunk.' + tgtType + '.torp' + str(torp_value)
		print('\\caption{\\label{' + label + '} Ships Sunk;  WP ' + str(warperiod) + ' -- ' + targetStrings[tgtType.lower()] + ', torpedo rating: ' + str(torp_value) + ' }')

		print('\\begin{tabular}{|l|' + maxRolls * ' c ' + '|' + maxDrms * ' c ' + '|}')
		print('\\hline')

		drmLabel = 'Elite Skipper DRM'
		if wolfpack:
			drmLabel = 'Wolfpack size DRM'
		print('\\multirow{2}{*}{Sub} & \\multicolumn{' + str(maxRolls) + '}{|c|}{ 1D10 Roll } & \\multicolumn{' + str(maxDrms) + '}{|c|}{\\multirow{2}{*}{' + drmLabel + '}} \\\\')
		
		l = '&'
		for i in range(0, maxRolls):
			l += '%2d' % i
			l += '&'
		for i in range(0, maxDrms-1):
			l += '&'
		l += '\\\\'
		print(l)

		print('\\hline')
		for l in lines:
			print(l)
		print('\\hline')
		print('\\end{tabular}')

		print('\\end{table}')
	else:


		print('-'*79)

		if wolfpack:
			print('WP ' + str(warperiod)  + ' - ' + tgtType + ' Wolfpack' + ' Torpedo value: ' + str(torp_value))
			print('Sub    Ships Sunk                                                   Wolfpack DRM')

		else:
			print('WP ' + str(warperiod)  + ' - ' + tgtType + ' Torpedo value: ' + str(torp_value))
			print('Sub    Ships Sunk                                                   Skipper DRM')

		for l in lines:
			print(l)



def comparePercentageHarness(warperiod, subs, tgtType, wolfpack, torp_value):
	# create filenames	
	files = createFilenames(warperiod, subs, tgtType, wolfpack,  torp_value)

	lines = []
	for f in files:
		for f2 in f:
			lines.append(comparePercentages2(f2))


	if latex_output:
		print('\\begin{table}[htb]')
		targetStrings = {'c2' : 'Large Convoy', 'c1' : 'Small Convoy', 'loners' : 'Loners'}

		label = 'table:effects.' + tgtType + '.torp' + str(torp_value)
		print('\\caption{\\label{' + label + '} Sub Effects;  WP ' + str(warperiod) + ' -- ' + targetStrings[tgtType.lower()] + ', torpedo rating: ' + str(torp_value) + ' }')

		print('\\begin{tabular}{|c|c|c|c|c|c|}')
		print('\\hline')
		print('Sub & Spotted & RTB & Damaged & Sunk & Promoted \\\\')
		print('\\hline')
		for l in lines:
			print(l)
		print('\\hline')
		print('\\end{tabular}')
		print('\\end{table}')

	else:
		#print('WP ' + str(warperiod) + ' - ' + tgtType)
		print('Sub Rating     Spotted           RTB       Damaged          Sunk      Promoted')
		for l in lines:
			print(l)

		print('-'*79)



def comparePercentages2(file):
	data = loadFile(file)

	damaged = [r.subsSpotted for r in data]
	damaged.sort()
	
	damageResult = getPercentageRolls(damaged, 1)

	sunk = [r.subsSunk for r in data]
	sunk.sort()
	sunkResult = getPercentageRolls(sunk, 0)

	rtb = [r.subsRTB for r in data]
	rtb.sort()
	rtbResult = getPercentageRolls(rtb, 2)

	spotted = [r.subsSpotted for r in data]
	spotted.sort()
	spottedResult = getPercentageRolls(spotted, 3)

	promoted = [r.subsPromoted for r in data]
	promoted.sort()
	promotedResult = getPercentageRolls(promoted, 9)


	# start line with sub rating
	sub = file.split('.')[1]

	f = sub[0] + '-' + sub[1] + '-' + sub[2] + '       '

	if output == 'latex':
		f += '& $' + spottedResult + '$'
		f += '& $' + rtbResult + '$'
		f += '& $' + damageResult + '$'
		f += '& $' + sunkResult + '$'
		if not wolfpack:
			skipper = int(file.split('.')[4][4])
			if skipper < 2:
				f += '& $' + promotedResult + '$'
			else:
				f += '&'
		else:
			f += '&'
		f += '\\\\'
	

	if output == 'html':
		f = '<tr><th nowrap scope="row">' + f + '</th>'
		if wolfpack:
			wolfpack_size = (file.split('.')[4][8:])
			f += '<td>' + wolfpack_size + '</td>'
		else:
			f += '<td />'

		f += '<td>' + spottedResult + '</td>'
		f += '<td>' + rtbResult + '</td>'
		f += '<td>' + damageResult + '</td>'
		f += '<td>' + sunkResult + '</td>'
		f += '<td>' + promotedResult + '</td>'
		f += '</tr>'


	if output == 'text':
		f += '% 10s    ' % spottedResult
		f += '% 10s    ' % rtbResult
		f += '% 10s    ' % damageResult
		f += '% 10s    ' % sunkResult
		if not wolfpack:
			skipper = int(file.split('.')[4][4])
			if skipper < 2:
				f += '% 10s    ' % promotedResult

	return f


def compareCombinedHarnessLatex(warperiod, subs, tgtType, wolfpack, torp_value):
	files = createFilenames(warperiod, subs, tgtType, wolfpack, torp_value)

	tables = []
	tablesSunk = []
	drms = []
	drmsSunk = []
	maxRolls = 0
	maxDrms = 0
	for f in files:
	
		t, d = compareTonnage(f)
		tables.append(t)
		drms.append(d)

		t2, d2 = compareShipsSunk(f)
		tablesSunk.append(t2)
		drmsSunk.append(d2)

		maxRolls = max(maxRolls, len(t))
		maxDrms = max(maxDrms, len(d))

		maxRolls = max(maxRolls, len(t2))
		maxDrms = max(maxDrms, len(d2))



	# make sure the are the same length!
	for i in range(0, len(tables)):
		if len(tables[i]) < maxRolls:
			pad = [tables[i][-1]] * (maxRolls - len(tables[i]))

			tables[i] += pad

	for i in range(0, len(tablesSunk)):
		if len(tablesSunk[i]) < maxRolls:
			pad = [tablesSunk[i][-1]] * (maxRolls - len(tablesSunk[i]))
			tablesSunk[i] += pad

	print('%-----------------------------------------------------------------')
	print('% WP' + str(warperiod) + ' - Torp value: ' + str(torp_value))
	if wolfpack:
		print('% Wolfpack attack on ' + tgtType)
	else:
		print('% Solo attack on ' + tgtType)
	print('%-----------------------------------------------------------------')


	print('\\begin{table}[htb]')
	print('\\centering')
	targetStrings = {'c2' : 'a large convoy (C2)', 'c1' : 'a small convoy (C1)', 'loners' : 'some loners'}
	label = 'table:' + tgtType + '.torp' + str(torp_value)
	if wolfpack:
		label += '.wolfpack'
	else:
		label += '.solo'

	caption = 'Combat result of '
	if wolfpack:
		caption += 'a wolfpack'
	else:
		caption += 'a single sub'
	caption += ' attack on '
	caption += targetStrings[tgtType.lower()]
	caption += ' in war period ' + str(warperiod)
	caption += ' with torpedo value $' + str(torp_value) + '$'

	print('\\caption{\\label{' + label + '} ' + caption + '}')

	print('\\begin{tabular}{|c|c|' + maxRolls * ' c ' + '|' + maxDrms * ' c ' + '|}')
	print('\\hline')

	drmLabel = 'Elite Skipper DRM'
	if wolfpack:
		drmLabel = 'Wolfpack size DRM'
	print('&\\multirow{2}{*}{Sub} & \\multicolumn{' + str(maxRolls) + '}{|c|}{ 1D10 Roll } & \\multicolumn{' + str(maxDrms) + '}{|c|}{\\multirow{2}{*}{' + drmLabel + '}} \\\\')
	
	l = '&&'
	for i in range(0, maxRolls):
		l += '%2d' % i
		l += '&'
	if wolfpack:
		for i in range(0, maxDrms):
			l += str(2+2*i) + '&'
	else:
		for i in range(0, maxDrms):
			l += '&'

	l = l[:-1]		
	l += '\\\\'
	print(l)

	# print tons 
	print('\\hline')
	header = '\\multirow{' + str(len(subs)) + '}{*}{Tons}&'
	for t in zip(subs, tables, drms):
		print(header + printTable(t[0], t[1], t[2]))
		header = '&'
	print('\\hline')

	# print sunk
	header = '\\multirow{' + str(len(subs)) + '}{*}{Sunk}&'
	for t in zip(subs, tablesSunk, drmsSunk):
		print(header + printTable(t[0], t[1], t[2]))
		header = '&'

	# end the table
	if output == 'latex':
		print('\\hline')
		print('\\end{tabular}')

	if output == 'html':
		print('</table>')




	# begin new table

	lines = []
	for f in files:
		for f2 in f:
			lines.append(comparePercentages2(f2))
	
	print('\\begin{tabular}{|c|c|c|c|c|c|}')
	print('\\hline')
	print('\\multicolumn{6}{|c|}{Combat Effects}\\\\')
	print('\\hline')
	print('Sub & Spotted & RTB & Damaged & Sunk & Promoted \\\\')
	lastsub = ''
	for l in lines:
		sub = l[0:5]
		if sub != lastsub:
			print('\\hline')
			lastsub = sub

			print('\\multirow{3}{*}{' + sub + '}' + l[6:])
		else:
			print(l[6:])

	print('\\hline')
	print('\\end{tabular}')
	print('\\end{table}')
	print('%-----------------------------------------------------------------')
	print('\\newpage')
	



def compareCombinedHarnessHtml(warperiod, subs, tgtType, wolfpack, torp_value):
	if output == 'text':
		return

	files = createFilenames(warperiod, subs, tgtType, wolfpack, torp_value)

	tables = []
	tablesSunk = []
	drms = []
	drmsSunk = []
	maxRolls = 0
	maxDrms = 0
	for f in files:
	
		t, d = compareTonnage(f)
		tables.append(t)
		drms.append(d)

		t2, d2 = compareShipsSunk(f)
		tablesSunk.append(t2)
		drmsSunk.append(d2)

		maxRolls = max(maxRolls, len(t))
		maxDrms = max(maxDrms, len(d))

		maxRolls = max(maxRolls, len(t2))
		maxDrms = max(maxDrms, len(d2))



	# make sure the are the same length!
	for i in range(0, len(tables)):
		if len(tables[i]) < maxRolls:
			pad = [tables[i][-1]] * (maxRolls - len(tables[i]))

			tables[i] += pad

	for i in range(0, len(tablesSunk)):
		if len(tablesSunk[i]) < maxRolls:
			pad = [tablesSunk[i][-1]] * (maxRolls - len(tablesSunk[i]))
			tablesSunk[i] += pad

	print('<!--')
	print('WP ' + str(warperiod) + ' Torp value: ' + str(torp_value))
	if wolfpack:
		print('Wolfpack attack on ' + tgtType)
	else:
		print('Solo attack on ' + tgtType)
	print('-->')



	caption = 'Combat result of '
	if wolfpack:
		caption += 'a wolfpack'
	else:
		caption += 'a single sub'
	caption += ' attack on '
	targetStrings = {'c2' : 'a large convoy (C2)', 'c1' : 'a small convoy (C1)', 'loners' : 'some loners'}
	caption += targetStrings[tgtType.lower()]
	caption += ' in war period ' + str(warperiod)
	caption += ' with torpedo value ' + str(torp_value)

	print('<h3>' + caption + '</h3>')
	print('<h4>Combat Result</h4>')
	print('<table class="table table-striped">')
	print('\t<thead class="thead-inverse">')
	print('\t\t<tr>')
	print('\t\t<th>Sub</th>')
	print('\t\t<th colspan="' + str(maxRolls) + '">Rolls</th>')

	if wolfpack:
		print('\t\t<th colspan="' + str(maxDrms) + '">Wolfpack Size</th>')
	else:
		print('\t\t<th colspan="' + str(maxDrms) + '">DRMs</th>')
	print('\t\t</tr>')
	print('\t\t<th />')

	for i in range(0, maxRolls):
		print('\t\t<th>%02d' % i + '</th>')

	if wolfpack:
		for i in range(0, maxDrms):
			print('\t\t<th>%2d' % (2+i*2) + '</th>')
	else:
		for i in range(0, maxDrms):
			print('\t\t<th>%+d' % i + '</th>')			

	print('\t</thead>')


	for t in zip(subs, tables, drms):
		print('\t\t' + printTable(t[0], t[1], t[2]))

		colspan = maxRolls + maxDrms + 1
		print('\t\t<td colspan"' + str(colspan) + '"Combat Effects</td>')

	# end this table
	if output == 'html':
		print('</table>')


	# begin new table 
	print('<h4>Combat Effects</h4>')
	print('<table class="table table-striped">')
	print('\t<thead class="thead-inverse">')
	print('\t\t<tr>')
	print('\t\t<th>Sub</th>')
	print('\t\t<th>WP Size</th>')
	print('\t\t<th>Spotted</th>')
	print('\t\t<th>RTB</th>')
	print('\t\t<th>Damaged</th>')
	print('\t\t<th>Sunk</th>')
	print('\t\t<th>Promoted</th>')
	print('\t\t</tr>')
	print('\t</th>')

	print('\t<tbody>')

	started = True
	for f in files:

		if not started:
			print('\t\t\t<tr><th /><td /><td /><td /><td /><td /><td /></tr>')
		else:
			started = False

		for f2 in f:

			l = comparePercentages2(f2)
			sp = l.find('-')-1
			sub = l[sp:sp+6]
			
			print('\t\t\t' + l)



	print('\t</tbody>')
	print('</table>')





if __name__ == '__main__':

	warperiod = 1
	subs = ('212', '332', '423', '533')
	tgtType = 'C2' #, 'C2')
	wolfpack = True
	torp_value = 0

	if output == 'text':
		compareTonnageHarness(warperiod, subs, tgtType, wolfpack, torp_value)
		compareSunkHarness(warperiod, subs, tgtType, wolfpack, torp_value)
		comparePercentageHarness(warperiod, subs, tgtType, wolfpack, torp_value)
	
	if output == 'latex':
		compareCombinedHarnessLatex(warperiod, subs, tgtType, wolfpack, torp_value)


	if output == 'html':
		compareCombinedHarnessHtml(warperiod, subs, tgtType, wolfpack, torp_value)
