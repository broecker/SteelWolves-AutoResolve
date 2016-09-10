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

import sys
import random
import math

cups = {}

# global values
torpvalue = -1
bdienst = 0
asw_value = 0
air_cover = 'light'
base_straggle_level = 1 

# current ops area
red_boxes = 0



class Encounter:
	'''	Describes a single counter on the convoy display. Can be a ship, 
		aircraft, event. '''
	def __init__(self, type, nation, tons, defense, asw):
		self.type = type
		self.nation = nation
		self.tons = tons
		self.defense = defense
		self.asw = asw
		self.visible = False
		self.diligent = False
		self.validTarget = True
		self.damaged = False
		self.column = None

	def __repr__(self):
		if self.type == 'M':
			return self.type + str(self.tons) + 't (' + str(self.defense) + '-' + str(self.asw) + ')'
		else:
			return self.type + ' (' + str(self.defense) + '-' + str(self.asw) + ')'

	def rollForDamage(self):
		roll = random.randint(0, 9) + torpvalue
		result = 'none'

		if self.tons <= 4:
			if roll == 1:
				result = 'damage'
			if roll > 1:
				result = 'sunk'

		if self.tons > 4 and self.tons < 10:
			if roll == 2:
				result = 'damage'
			if roll > 2:
				result = 'sunk'

			if roll == 7:
				# special case
				roll2 = random.randint(0, 9)
				if roll2 == 8:
					print('IMPLEMENT_ME: Sub damaged')
				if roll2 == 9:
					r3 = random.randint(0, 9)
					if r3 >= 7:
						print('IMPLEMENT_ME: Sub sunk')
					else:
						print('IMPLEMENT_ME: Sub damaged RTB')


		if self.tons > 9 and self.tons < 18:
			if roll > 2:
				result = 'damage'
			if roll > 4:
				result = 'sunk'

		if self.tons > 17 and self.tons < 29:
			if roll > 3:
				result = 'damage'
			if roll > 5:
				result = 'sunk'

		if self.tons > 28 and self.tons < 37:
			if roll > 4:
				result = 'damage'
			if roll > 6:
				result = 'sunk'

		if self.tons > 36 and self.tons < 56:
			if roll > 5:
				result = 'damage'
			if roll > 7:
				result = 'sunk'

		if self.tons > 55:
			if roll > 6:
				result = 'damage'
			if roll == 9:
				result = 'sunk'

		if result == 'damage':

			if self.damaged:
				result = 'sunk'
			
			self.damaged = True

		if result == 'sunk':
			#remove from column etc 

			if self.column:
				i = self.column.targets.index(self)
				self.column.targets[i] = None
				self.column = None


		print('Rolling damage for', self, ':', roll, '(', torpvalue, 'torp value) ->', result)
		return result


class Column:
	''' A column in the convoy'''
	def __init__(self, convoy, name, entry, max_subs):
		self.convoy = convoy
		self.name = name
		self.targets = []
		self.entry = entry
		self.sub_positions = []
		self.max_subs = max_subs

	def __repr__(self):
		return self.name + ' (' + str(self.entry) + ')'

	def setAdjacent(self, adj):
		self.adjacent = adj

	def seed(self, cup, count):
		if len(cup) < count:
			print('Warning, draw amount exceeds cup!')
			self.targets = cup
		else:
			self.targets = random.sample(cup, count)

		random.shuffle(self.targets)
		self.hideAll()

	def hideAll(self):
		for t in self.targets:
			if t:
				t.visible = False
				t.column = self

	def revealAll(self):
		for t in self.targets:
			if t:
				t.visible = True

		return self.targets

	def revealCounters(self, n, tryNeigbours=True):
		result = []

		print('Revealing', n, 'counters in column', self.name)

		if self.countHidden() < n:
			print ('Warning, not enough hidden counters remaining in column', self.name)
						
			if tryNeigbours:
				o = n - self.countHidden()

				# split the overflow between adjacent columns
				l = round(o / len(self.adjacent))
				r = o - l

				result += self.adjacent[0].revealCounters(l, False)
				if r > 0:
					result += self.adjacent[1].revealCounters(r, False)

			result += self.revealAll();
		else:
			n = int(n)
			revealed = random.sample(self.targets, n)
			for r in revealed:
				if r:
					r.visible = True

			result = revealed

		return result

	def getASWValue(self):
		#return sum(n.asw for n in self.targets if (n.visible and n.validTarget and (not n.damaged)))
		r = 0
		for n in self.targets:
			if n and n.visible and n.validTarget and not n.damaged:
				r += n.asw

		return r


	def getVisibleTargets(self):
		return [t for t in self.targets if t and t.visible and t.validTarget]		

	def countHidden(self):
		return sum(t.visible == False for t in self.targets if t)

	def tryAndPlaceSub(self, sub):
		if (self.entry == None or sub.tac_roll > self.entry) and len(self.sub_positions) < self.max_subs:
			self.sub_positions.append(sub)
			sub.column = self

			print('Placed sub',sub.name,'in column', self.name,' [ roll:', sub.tac_roll, '>', self.entry,']')

			return True;
		else:
			return False;

	def printColumn(self):
		''' prints the column horizontally'''

		counters = []
		for c in self.targets:

			if c == None:
				counters.append('  ')
			else:

				if c.visible:
					counters.append(c.type)
				else:
					counters.append('**')

		subs = [s for s in self.sub_positions]

		print(self.name, counters, subs)

