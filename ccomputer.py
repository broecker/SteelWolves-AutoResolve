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
import random
import math

cups = {}

# global values
class GlobalValues:
	def __init__(self):
		self.torp_value = -1
		self.bdienst = 0
		self.asw_value = 0
		self.air_cover = 'light'
		self.base_straggle_level = 1
		self.red_dots = 0
		self.attackIterations = 3000
		self.verbose_combat = False

	def setWP(self, wp):

		if wp == 1:
			self.asw_value = 0
			self.torp_value = -1
			self.straggle_level = 1
			self.red_dots = random.choice([0, 0, 0, 1, 2])

		if wp == 2:
			self.asw_value = 1
			self.torp_value = random.choice((0, 0, 0, +1))
			self.straggle_level = 1
			self.red_dots = random.choice([0, 0, 0, 1, 2])

		if wp == 3:
			self.asw_value = 1
			self.torp_value =random.choice((0,1))
			self.red_dots = random.choice([0, 0, 0, 1, 2, 2, 3])
		if wp == 4:
			self.asw_value = random.choice((1,1,2,2))
			self.torp_value = random.choice((0,0,1,1,1,1,2,2))
			self.red_dots = random.choice([0, 0, 0, 0, 1, 1, 2, 3, 3, 3])
		if wp == 5:
			self.asw_value = 2
			self.torp_value = random.choice((1,1,2,2))
			self.red_dots = random.choice([0, 1, 1, 2, 2, 3, 3, 3, 3, 3])

		print('Set global values to: WP:', wp, 'ASW:', self.asw_value, ' torp:', self.torp_value, 'red area:', self.red_dots)

globals = GlobalValues()


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
		self.sunk = False
		self.column = None
		self.fast = False

	def __repr__(self):
		if self.type == 'M':
			return self.type + str(self.tons) + 't (' + str(self.defense) + '-' + str(self.asw) + ')'
		else:
			return self.type + ' (' + str(self.defense) + '-' + str(self.asw) + ')'

	def rollForDamage(self, sub):
		roll = random.randint(0, 9) + globals.torp_value
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
					sub.takeDamage(False)
				if roll2 == 9:
					r3 = random.randint(0, 9)
					if r3 >= 7:
						sub.sink()
					else:
						sub.takeDamage(True)


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
			self.sunk = False

		if result == 'sunk':
			#remove from column etc 

			if self.column:
				i = self.column.targets.index(self)
				self.column.targets[i] = None
				self.column = None

			self.damaged = False
			self.sunk = True


		if globals.verbose_combat:
			print('Rolling damage for', self, ':', roll, '(', globals.torp_value, 'torp value) ->', result)
		return result


	def isValidTarget(self):
		return not (self.type == 'Event' or self.type == 'Draw Liner')

