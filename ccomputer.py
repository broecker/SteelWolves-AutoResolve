import random

cups = {}
torp = -1
bdienst = 0

tdcCup = []


class Encounter:
	def __init__(self, type, nation, tons, defense):
		self.type = type
		self.nation = nation
		self.tons = tons
		self.defense = defense

class Column:
	def __init__(self, name, entry, max_subs):
		self.name = name
		self.targets = []
		self.entry = entry
		self.sub_positions = []
		self.max_subs = max_subs

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
			t.visible = False

	def tryAndPlaceSub(self, sub):
		if (self.entry == None or sub.tac_roll > self.entry) and len(self.sub_positions) < self.max_subs:
			self.sub_positions.append(sub)
			sub.column = self

			print('Placed sub in column', self.name,' [ roll:', sub.tac_roll, '>', self.entry,']')

			return True;
		else:
			return False;

class Sub:
	def __init__(self, tac, skipper):
		self.tac = tac
		self.skipper = skipper

	def performTacRoll(self):
		self.tac_roll = random.randint(0,9) + self.tac + self.skipper


def getEvent(type) : 
	return Encounter(type, None, None, None);

def getAircraft(nation, strength):
	return Encounter('AC', nation, None, strength);

def getWarship(type, name, tons, defense):
	ws = Encounter(type, 'british', tons, defense)
	ws.name = name
	return ws

def getDD(nation, tons, diligent):
	dd = Encounter('DD', nation, tons, 3)
	dd.diligent = diligent
	return dd

def getES(nation, diligent):
	es = Encounter('ES', nation, 2, 2)
	es.diligent = diligent
	return es

def getAM(nation):
	return Encounter('AM', nation, 2, 2)
	
def getMerchant(nation, hvy):
	m = Encounter('M', nation, 0, 0);

	MAX_MERCHANT_TONNAGE = 10;
	if hvy == True:
		m.tons = random.randint(6, MAX_MERCHANT_TONNAGE)
	else:
		m.tons = random.randint(2, 5)
	return m;

def getSV(nation, tons):
	return Encounter('SV', nation, tons, 0)

def getFV():
	return Encounter('FV', 'british', 1, 0);

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
	if config[12]:
		cup.append(getWarship('CV', 'Courageous', 20, 6))
	if config[13]:
		cup.append(getWarship('CVE', 'Avenger', 15, 4))
	if config[14]:
		cup.append(getWarship('CV', 'Audacity', 20, 6))
	if config[15]:
		cup.append(getWarship('CA', 'Malaya', 10, 8))
	if config[16]:
		cup.append(getWarship('CA', 'Ramilles', 10, 8))
	if config[17]:
		cup.append(getWarship('CL', 'D 6t', 6, 4))

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
		cup.append(Encounter('TB', 'french', 1, 1))

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
		cup.append(Encounter('CM', 'british', 7, 4))


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
	tdcCup = []

	for i in range(0,5):
		tdcCup.append(-2)
		tdcCup.append(2)
	for i in range(0,10):
		tdcCup.append(-1)
		tdcCup.append(1)
		tdcCup.append(0)

	random.shuffle(tdcCup)


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
	

def hideColumn(col):
	for c in col:
		c.visible = False;

def revealCounters(sub):
	''' flips num counters to be visible in the given column'''

	print('sub is reveling', sub['tac'], 'counters in position', sub['position']['name'])

	# count how many are unrevealed first
	unrevealed = sum(c['visible'] == True for c in sub['column'])
	print(unrevealed)



def placeSub(positions, sub):

	for p in positions:

		if p['entry'] == None or sub['tac_roll'] > p['entry']:

			# see if we have empty positions
			try:
				a = p['subs'].index(None)
				p['subs'][a] = sub				
				print('Sub entered position', p['name'], '[ die roll: ', sub['tac_roll'], '>', p['entry'], ']')

				sub['column'] = p['column']
				sub['position']  = p

				return
			except ValueError:
				# silently ignore errors and try the next position
				pass


	return False


def attackC2(subs):
	print('Attacking large convoy (C2)')

	# fill in columns [13.24]
	os = Column('Outer Starboard', None, 3)
	s = Column('Starboard', 7, 2)
	cs = Column('Center Starboard', 9, 1)
	cp = Column('Center Port', 9, 1)
	p = Column('Port', 7, 2)
	op = Column('Outer Port', None, 3)

	allColumns = [cs, cp, p, s, os, op]


	os.seed(cups['outer'], 5)
	s.seed(cups['inner'], 5)
	cs.seed(cups['center'], 5)
	cp.seed(cups['center'], 5)
	p.seed(cups['inner'], 5)
	op.seed(cups['outer'], 5) 


	# roll for each sub [14.11]
	for s in subs:
		s.performTacRoll()

		# try and place the sub as close to the center as possible
		for c in allColumns:
			if c.tryAndPlaceSub(s):
				break;



if __name__ == '__main__':
	seedCups(1)
	seedTDCCup()

	# search and contact phase here
	sub1 = Sub(4, 0)
	sub2 = Sub(4, 1)
	sub3 = Sub(4, -1)
	attackC2([sub1, sub2, sub3])