class Convoy:
	'''Convoys of different size hold different columns'''
	def __init__(self, type):
		self.columns = []
		self.straggle_level = 0



		if type == 'C1':
			print('not yet implemented')



		if type == 'C2':
			# fill in columns [13.24]
			os = Column(self, 'Outer Starboard', None, 3)
			s = Column(self, 'Starboard', 7, 2)
			cs = Column(self, 'Center Starboard', 9, 1)
			cp = Column(self, 'Center Port', 9, 1)
			p = Column(self, 'Port', 7, 2)
			op = Column(self, 'Outer Port', None, 3)

			os.setAdjacent([s])
			s.setAdjacent([os,cs])
			cs.setAdjacent([s,cp])
			cp.setAdjacent([cs, p])
			p.setAdjacent([cp,op])
			op.setAdjacent([p])

			self.columns = [os, s, cs, cp, p, op]


			os.seed(cups['outer'], 5)
			s.seed(cups['inner'], 5)
			cs.seed(cups['center'], 5)
			cp.seed(cups['center'], 5)
			p.seed(cups['inner'], 5)
			op.seed(cups['outer'], 5) 

		if type == 'Loner':
			print('Loner not yet implemented')

		if type == 'TF':
			print('Task Force not yet implemented')

	def printColumns(self):	
		for c in self.columns:
			c.printColumn()



	def placeSub(self, sub):
		sub.performTacRoll()


		# sorted columns by tac entry roll
		cols = sorted(self.columns, key=lambda x:(x.entry or 0))
		
		# try and place the sub as close to the center as possible
		for c in cols:
			if c.tryAndPlaceSub(sub):
				break;


	def getTotalASWValue(self):
		a = 0
		for c in self.columns:
			a += c.getASWValue()

		return math.ceil(a)


	def counterattack(self, sub, reattack, result):
		# 14.2
		# totalASW = self.getTotalASWValue()

		# get asw value in current and adjacent columns
		immediateColumns = [sub.column] + sub.column.adjacent
		asw = sum(c.getASWValue() for c in immediateColumns)

		# find remote available asw values from aircraft or cvs
		for c in self.columns:
			if c not in immediateColumns:
				for t in c.targets:
					if t and t.visible and (t.type == 'AC' or t.type == 'CV'):
						asw += t.asw

		asw += red_boxes
		asw += asw_value


		defense = sub.defenseRating + sub.skipper
		if sub.inexperienced:
			defense -= 1

		diff = asw - defense
		print('Counterattack, red boxes:', red_boxes, 'global asw:', asw_value)
		print('Total ASW', asw, 'defense', defense, 'diff', diff)

		if diff < 0:
			print('No counterattack, diff:', diff)
		else:
			# counterattack
			roll = random.randint(0,9)
			roll += sub.isDamaged()
			if reattack:
				roll += 1
			if sub.spotted:
				roll += 1


			if roll > 12:
				roll = 12

			if asw > 8:
				asw = 8
			asw = int(asw)

			print('Counterattack roll', roll, 'with asw', asw)
			# counterattack table [14.2C]
			# format: [asw] ([spotted], [damaged], [damagedRTB], [damagedRTB+], [sunk-], [sunk])
			table =	(	([9], [10], [11], [], [], [12]),
						([8], [9,10], [], [11], [], [12]),
						([8], [9,10], [], [11], [], [12]),
						([7], [8,9], [], [10], [], [11,12]),
						([7], [8,9], [], [10], [], [11,12]),
						([4,5], [6,7], [8], [9], [10], [11,12]),
						([4,5], [6,7], [8], [9], [10], [11,12]),
						([3,4], [5,6], [7], [8], [9],[10,11,12]),
						([2,3], [4,5], [], [6,7], [8], [9,10,11,12])
					)

			row = table[asw]
			
			if roll < row[0][0]:
				print('No effect.')
			else:

				if roll in row[0]:
					sub.spotted = True
					print('Sub', sub, 'spotted')

				if roll in row[1]:
					sub.takeDamage(False)
				if roll in row[2]:
					sub.takeDamage(True)

				if roll in row[3]:
					roll2 = random.randint(0, 9)
					if roll2 >= 7:
						sub.sink()
					else:
						sub.takeDamage(True)

				if roll in row[4]:
					roll2 = random.randint(0,9)
					if roll2 >= 4:
						sub.sink()
					else:
						sub.takeDamage(True)

				if roll in row[5]:
					sub.sink()


				result.addSub(sub)

		return result