class Column:
	''' A column in the convoy'''
	def __init__(self, convoy, name, entry, max_subs, draw_cup, column_size):
		self.convoy = convoy
		self.name = name
		self.targets = []
		self.entry = entry
		self.sub_positions = []
		self.max_subs = max_subs
		self.draw_cup = draw_cup

		self.seed(column_size)


	def __repr__(self):
		return self.name + ' (' + str(self.entry) + ')'

	def setAdjacent(self, adj):
		self.adjacent = adj

	def seed(self, count):
		if len(self.draw_cup) < count:
			print('Warning, draw amount exceeds cup!')
			self.targets = self.draw_cup
		else:
			self.targets = random.sample(self.draw_cup, count)

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

		if globals.verbose_combat:
			print('Revealing', n, 'counters in column', self.name)

		if self.countHidden() < n:
			if globals.verbose_combat:
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

	def hasFreeSubSlot(self):
		return len(self.sub_positions) < self.max_subs

	def tryAndPlaceSub(self, sub):
		if (self.entry == None or sub.tac_roll > self.entry) and self.hasFreeSubSlot():
			self.sub_positions.append(sub)
			sub.column = self

			if globals.verbose_combat:
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
			# fill in columns [13.24]
			os = Column(self, 'Outer Starboard', None, 2, cups['outer'], 6)
			s = Column(self, 'Starboard', 9, 1, cups['inner'], 6)
			p = Column(self, 'Port', 9, 1, cups['inner'], 6)
			op = Column(self, 'Outer Port', None, 2, cups['outer'], 6)

			os.setAdjacent([s])
			s.setAdjacent([os,p])
			p.setAdjacent([s, op])
			op.setAdjacent([p])

			self.columns =[os, s, p, op]

		if type == 'C2':
			# fill in columns [13.24]
			os = Column(self, 'Outer Starboard', None, 3, ['outer'], 6)
			s = Column(self, 'Starboard', 7, 2, ['inner'], 6)
			cs = Column(self, 'Center Starboard', 9, 1, ['center'], 6)
			cp = Column(self, 'Center Port', 9, 1, ['center'], 6)
			p = Column(self, 'Port', 7, 2, ['inner'], 6)
			op = Column(self, 'Outer Port', None, 3, ['outer'], 6)

			os.setAdjacent([s])
			s.setAdjacent([os,cs])
			cs.setAdjacent([s,cp])
			cp.setAdjacent([cs, p])
			p.setAdjacent([cp,op])
			op.setAdjacent([p])

			self.columns = [os, s, cs, cp, p, op]

		if type == 'TF':
			print('Task Force not yet implemented')

	def printColumns(self):	
		for c in self.columns:
			c.printColumn()



	def placeSub(self, sub):
		sub.performTacRoll()


		# sorted columns by tac entry roll
		cols = sorted(self.columns, key=lambda x:(x.entry or 0), reverse=True)

		# try and place the sub as close to the center as possible
		for c in cols:
			if c.tryAndPlaceSub(sub):
				break;


	def getTotalASWValue(self):
		a = 0
		for c in self.columns:
			a += c.getASWValue()

		return math.ceil(a)


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
		self.subPromoted = 0

	def printSummary(self):
		print('Sub',self.sub, 'sunk', self.sunk, 'ships for', self.tons, 'tons. Status:', self.subDamaged, 'damaged', self.subSpotted, 'spotted', self.subSunk, 'sunk', self.subRTB, 'RTB', 'promoted', self.subPromoted)

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


	def normalize(self):
		if self.subSunk > 0:
			self.subSunk = 1
			self.subDamaged = 0
			self.subSpotted = 0
			self.subRTB = 0
		if self.subDamaged > 0:
			self.subDamaged = 1
		if self.subRTB > 0:
			self.subRTB = 1
		if self.subSpotted > 0:
			self.subSpotted = 1
		if self.subPromoted > 0:
			self.subPromoted = 1




	def combine(self, results):

		for r in results:
			if r == None:
				continue

			self.sunk += r.sunk
			self.tons += r.tons 
			self.damaged += r.damaged
			self.subDamaged += r.subDamaged
			self.subSunk += r.subSunk
			self.subSpotted += r.subSpotted
			self.subRTB += r.subRTB
			self.subPromoted += r.subPromoted



class Sub:
	def __init__(self, name, attack, defense, tactical, skipper):
		self.name = name
		self.attackRating = attack
		self.defenseRating = defense
		self.tacRating = tactical
		self.skipper = skipper
		self.crashDiveRating = 1
		self.inexperienced = False
		self.spotted = False
		self.damage = 0
		self.rtb = False

		self.tonsSunk = 0
		self.targetsSunk = 0

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
			if globals.verbose_combat:
				print('Sub', self.name, 'fails to crash dive, becomes spotted')
			return False
		else:
			if globals.verbose_combat:
				print('Sub', self.name, 'crash dives!')
			return True

	def takeDamage(self, rtb=False):
		self.damage += 1

		rtbText = ''
		if rtb:
			self.rtb = True
			rtbText = ' returns to base'

		if globals.verbose_combat:
			print('Sub ' + str(self.name) + ' takes damage' + rtbText)

		if self.damage > 1:
			roll = random.randint(0, 9)
			if roll > self.defenseRating:
				self.sink()

	def isDamaged(self):
		return self.damage > 0

	def isSunk(self):
		return self.damage == -1

	def sink(self):
		self.damage = -1
		if globals.verbose_combat:
			print('Sub ' + str(self.name) + 'sinks')

	def eligibleForPromotion(self):
		return self.tonsSunk >= 23 and self.targetsSunk >= 3

	def claimTarget(self, target):
		if globals.verbose_combat:
			print('Sub ' + self.name + ' is claiming target ' + str(target))
		self.tonsSunk += target.tons
		self.targetsSunk += 1

	def canReAttack(self):
		return self.damage == 0 and self.rtb == False


	def promoteSkipper(self):
		self.skipper = min(self.skipper + 1, 2)
		if globals.verbose_combat:
			print('Sub ' + str(self.name) + ' promotes her skipper to level ' + str(self.skipper))

	def improvePosition(self):
		currentEntryReq = 0
		if self.column.entry:
			currentEntryReq = self.column.entry

		for a in self.column.adjacent:
			if a.entry and a.entry > currentEntryReq and a.hasFreeSubSlot():

				oc = self.column

				# remove from current column and add to new one
				self.column.sub_positions.remove(self)
				a.sub_positions.append(self)

				if globals.verbose_combat:
					print('Sub ' + str(self) + ' moves from column ' + str(oc) + ' to ' + str(a))

				return


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

