#!/usr/bin/env python

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

import random

if __name__ == '__main__':

	random.seed(0)

	drm = 0
	dice = 2
	face = 10
	count = 10000
	highEnd = int(dice * face * 1.5) 

	trimLeft = False
	trimRight = True

	rolls = []
	for i in range(0, highEnd):
		rolls.append(0)


	for i in range(0,count):
		roll = 0
		for d in range(0, dice):
			roll += random.randint(0, face-1)

		roll += drm
		roll = max(0, roll)

		rolls[roll] += 1

	maxRoll = 0
	minRoll = count
	meanRoll = 0
	for r in rolls:
		maxRoll = max(maxRoll, r)
		minRoll = min(minRoll, r)
		meanRoll += r

	# trim the right side of the list
	if trimRight:
		while rolls[-1] == 0:
			rolls.pop()

	# trim the left side of the list
	offset = 0
	if trimLeft:
		while rolls[0] == 0:
			rolls.pop(0)
			offset += 1

	print(count, 'rolls of %dd' % dice + '%d' % face + ' with DRM %+d' % drm)
	for i in range(0, len(rolls)):

		s = "%4d" % rolls[i] + ' '
		
		c = round(float(rolls[i]) / maxRoll * 10)
		s += c * '*'

		if rolls[i] == maxRoll:
			s += ' <- Peak'

		print("%02d " % (i + offset), s)