class CombatResult:
	'''Describes and stores the outcome of a single sub vs convoy attack'''
	def __init__(self, sub):
		self.sub = sub
		self.sunk = 0
		self.tons = 0
		self.damaged = 0

		self.subDamaged = 0
		self.subSunk = 0
		self.subSpotted = 0
		self.subRTB = 0

	def printSummary(self):
		print('Sub',self.sub, 'sunk', self.sunk, 'ships for', self.tons, 'tons. Status:', self.subDamaged, 'damaged', self.subSpotted, 'spotted', self.subSunk, 'sunk', self.subRTB, 'RTB')

	def addSub(self, sub):
		if sub.isDamaged():
			self.subDamaged += 1
		if sub.isSunk():
			self.subSunk += 1
		else:
			if sub.spotted:
				self.subSpotted += 1
			if sub.rtb:
				self.subRTB += 1 

	def combine(self, results):
		for r in results:
			self.sunk += r.sunk
			self.tons += r.tons 
			self.damaged += r.damaged
			self.subDamaged += r.subDamaged
			self.subSunk += r.subSunk
			self.subSpotted += r.subSpotted
			self.subRTB += r.subRTB



class Sub:
	def __init__(self, name, attack, defense, tactical, skipper):
		self.name = name
		self.attackRating = attack
		self.defenseRating = defense
		self.tacRating = tactical
		self.skipper = skipper
		self.crashDiveRating = 3
		self.inexperienced = False
		self.spotted = False
		self.damage = 0
		self.rtb = False

	def __repr__(self):
		return self.name + '(' + str(self.attackRating) + '-' + str(self.defenseRating) + '-' + str(self.tacRating) + ')'

	def performTacRoll(self):
		self.tac_roll = random.randint(0,9) + self.tacRating + self.skipper

	def revealCounters(self):
		return self.column.revealCounters(self.tacRating, True)

	def crashDive(self):
		roll = random.randint(0, 9)
		if self.inexperienced:
			roll += 1

		if roll < self.crashDiveRating:
			self.spotted = True
			print('Sub', self.name, 'fails to crash dive, becomes spotted')
			return False
		else:
			print('Sub', self.name, 'crash dives!')
			return True

	def takeDamage(self, rtb=False):
		self.damage += 1
		
		rtbText = ''
		if rtb:
			self.rtb = True
			rtbText = ' returns to base'

		print('Sub ' + str(self.name) + ' takes damage' + rtbText)

	def isDamaged(self):
		return self.damage > 0

	def isSunk(self):
		return self.damage == -1

	def sink(self):
		self.damage = -1
		print('Sub ' + str(self.name) + 'sinks')

	def attack(self, convoy):
		result = CombatResult(self)

		# get revealed targets in the current and adjacent columns
		revealed = self.column.getVisibleTargets()
		for a in self.column.adjacent:
			revealed += a.getVisibleTargets()


		tdcCount = min(len(revealed), self.tacRating)


		print('Sub', self.name, 'has', len(revealed), 'potential targets, placing', tdcCount, 'TDC markers, tactical rating:', self.tacRating)
		


		# sorts targets by tonnage and if they are damaged
		def getTargetPriority(tgt):
			p = tgt.tons;
			if tgt.damaged:
				p += int(tgt.tons/2)
			return p

		revealed.sort(key=getTargetPriority, reverse=True)
		revealed = revealed[0:tdcCount]

		# set TDC markers [14.14]
		for r in revealed:
			r.tdc = drawTDCCounter()
			print('Target/TDC:', r, r.tdc)


		targets = []

		# split combat value in 4's and assign targets [14.15]
		cv = self.attackRating
		tdcIndex = 0

		while cv > 0 and len(revealed) > 0 and tdcIndex < len(revealed):
			# place a TDC on a counter
			
			r = revealed[tdcIndex]
			r.tdc = drawTDCCounter()
			targets.append(r)

			tdcIndex += 1
			cv -= 4 


		# 14.15 targeted escorts

		# 14.16 attack
		attackValue = self.attackRating + self.skipper + torpvalue + convoy.straggle_level
	
		for t in targets:
			aswValue = self.column.getASWValue()
			for a in self.column.adjacent:
				aswValue += a.getASWValue()

			columnMod = 0
			if self.column != t.column:
				columnMod = 1
			damageMod = 0
			if t.damaged:
				damageMod = -1

			print('Combat vs', t)
			print('Attack :', attackValue, '[', self.attackRating, 'attack',self.skipper,'skipper',torpvalue,' torp rating', convoy.straggle_level, 'convoy straggle]')
			print('Defense:', aswValue, '[', aswValue, 'ASW', t.tdc,'TDC', columnMod, 'column mod',damageMod, ' damaged]')
			aswValue = aswValue + t.tdc + columnMod + damageMod


			diff = attackValue - aswValue
			roll = random.randint(0, 9)
			if self.inexperienced:
				roll += 1

			if roll <= diff:
				print('Diff:',diff,'Roll:', roll, 'Target hit')

				# consult attack results table here
				d = t.rollForDamage()

				if d == 'sunk':
					result.sunk += 1
					result.tons += t.tons

				if d == 'damage':
					result.damaged += 1
 


			else:
				print('Diff:',diff,'Roll:', roll, 'Target missed')

		# remove tdc markers again
		for r in revealed:
			r.tdc = None



		return result