def getES(nation, diligent, wp):
	# escorts: DD, DE, PF, CT, SL, TB, PG, CG

	pool = []
	if diligent:
		pool.append(('SL', 1, 6, 6))
		
		if wp >= 4:
			pool.append(('SL', 1, 6, 5))
			pool.append(('CT', 1, 6, 4))
		if wp == 5:
			pool.append(('CT', 1, 6, 3))
			pool.append(('CT', 1, 6, 3))

	else:

		pool.append(('ES', 1, 6, 2))
		pool.append(('SL', 1, 5, 0.5))
		pool.append(('FP', 1, 8, 2))
		pool.append(('ML', 3, 4, 0))

		if wp >= 2:
			pool.append(('CT', 1, 6, 1))
			pool.append(('CT', 1, 6, 1))
			pool.append(('CT', 1, 6, 1))
			pool.append(('CT', 1, 6, 1))
			pool.append(('CT', 1, 6, 2))
			pool.append(('CT', 1, 6, 2))

		if wp >= 3:
			pool.append(('DE', 1, 6, 2))
			pool.append(('CT', 1, 6, 1))
			pool.append(('CT', 1, 6, 1))
			pool.append(('CT', 1, 6, 1))
			pool.append(('CT', 1, 6, 1))
			pool.append(('CT', 1, 6, 2))
			pool.append(('CT', 1, 6, 2))
			pool.append(('CT', 1, 6, 2))
			pool.append(('CT', 1, 6, 2))
			pool.append(('CT', 1, 6, 2))
		if wp >= 4:
			pool.append(('SL', 2, 6, 2))

		if wp == 5:
			pool.append(('DE', 1, 7, 3))


	e = random.choice(pool)

	es = Encounter(e[0], nation, e[1], e[2], e[3])
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

def getESs(count, nation, diligent, wp):
	es = []
	for i in range(0, count):
		es.append(getES(nation, diligent, wp))
	return es

def seedCup(config, wp):
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
		cl = getWarship('CL', 'D 6t', 6, 4, 1)
		cl.fast = True
		cup.append(cl)

	if config[18]:
		cup.append(getAM('british'))
	cup += getDDs(config[19], 'british/aus/greek/nor', 1, False)
	cup += getDDs(config[20], 'british/aus/netherland/vichy/poland', 2, False)
	cup += getESs(config[21], 'british/nor/vichy/poland', False, wp)
	cup += getDDs(config[22], 'british', 2, True)
	cup += getESs(config[23], 'british', True, wp)
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

def seedTDCCup(warperiod):
	
	dist = []
	if warperiod == 1:
		dist = [1,3,7,8,8,7,4,1,1]
	if warperiod == 2:
		dist = [1,3,7,8,9,8,2,1,1]
	if warperiod == 3:
		dist = [1,2,7,6,9,8,6,2,1]
	if warperiod == 4:
		dist = [1,3,7,8,10,8,4,2,1]
	if warperiod == 5:
		dist = [1,2,7,8,9,8,7,3,1]

	def repeat(value, count):
		return [value]*count

	cups['tdc'] = []

	mod = -4
	for i in dist:
		cups['tdc'] += repeat(mod, i)
		mod += 1

	#print('Reshuffled TDC cup for WP' + str(warperiod) + ': ', cups['tdc'])


	random.shuffle(cups['tdc'])