class Wolfpack:
	def __init__(self, name, subs):
		self.subs = subs 
		self.name = name 
	def __repr__(self):
		return 'Wolfpack ' + self.name +'(' + str(len(self.subs)) + ' boats)'



def getEvent(type) : 
	e = Encounter(type, None, None, None, None);
	e.validTarget = False;
	return e

def getAircraft(nation, asw):
	ac = Encounter('AC', nation, None, None, asw);
	ac.validTarget = False
	return ac

def getWarship(type, name, tons, defense, asw):
	ws = Encounter(type, 'british', tons, defense, asw)
	ws.name = name
	return ws

def getDD(nation, tons, diligent):
	dd = Encounter('DD', nation, tons, random.randint(6,7), random.randint(1,3))
	dd.diligent = diligent
	return dd

def getES(nation, diligent):
	es = Encounter('ES', nation, 2, 2, 1)
	es.diligent = diligent
	return es

def getAM(nation):
	return Encounter('AM', nation, 2, 2, 1)
	
def getMerchant(nation, hvy):
	m = Encounter('M', nation, 0, 0, 0);


	try:
		a = getMerchant._light

	except AttributeError:

		# lgt merchant distribution
		# 8x 1t 0-0
		# 16x 2t 0-0/1-0
		# 9x 3t 0-0/1-0
		# 20x 4t 1-0
		# 35x 5 1-0/3-0	

		# stored as weight-defense
		getMerchant._light = []
		for i in range(0,8):
			getMerchant._light.append((1, 0))
		for i in range(0,16):
			getMerchant._light.append((2,0))
		for i in range(0,9):
			getMerchant._light.append((3,random.randint(0,1)))
		for i in range(0,20):
			getMerchant._light.append((4,1))
		for i in range(0,35):
			getMerchant._light.append((5,random.randint(1,3)))
		random.shuffle(getMerchant._light)



		# hvymerchant distribution:
		# 14x 6t 0-0/2-0
		# 16x 7t 1-0/2-0
		# 11x 8t 2-0
		# 9x 9t 3-0
		# 5x 10t 3-0
		# 2x 11t 3-0
		# 2x 12t 3-0
		# 14t 3-0
		# 17t 3-0
		# 20t 4-0
		getMerchant._heavy =[]
		for i in range(0, 14):
			getMerchant._heavy.append((6,random.randint(0,2)))
		for i in range(0, 16):
			getMerchant._heavy.append((7,random.randint(1,2)))
		for i in range(0,11):
			getMerchant._heavy.append((8,2))
		for i in range(0,9):
			getMerchant._heavy.append((9,3))
		for i in range(0,5):
			getMerchant._heavy.append((10,3))
		getMerchant._heavy.append((11,3))
		getMerchant._heavy.append((11,3))
		getMerchant._heavy.append((12,3))
		getMerchant._heavy.append((12,3))
		getMerchant._heavy.append((14,3))
		getMerchant._heavy.append((17,3))
		getMerchant._heavy.append((20,4))
		random.shuffle(getMerchant._heavy)

	if hvy == True:
		s = random.choice(getMerchant._heavy)
		m.tons = s[0]
		m.defense = s[1]
	else:
		s = random.choice(getMerchant._light)
		m.tons = s[0]
		m.defense = s[1]
	return m;

def getSV(nation, tons):
	return Encounter('SV', nation, tons, 0, 0)

def getFV():
	return Encounter('FV', 'british', 1, 0, 0);

def getMerchants(count, nation, heavy):
	ms = []
	for i in range(0, count):
		ms.append(getMerchant(nation, heavy))
	return ms

def getDDs(count, nation, tons, diligent):
	dds = []
	for i in range(0, count):
		dds.append(getDD(nation, tons, diligent))
	return dds

def getESs(count, nation, diligent):
	es = []
	for i in range(0, count):
		es.append(getES(nation, diligent))
	return es

def seedCup(config):
	''' Note the config is just the column of a single cup/wp read top to bottom.
		Fill in zeros for no value'''
	cup = []

	if len(config) < 57:
		print('error -- configuration vector wrong size!')

	# events [0, 1]
	cup.append(getEvent('Event'))
	if config[1]:
		cup.append(getEvent('Draw Liner'))

	# convoy/loner aircraft [2, 11]
	if config[2]:
		cup.append(getAircraft('british', 0.5))
	# ... more 


	# convoy/loner warships [12, 33]
	# note: these values are just placeholders for now
	if config[12]:
		cup.append(getWarship('CV', 'Courageous', 27, 4, 0))
	if config[13]:
		cup.append(getWarship('CVE', 'Avenger', 15, 4, 0))
	if config[14]:
		cup.append(getWarship('CV', 'Audacity', 20, 6, 1))
	if config[15]:
		cup.append(getWarship('CA', 'Malaya', 10, 8, 0))
	if config[16]:
		cup.append(getWarship('CA', 'Ramilles', 10, 8, 1))
	if config[17]:
		cup.append(getWarship('CL', 'D 6t', 6, 4, 1))

	if config[18]:
		cup.append(getAM('british'))
	cup += getDDs(config[19], 'british/aus/greek/nor', 1, False)
	cup += getDDs(config[20], 'british/aus/netherland/vichy/poland', 2, False)
	cup += getESs(config[21], 'british/nor/vichy/poland', False)
	cup += getDDs(config[22], 'british', 2, True)
	cup += getESs(config[23], 'british', True)
	cup += getDDs(config[24], 'canadian', 2, False)
	cup += getDDs(config[25], 'canadian', 2, True)

	#CTs here

	cup += getDDs(config[28], 'french', 2, False)
	if config[29]:
		cup.append(Encounter('TB', 'french', 1, 1, 1))

	cup += getDDs(config[30], 'us', 1, False)
	cup += getDDs(config[31], 'us', 2, False)



	# merchants [34, 56]
	cup += getMerchants(config[34], 'british', True)
	cup += getMerchants(config[35], 'british', False)
	cup += getMerchants(config[36], 'french', True)
	cup += getMerchants(config[37], 'french', False)
	cup += getMerchants(config[38], 'nor/dutch/belg', True)
	cup += getMerchants(config[39], 'nor/dutch/belg', False)

	# [40]
	cup += getMerchants(config[40], 'canadian', True)
	cup += getMerchants(config[41], 'canadian', False)
	cup += getMerchants(config[42], 'danish/finnish', True)
	cup += getMerchants(config[43], 'danish/finnish', False)
	cup += getMerchants(config[44], 'swedish', True)
	cup += getMerchants(config[45], 'swedish', False)
	cup += getMerchants(config[46], 'panamian', True)
	cup += getMerchants(config[47], 'panamian', False)
	cup += getMerchants(config[48], 'greek', True)
	cup += getMerchants(config[49], 'greek', False)

	# [50]
	cup += getMerchants(config[50], 'us/brazil/soviet', True)
	cup += getMerchants(config[51], 'us/brazil/soviet', False)
	
	if config[52]:
		cup.append(Encounter('CM', 'british', 7, 4, 1))


	if config[53] > 0:
		cup.append(getSV('finnish', 2))
	if config[54] > 0:
		cup.append(getSV('us', 2))

	if config[55]:
		cup.append(getSV('british', 1))
	if config[56]:
		cup.append(getFV())


	#print(cup);

	return cup