def drawTDCCounter():
	return random.choice(cups['tdc'])

def seedCups(wp):
	cups['loner'] = []
	cups['outer'] = []
	cups['inner'] = []
	cups['center'] = []
	cups['west inner'] = []
	cups['west outer'] = []


	# WP1 seed
	
	if wp == 1:
		cups['loner'] = seedCup((1,1,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,5,14,1,2,2,3,0,0,0,3,0,2,0,0,1,1,0,0,0,1,0,1,1), 1)
		cups['outer'] = seedCup((1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,1,1,0,1,0,0,0,0,1,1,0,0,0,0,3,12,0,2,2,5,0,0,0,2,0,1,0,0,0,1,0,0,0,0,0,0,0), 1)
		cups['inner'] = seedCup((1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,1,0,0,1,0,0,0,0,0,1,0,0,0,0,0,7,8,0,1,1,3,0,1,0,1,1,1,0,0,0,2,0,0,0,0,0,0,0,0), 1)
		cups['center'] = seedCup((1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,13,5,1,0,4,2,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0), 1)

	if wp == 2:
		cups['loner'] = seedCup((1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,6,9,0,1,3,6,0,1,0,2,0,2,0,0,0,3,0,0,0,1,0,1,1), 2)
		cups['outer'] = seedCup((1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,1,1,0,0,0,0,0,0,0,0,0,0,0,4,12,0,1,1,4,0,0,0,3,0,1,0,0,0,1,0,0,0,0,0,0,0), 2)
		cups['inner'] = seedCup((1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,9,9,1,0,3,2,0,0,0,1,0,1,0,1,0,1,0,0,0,0,0,0,0), 2)
		cups['center'] = seedCup((1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,16,5,0,0,3,1,1,0,1,0,1,0,0,0,1,0,0,0,0,0,0,0,0), 2)


	if wp == 3:
		cups['loner'] =seedCup((1,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,4,12,0,1,2,2,0,0,0,1,0,1,0,1,0,2,0,1,0,1,0,1,1),3)
		cups['outer'] = seedCup((1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,1,3,1,1,0,0,0,0,0,0,0,0,0,0,2,12,0,0,1,4,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,),3)
		cups['inner'] = seedCup((1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,2,1,0,0,0,0,0,0,0,0,0,0,0,8,8,0,1,3,2,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0),3)
		cups['center'] = seedCup((1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,14,2,1,0,2,0,1,0,1,0,1,0,1,0,1,0,0,0,1,0,0,0,0),3)
		cups['west inner'] = seedCup((1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,0,0,2,0,0,0,0,0,0,8,7,0,1,3,3,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0),3)
		cups['west outer'] = seedCup((1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,2,0,0,1,0,0,3,0,0,0,0,0,0,3,10,0,0,0,4,0,1,0,0,0,1,0,1,0,1,0,0,0,0,0,0,0),3)

	if wp >= 4:
		print('WP4+ not yet implemented!')

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
	subsPromoted = 0

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
		subsPromoted += r.subPromoted

	shipsSunk.sort()
	shipsTonnage.sort()

	minSunk = 100
	maxSunk = 0
	meanSunk = 0.0
	totalSunk = 0
	for s in shipsSunk:
		totalSunk += s
		minSunk = min(minSunk, s)
		maxSunk = max(maxSunk, s)

	devSunk = pstdev(shipsSunk)
	meanSunk = totalSunk / len(shipsSunk)

	minTons = 100
	maxTons = 0
	meanTons = 0.0
	totalTons = 0.0
	for t in shipsTonnage:
		totalTons += t
		minTons = min(minTons, t)
		maxTons = max(maxTons, t)

	devTons = pstdev(shipsTonnage)
	meanTons = totalTons / len(shipsTonnage)



	print('Subs spotted:', subsSpotted, '/', len(results))
	print('Subs damaged:', subsDamaged, '/', len(results))
	print('Subs sunk:', subsSunk, '/', len(results))
	print('Subs RTB:', subsRTB, '/', len(results))
	print('Subs promoted:', subsPromoted, '/', len(results))

	print('Ships sunk:', totalSunk, '[', minSunk, '-', maxSunk, '], mean', meanSunk, '/', devSunk)
	print('Ships tonnage:', totalTons, '[', minTons, '-', maxTons, '] mean', meanTons, '/', devTons)


def writeResults(filename, results):

	f = open(filename, 'w')
	f.write('# name, tgt sunk, tgt tons, subsDmgd, subsSunk, subsSpotted, subsRTB, subsPromoted\n')
	for r in results:
		f.write(str(r.sub) + ',' + str(r.sunk) + ',' + str(r.tons) + ',' + str(r.subDamaged) + ',' + str(r.subSunk) + ',' + str(r.subSpotted) + ',' + str(r.subRTB) + ',' + str(r.subRTB) + '\n')

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


def revealCounters(convoy, sub):
	sub.column.revealCounters(sub.tacRating)

	# get revealed targets in the current and adjacent columns
	revealed = sub.column.getVisibleTargets()
	for a in sub.column.adjacent:
		revealed += a.getVisibleTargets()

	tdcCount = min(len(revealed), sub.tacRating)

	if globals.verbose_combat:
		print('Sub', sub.name, 'has', len(revealed), 'potential targets, placing', tdcCount, 'TDC markers, tactical rating:', sub.tacRating)
	return revealed

def placeTDC(revealed, sub, combatRound):

	# sorts targets by tonnage and if they are damaged
	def getTargetPriority(tgt):
		p = tgt.tons;
		if tgt.damaged:
			p += int(tgt.tons/2)
		return p


	tdcCount = min(len(revealed), sub.tacRating)

	revealed.sort(key=getTargetPriority, reverse=True)
	revealed = revealed[0:tdcCount]

	# set TDC markers [14.14]
	for r in revealed:
		r.tdc = drawTDCCounter()
		if globals.verbose_combat:
			print('Target/TDC:', r, r.tdc)

		# subtract 1 in the reattack round
	if combatRound > 1:
		if globals.verbose_combat:
			print('Reattack round -- improving target solutions')
		for r in revealed:
			r.tdc = max(-4, r.tdc-1)
			if globals.verbose_combat:
				print('Target/TDC:', r, r.tdc)

	# re-evaluate target priority with the tdcs
	def getUpdatedTargetPriority(tgt):

		p = tgt.tons
		if tgt.damaged:
			p += int(tgt.tons)

		try:
			# negative TDC values are good
			p += tgt.tdc * -1
		except KeyError:
			return -100

		return p

	if globals.verbose_combat:
		print(revealed)

	revealed.sort(key=getUpdatedTargetPriority, reverse=True)
	if globals.verbose_combat:
		print('Updated target priority:', revealed)

	return revealed


def selectTargets(revealed, sub):
	targets = []

	# split combat value in 4's and assign targets [14.15]
	cv = sub.attackRating
	tdcIndex = 0

	while cv > 0 and len(revealed) > 0 and tdcIndex < len(revealed):
		# place a TDC on a counter
		
		r = revealed[tdcIndex]
		r.tdc = drawTDCCounter()
		targets.append(r)

		tdcIndex += 1
		cv -= 4 

	return targets


def attackSingleTarget(target, sub, aswValue):
	result = CombatResult(sub)

	# 14.16 attack
	attackValue = sub.attackRating + sub.skipper + globals.torp_value

	damageMod = 0
	if target.damaged:
		damageMod = -1

	if globals.verbose_combat:
		print('Combat vs', target)
		print('Attack :', attackValue, '[', sub.attackRating, 'attack',sub.skipper,'skipper',globals.torp_value,' torp rating')
		print('Defense:', aswValue, '[', aswValue, 'ASW', target.tdc,'TDC', damageMod, ' damaged]')
	aswValue = aswValue + target.tdc + damageMod

	diff = attackValue - aswValue
	roll = random.randint(0, 9)
	if sub.inexperienced:
		roll += 1

	if roll <= diff:
		if globals.verbose_combat:
			print('Diff:',diff,'Roll:', roll, 'Target hit')

		# consult attack results table here
		d = target.rollForDamage(sub)

		if d == 'sunk':
			result.sunk += 1
			result.tons += target.tons

			sub.claimTarget(target)

		if d == 'damage':
			result.damaged += 1

	else:
		if globals.verbose_combat:
			print('Diff:',diff,'Roll:', roll, 'Target missed')

	target.tdc = None
	return result