def printCup(cup):
	for c in cup:
		print(c)

def seedTDCCup():
	cups['tdc'] = [4, -4]

	for i in range(0, 3):
		cups['tdc'].append(3)
		cups['tdc'].append(-3)

	for i in range(0,7):
		cups['tdc'].append(-2)
		cups['tdc'].append(2)
	for i in range(0,8):
		cups['tdc'].append(-1)
		cups['tdc'].append(1)
	for i in range(0, 10):
		cups['tdc'].append(0)

	random.shuffle(cups['tdc'])

def drawTDCCounter():
	return random.choice(cups['tdc'])


# This class provides the functionality we want. You only need to look at
# this if you want to know how this works. It only needs to be defined
# once, no need to muck around with its internals.
class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration
    
    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args: # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False



def seedCups(wp):
	cups['loner'] = []
	cups['outer'] = []
	cups['inner'] = []
	cups['center'] = []
	cups['west inner'] = []
	cups['west outer'] = []


	# WP1 seed
	for case in switch(wp):
		if case(1):
			cups['loner'] = seedCup((1,1,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,5,14,1,2,2,3,0,0,0,3,0,2,0,0,1,1,0,0,0,1,0,1,1))
			cups['outer'] = seedCup((1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,1,1,0,1,0,0,0,0,1,1,0,0,0,0,3,12,0,2,2,5,0,0,0,2,0,1,0,0,0,1,0,0,0,0,0,0,0))
			cups['inner'] = seedCup((1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,1,0,0,1,0,0,0,0,0,1,0,0,0,0,0,7,8,0,1,1,3,0,1,0,1,1,1,0,0,0,2,0,0,0,0,0,0,0,0))
			cups['center'] = seedCup((1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,13,5,1,0,4,2,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0))
			break;
		if case(2):
			cups['loner'] = seedCup((1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,6,9,0,1,3,6,0,1,0,2,0,2,0,0,0,3,0,0,0,1,0,1,1))
			cups['outer'] = seedCup((1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,1,1,0,0,0,0,0,0,0,0,0,0,0,4,12,0,1,1,4,0,0,0,3,0,1,0,0,0,1,0,0,0,0,0,0,0))
			cups['inner'] = seedCup((1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,9,9,1,0,3,2,0,0,0,1,0,1,0,1,0,1,0,0,0,0,0,0,0))
			cups['center'] = seedCup((1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,16,5,0,0,3,1,1,0,1,0,1,0,0,0,1,0,0,0,0,0,0,0,0))
			break;
		if case():
			print('wp 3+ not yet implemented!')


	print('loners: ', len(cups['loner']))
	print('outer : ', len(cups['outer']))
	print('inner : ', len(cups['inner']))
	print('center: ', len(cups['center']))
	print('west inner: ', len(cups['west inner']))
	print('west outer: ', len(cups['west outer']))

	#printCup(cups['loner'])
	