def attackTargets(convoy, targets, sub):
	result = CombatResult(sub)

	# 14.15 targeted escorts

	# 14.16 attack
	attackValue = sub.attackRating + sub.skipper + globals.torp_value + convoy.straggle_level

	for t in targets:
		aswValue = sub.column.getASWValue()
		for a in sub.column.adjacent:
			aswValue += a.getASWValue()

		columnMod = 0
		if sub.column != t.column:
			columnMod = 1
		damageMod = 0
		if t.damaged:
			damageMod = -1

		if globals.verbose_combat:
			print('Combat vs', t)
			print('Attack :', attackValue, '[', sub.attackRating, 'attack',sub.skipper,'skipper',globals.torp_value,' torp rating', convoy.straggle_level, 'convoy straggle]')
			print('Defense:', aswValue, '[', aswValue, 'ASW', t.tdc,'TDC', columnMod, 'column mod',damageMod, ' damaged]')
		aswValue = aswValue + t.tdc + columnMod + damageMod

		diff = attackValue - aswValue
		roll = random.randint(0, 9)
		if sub.inexperienced:
			roll += 1

		if roll <= diff:
			if globals.verbose_combat:
				print('Diff:',diff,'Roll:', roll, 'Target hit')

			# consult attack results table here
			d = t.rollForDamage(sub)

			if d == 'sunk':
				result.sunk += 1
				result.tons += t.tons

				sub.claimTarget(t)

			if d == 'damage':
				result.damaged += 1

		else:
			if globals.verbose_combat:
				print('Diff:',diff,'Roll:', roll, 'Target missed')

	# remove tdc markers again
	for r in targets:
		r.tdc = None


	return result




def attackRound(convoy, sub, combatRound):

	# reveal counters [14.12]
	revealed = sub.revealCounters()

	for r in revealed:
		if r and r.type == 'AC':
			if globals.verbose_combat:
				print('Found aircraft!')

			if air_cover == 'light' and random.randint(0,9) > 4:
				# replace with new draw
				if globals.verbose_combat:
					print('Light air cover, replacing AC with new draw')
				
				for t in r.column.targets:
					if globals.verbose_combat:
						print(t)

				try:
					idx = r.column.targets.index(r)
					
					if idx:
						new_encounter = random.choice(r.column.draw_cup)
						r.column.targets[idx] = new_encounter
						new_encounter.visible = True

						revealed.append(r.column.targets[idx])
						if globals.verbose_combat:
							print('Redrew encounter at position ' + str(idx) + ': ' + str(new_encounter))

				except ValueError:
					print('FIXME! AC column index could not be found')

		if r and r.type == 'Event':
			# ignore events?
			if globals.verbose_combat:
				print('Found event, ignoring it')

		if r and r.diligent:
			if globals.verbose_combat:
				print('Found diligent escort')
			if not sub.crashDive():
				# roll for damage from diligent escort
				diligentEscortTable(sub)


	# set tdcs [14.14]
	seedTDCCup()
	combatResult = sub.attack(convoy, combatRound)
	combatResult = convoy.counterattack(sub, combatRound > 1, combatResult)

	return combatResult



def convoyCounterAttack(convoy, sub, combatRound):
	# 14.2
	# totalASW = self.getTotalASWValue()

	# get asw value in current and adjacent columns
	immediateColumns = [sub.column] + sub.column.adjacent
	asw = sum(c.getASWValue() for c in immediateColumns)

	# find remote available asw values from aircraft or cvs
	for c in convoy.columns:
		if c not in immediateColumns:
			for t in c.targets:
				if t and t.visible and (t.type == 'AC' or t.type == 'CV'):
					asw += t.asw

	return counterAttack(asw, sub, combatRound)


def counterAttack(totalASW, sub, combatRound):

	asw = totalASW

	asw += globals.red_dots
	asw += globals.asw_value


	defense = sub.defenseRating + sub.skipper
	if sub.inexperienced:
		defense -= 1

	diff = asw - defense
	if globals.verbose_combat:
		print('Counterattack, red boxes:', globals.red_dots, 'global asw:', globals.asw_value)
	if globals.verbose_combat:
		print('Total ASW', asw, 'defense', defense, 'diff', diff)

	result = CombatResult(sub) 

	if diff < 0:
		if globals.verbose_combat:
			print('No counterattack, diff:', diff)
	else:
		# counterattack
		roll = random.randint(0,9)
		roll += sub.isDamaged()
		if combatRound > 1:
			roll += 1
		if sub.spotted:
			roll += 1


		if roll > 12:
			roll = 12

		if asw > 8:
			asw = 8
		asw = int(asw)

		if globals.verbose_combat:
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
			if globals.verbose_combat:
				print('No effect.')
		else:

			if roll in row[0]:
				sub.spotted = True
				if globals.verbose_combat:
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




def withdrawSubs(subs, combatRound):

	if globals.verbose_combat:
		print('!!!!Withdrawing subs')
		print('Before:', subs)

	# [14.3] Voluntary withdrawal
	# in our case all RTB, damaged and spotted subs and also all subs 
	subs = [s for s in subs if not (s.rtb or s.isDamaged() or s.spotted)]

	if combatRound > 1 and len(subs) > 0:
		# then remove all subs without elite skipper		
		subs = [s for s in subs if s.skipper > 0]

	if globals.verbose_combat:
		print('After:', subs)

	return subs


def increaseStraggle(convoy, targetsDamagesOrSunk, combatRound):
	
	roll = random.randint(0, 9)
	if roll < targetsDamagesOrSunk or roll == 0:
		if globals.verbose_combat:
			print('Convoy straggle level increases')
		convoy.straggle_level += 1

	if roll == 9:
		if globals.verbose_combat:
			print('Convoy straggle level decreases')
		convoy.straggle_level = max(convoy.straggle_level-1, 0)


def createSubs(subcount, convoy, id):
	subs = []
	for s in range(0, subcount):

		name = 'U-' + str(id)
		if subcount > 1:
			name += '.' + str(s)

		sub = Sub(name, 5, 3, 3, 0)
		convoy.placeSub(sub)
		subs.append(sub)

	return subs



def attackLonersHarness():
	subs = [(2,1,2), (3,3,2), (4,2,3), (5,3,3)]
	warperiod = 1

	for skipper in range(0, 3):
		for sub in subs:
			attackLoners(warperiod, skipper, sub)


def attackLoners(warperiod=3, skipper=0, sub_vals = (3,3,2)):
	results = []

	globals.torp_value = 0

	sub_atk = sub_vals[0]
	sub_def = sub_vals[1]
	sub_tac = sub_vals[2]


	seedTDCCup(warperiod)

	for i in range(0, globals.attackIterations):
		# refresh the cups periodically
		if i % 50 == 0:
			seedCups(warperiod)
			globals.setWP(warperiod)


		sub = Sub('U-'+str(i), sub_atk, sub_def, sub_tac, skipper)

		# create convoy and subs
		targets = []
		for i in range(0,4):
			targets.append(random.choice(cups['loner']))

		# reveal all and remove stuff
		totalASW = 0
		for t in targets:
			t.visible = True

			try:
				totalASW += t.asw
			except TypeError:
				pass

		targets = [t for t in targets if t.isValidTarget()]

		# [28.23] and [28.24]
		attackResults = []
		for t in targets:

			if t.type == 'AC':
				pass
			else:
				t.tdc = random.choice(cups['tdc'])
				result = attackSingleTarget(t, sub, totalASW)
				attackResults.append(result)


				if result.sunk > 0:
					targets.remove(t)


		# one single counter attack
		defense = counterAttack(totalASW, sub, 1)
		defense.combine(attackResults)

		if sub.canReAttack():
			# second combat round
			if globals.verbose_combat:
				print('Loner reattack round')

			# remove fast units
			for t in targets:
				if t.fast and t.damaged == False:
					targets.remove(t)

				attackResults = []

				for t in targets:
					if t.type == 'AC':
						pass
					else:
						t.tdc = random.choice(cups['tdc'])
						result = attackSingleTarget(t, sub, totalASW)
						attackResults.append(result)


						if result.sunk > 0:
							targets.remove(t)


			# one single counter attack
			defense2 = counterAttack(totalASW, sub, 1)
			defense2.combine(attackResults)

			defense.combine([defense2])


		defense.printSummary()
		results.append(defense)


		if sub.eligibleForPromotion():
			if globals.verbose_combat:
				print('Sub eligible for promotion (' + str(sub.targetsSunk) +' tgts, ' + str(sub.tonsSunk) + ' tons)' )
			result.subPromoted = 1
			sub.promoteSkipper()


	summarizeResults(results)

	filename = 'loners-' + str(sub.attackRating) + str(sub.defenseRating) + str(sub.tacRating) +  '+' + str(sub.skipper)
	filename += '-wp' + str(warperiod) + '.csv'

	writeResults(filename, results)