# from http://stackoverflow.com/questions/15389768/standard-deviation-of-a-list
def mean(data):
    """Return the sample arithmetic mean of data."""
    n = len(data)
    if n < 1:
        raise ValueError('mean requires at least one data point')
    return sum(data)/n # in Python 2 use sum(data)/float(n)

def _ss(data):
    """Return sum of square deviations of sequence data."""
    c = mean(data)
    ss = sum((x-c)**2 for x in data)
    return ss

def pstdev(data):
    """Calculates the population standard deviation."""
    n = len(data)
    if n < 2:
        raise ValueError('variance requires at least two data points')
    ss = _ss(data)
    pvar = ss/n # the population variance
    return pvar**0.5

def summarizeResults(results):
	subsSunk = 0
	subsDamaged = 0
	subsSpotted = 0
	subsRTB = 0

	shipsSunk = []
	shipsDamaged = []
	shipsTonnage = []

	for r in results:
		if r.subSunk:
			subsSunk += 1
		if r.subSpotted:
			subsSpotted += 1
		if r.subDamaged:
			subsDamaged += 1
		if r.subRTB:
			subsRTB += 1

		shipsSunk.append(r.sunk)
		shipsDamaged.append(r.damaged)
		shipsTonnage.append(r.tons)


	shipsSunk.sort()
	shipsTonnage.sort()

	minSunk = 100
	maxSunk = 0
	meanSunk = 0.0
	for s in shipsSunk:
		meanSunk += s
		minSunk = min(minSunk, s)
		maxSunk = max(maxSunk, s)

	devSunk = pstdev(shipsSunk)
	meanSunk /= len(shipsSunk)

	minTons = 100
	maxTons = 0
	meanTons = 0.0
	for t in shipsTonnage:
		meanTons += t
		minTons = min(minTons, t)
		maxTons = max(maxTons, t)

	devTons = pstdev(shipsTonnage)
	meanTons /= len(shipsTonnage)


	print('Subs spotted:', subsSpotted, '/', len(results))
	print('Subs damaged:', subsDamaged, '/', len(results))
	print('Subs sunk:', subsSunk, '/', len(results))
	print('Subs RTB:', subsRTB, '/', len(results))

	print('Ships sunk:', meanSunk, '[', minSunk, '-', maxSunk, '], mean', meanSunk, '/', devSunk)
	print('Ships tonnage:', meanTons, '[', minTons, '-', maxTons, '] mean', meanTons, '/', devTons)


def createTable(results):
	'''This method tries to fit the result data with a standard distribution of
		lots of 2d10 rolls and create a table from it.'''
	# this is based on a 2d10 distribution:
	# 2d10 - relative probability
	# 00 	0.01
	# 01 	0.02
	# 02 	0.03
	# 03 	0.04
	# 04 	0.05
	# 05 	0.06
	# 06 	0.07
	# 07 	0.08
	# 08 	0.09
	# 09 	0.10
	# 10 	0.09
	# 11 	0.08
	# 12 	0.07
	# 13 	0.06
	# 14 	0.05
	# 15 	0.04
	# 16 	0.03
	# 17 	0.02
	# 18 	0.01

	# first, sort the data by tons sunk
	results = sorted(results, key=lambda r: r.tons)

	tonnage = {}

	for r in results:
		t = str(r.tons)
		try:
			tonnage[t] += 1
		except KeyError:
			tonnage[t] = 1

	sortedTons = []
	for tons, count in tonnage.items():
		sortedTons.append((int(tons),count))
	sortedTons = sorted(sortedTons, key=lambda t: t[0])

	minTons = 100
	maxTons = 0

	minResult = 100
	maxResult = 0

	allTons = 0
	allResults = 0

	for st in sortedTons:
		minTons = min(minTons, st[0])
		maxTons = max(maxTons, st[0])
		minResult = min(minResult, st[1])
		maxResult = max(maxResult, st[1])

		allTons += st[0]
		allResults += st[1]

	

	# find the peak
	st2 = sorted(sortedTons, key=lambda x:x[1])
	peak = st2[-1]
	#print('Peak:', peak)

	if peak[0] == 0:
		nlf = float(peak[1]) / len(results)
		print('0t-peak:', peak[1], '(%0.2f)' % nlf)
		while peak[0] == 0:
			st2.pop()
			peak = st2[-1]		

	print('Peak:', peak)


	print('Items:', len(sortedTons))
	print('Range:', minTons,'->',maxTons)
	print('Result range:', minResult, '->', maxResult)


	print('Attack tonnage distribution:')
	for t,c in sortedTons:
		s = int(round(float(c) / peak[1] * 10))
		s = s * '*'

		if c == peak[1]:
			s += ' <- Peak'

		print(t,c,s)