def attackConvoyHarness():
	subs = [(2,1,2), (3,3,2), (4,2,3), (5,3,3)]
	warperiod = 1

	for skipper in range(0, 3):
		for sub in subs:
			attackConvoy(warperiod, 'C1', skipper, sub)
			attackConvoy(warperiod, 'C2', skipper, sub)


def attackConvoy(warperiod=3, convoyType='C1', skipper=0, sub_vals=(3,3,2)):

	results = []

	for i in range(0, globals.attackIterations):

		# refresh the cups periodically
		if i % 50 == 0:
			seedCups(warperiod)
			globals.setWP(warperiod)

		# create convoy and subs
		convoy = Convoy(convoyType)
		convoy.straggle_level = globals.base_straggle_level

		# create the single(!) sub
		sub = Sub('U-'+str(i), sub_vals[0], sub_vals[1], sub_vals[2], skipper)
		convoy.placeSub(sub)

		# first round of attack
		targets = revealCounters(convoy, sub)

		seedTDCCup(warperiod)
		targets = placeTDC(targets, sub, 1)
		targets = selectTargets(targets, sub)
		result = attackTargets(convoy, targets, sub)

		defense = convoyCounterAttack(convoy, sub, 1)
		result.combine([defense])


		# determine if we go into a reattack round
		if not (sub.damage > 0 or sub.rtb):
			# [14.4] Re-attack rounds

			# [29.3] Check for straggle increase
			increaseStraggle(convoy, result.sunk+result.damaged, 1)

			# try to move up one column

			# TODO - Implement me
			sub.improvePosition()


			# second round of attack
			targets = revealCounters(convoy, sub)

			seedTDCCup(warperiod)
			targets = placeTDC(targets, sub, 2)
			targets = selectTargets(targets, sub)
			result2 = attackTargets(convoy, targets, sub)

			defense = convoyCounterAttack(convoy, sub, 2)
			result.combine([result2, defense])


			# possible 3rd round of combat
			if not (sub.damage > 0 or sub.rtb) and sub.skipper > 0:

				increaseStraggle(convoy, result2.sunk+result2.damaged>0, 2)

				targets = revealCounters(convoy, sub)
				seedTDCCup(warperiod)

				targets = placeTDC(targets, sub, 2)
				targets = selectTargets(targets, sub)
				result3 = attackTargets(convoy, targets, sub)

				defense = convoyCounterAttack(convoy, sub, 2)
				result.combine([result3, defense])

		if sub.eligibleForPromotion():
			if globals.verbose_combat:
				print('Sub eligible for promotion (' + str(sub.targetsSunk) +' tgts, ' + str(sub.tonsSunk) + ' tons)' )
			result.subPromoted = 1
			sub.promoteSkipper()

		result.normalize()
		results.append(result)

	#for r in results:
	#	r.printSummary() 

	summarizeResults(results)

	filename = convoyType.lower() + '-' + str(sub.attackRating) + str(sub.defenseRating) + str(sub.tacRating) +  '+' + str(sub.skipper)
	filename += '-wp' + str(warperiod) + '.csv'

	writeResults(filename, results)



	#r2 = [r for r in results if r.subPromoted > 0]
	#if len(r2) > 0:
	#	print('Skipper promotions:')
	#	for r in r2:
	#		r.printSummary()
	#else:
	#	print('No skippers promoted.')

if __name__ == '__main__':
	random.seed()
	#attackConvoy()
	

	attackLonersHarness()
	attackConvoyHarness()
	#attackLoners()