def writeResults(filename, results):

	f = open(filename, 'w')
	f.write('# name, tgt sunk, tgt tons, subsDmgd, subsSunk, subsSpotted, subsRTB\n')
	for r in results:
		f.write(str(r.sub) + ',' + str(r.sunk) + ',' + str(r.tons) + ',' + str(r.subDamaged) + ',' + str(r.subSunk) + ',' + str(r.subSpotted) + ',' + str(r.subRTB) + '\n')

	f.close()


def diligentEscortTable(sub):
	roll = random.randint(0, 9)
	if sub.inexperienced:
		roll += 1

	if roll == 6:
		sub.spotted = True
	if roll == 7:
		sub.takeDamage(False)
	if roll == 8:
		sub.takeDamage(True)
	if roll > 8:
		sub.sink()


def attackRound(convoy, subs, combatRound):
	attackResults = []
	for sub in subs:
		# reveal counters [14.12]
		revealed = sub.revealCounters()

		for r in revealed:
			if r and r.type == 'AC':
				print('Found aircraft!')

				if air_cover == 'light' and random .randint(0,9) > 4:
					# replace with new draw
					print('Light air cover, replacing AC with new draw')
					print('TODO!')

			if r and r.type == 'Event':
				print('Found event, ignoring it')

				# ignore events?

			if r and r.diligent:
				print('Found diligent escort')
				if not sub.crashDive():
					# roll for damage from diligent escort
					diligentEscortTable(sub)


		# set tdcs [14.14]
		seedTDCCup()
		combatResult = sub.attack(convoy)

		reAttack = False
		if combatRound > 1:
			reAttack = True

		combatResult = convoy.counterattack(sub, reAttack, combatResult)

		attackResults.append(combatResult)

	if len(attackResults) == 1:
		return attackResults[0]
	else:
		# combine all attacks into one result
		cr = CombatResult(Wolfpack('WF' + str(i), subs))
		cr.combine(attackResults)
		return cr




def attackC2():
	print('Attacking large convoy (C2)')

	subcount = 1

	results = []
	seedCups(1)

	for i in range(0, 1000):

		c2 = Convoy('C2')
		c2.straggle_level = base_straggle_level

		subs = []
		for s in range(0, subcount):

			name = 'U-' + str(i)
			if subcount > 1:
				name += '.' + str(s)

			sub = Sub(name, 5, 3, 3, 0)
			c2.placeSub(sub)
			subs.append(sub)



		combatResultRound1 = attackRound(c2, subs, 1)


		# [14.3] Voluntary withdrawal
		# in our case all RTB, damaged and spotted subs
		subs = [s for s in subs if not (s.rtb or s.isDamaged() or s.spotted)]

		if len(subs) == 0:
			print('No valid subs remaining for re-attack, breaking off the attack')
		else:


			# [14.4] Re-attack rounds

			# [29.3] Check for straggle increase
			tgt = combatResultRound1.sunk + combatResultRound1.damaged
			roll = random.randint(0, 9)	

			if roll < tgt or roll == 0:
				print('Convoy straggle level increases')
				c2.straggle_level += 1

			if roll == 9:
				print('Convoy straggle level decreases')
				c2.straggle_level = max(c2.straggle_level-1, 0)


			# convoy is large -- check for scatter
			combatResultRound2 = attackRound(c2, subs, 2,)
			combatResultRound1.combine([combatResultRound2])


		results.append(combatResultRound1)



	#c2.printColumns()
	#

	for r in results:
		r.printSummary() 

	summarizeResults(results)
	#writeResults('c2-wp1.csv', results)
	createTable(results)

def parseCommandLine():
	if len(sys.argv) == 1:
		return

	for c in range(1,len(sys.argv)):
		v = sys.argv[c]

		print(c)


if __name__ == '__main__':
	random.seed()
	parseCommandLine()

	seedTDCCup()

	attackC2()
