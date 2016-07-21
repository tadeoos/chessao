from szachao import *
import random
import time
import re
import os

def rozd(tal):
	a=[]
	b=[]
	for i in range(5):
		a.append(tal.cards.pop())
		b.append(tal.cards.pop())
	return (a,b,tal)

def karta_z_str(s):
	return karta(int(s[-1]), s[:-1])

def decode_card_color(s):
	if s == '♤':
		return 1 
	elif s == '♡':
		return 2
	elif s == '♢':
		return 3
	elif s == '♧':
		return 4
	else:
		raise ValueError

def decode_card(s):
	b = 1 if s[0]=='!' else 0

	if ';' in s:
		col = decode_card_color(s[-3])
		rank = s[:-3] if b == 0 else s[1:-3]
		w = s[-1]
		return (b, [karta(col, rank)], nawaleta(w))
	else:
		col = decode_card_color(s[-1])
		rank = s[:-1] if b == 0 else s[1:-1]
		return (b, [karta(col, rank)])

def nawaleta(s):
	c = s.lower()
	if c == 'p':
		return 'pionek'
	elif c == 'w':
		return 'wieza'
	elif c == 's':
		return 'skoczek'
	elif c == 'g':
		return 'goniec'
	elif c == 'd':
		return 'dama'
	else:
		return False

def schodki_check(lis):
	# schodkom brakuje jeszcze opcji schodzenia w dół...
	for i in range(len(lis)-1):
		if lis[i].ran==lis[i+1].ran:
			continue
		if int(lis[i].ran)+1==int(lis[i+1].ran) and lis[i].kol==lis[i+1].kol:
			continue
		return False
	return True

def ok_karta(karta, talie):
	if len(karta)>1:
		if not schodki_check(karta):
			return False
	for t in talie:
		if karta[0].kol == t[-1].kol or karta[0].ran == t[-1].ran or t[-1].ran=='Q' or karta[0].ran=='Q':
			return True
	return False

def odejmij(a,b):
	out = [x for x in a if x not in b]
	if len(out) == len(a) - len(b):
		return out
	elif len(b)==1:
		out.extend(b)
		return out
	else:
		assert len(out)==5
		return out


def ktora_kupka(karta, kupki, rnd=False):
	res = []
	for i in range(2):
		if karta[0].kol == kupki[i][-1].kol or karta[0].ran == kupki[i][-1].ran or kupki[i][-1].ran=='Q'or karta[0].ran=='Q':
			res.append(i)
	if len(res)==1:
		return res[0]
	elif len(res)==2:
		if rnd:
			return random.randint(0,1)
		a = input('Na którą kupkę dołożyć kartę? (0 - lewa / 1 - prawa) ')
		assert a in ('1', '0')
		return int(a)
	return 3

def rozpakuj_input(inp):
	a = inp.split()
	if len(a)==3:
		a[0] = [karta_z_str(s) for s in a[0].split(',')]
	elif len(a)==1:
		return [karta_z_str(s) for s in inp.split(',')]
	elif len(a)==2:
		return a
	return a 

def czy_pion_na_koncu(plansza, k):
	assert k in ('b', 'c')
	if k == 'b':
		for i in range(91,99):
			if type(plansza.brd[i])==pionek and plansza.brd[i].kolor=='b':
				return i
	else:
		for i in range(21,29):
			if type(plansza.brd[i])==pionek and plansza.brd[i].kolor=='c':
				return i
	return 0





#### PLAYER CLASS



class gracz:
	def __init__(self, ida, kol, reka=[], bot = True, name='gracz'):
		self.nr = ida
		self.kol = kol
		self.reka = reka
		self.name = name
		self.bot = bot

	def choose_card(self, talie, plansza):
		if self.bot:
			burn = random.randint(0,1)
			card = random.choice(self.reka)
			if not ok_karta([card], talie):
				burn = 1
			if not burn and card.ran=='J':
				ch = [s[0] for s in jaki_typ_zostal(plansza,odwrot(self.kol)) if s!='krol']
				# here is a problem with jack loosing its ability when there is only king left..
				if len(ch)==0:
					return (burn, [card])
				choice = random.choice(ch)
				return (burn, [card], nawaleta(choice))
			return (burn, [card])
		else:
			ask = input('Karta: ')
			return None
			# trza dokończyć..

	def choose_move(self, d):
		if self.bot:
			random_ruch = random.choice(list(d.keys()))
			random_nr = random.randint(0,len(d[random_ruch])-1)
			return [random_ruch, d[random_ruch][random_nr]]
		else:
			ask = input('Ruch: ')
			return None

	def choose_prom(self):
		if self.bot:
			return random.choice(['D','G','S','W'])
		else:
			return input('Na jaką figurę chcesz zamienić piona?\nD - Dama\nG - Goniec\nS - Skoczek\nW - Wieża\n').upper()
	def __str__(self):
		return 'Gracz {}'.format(self.nr)
	def __repr__(self):
		return 'Gracz {}'.format(self.nr)



######## SZACHAO CLASS

class rozgrywka:
	def __init__(self, rnd=1):
		self.plansza = board(rnd)
		self.karty = talia()
		self.karty.combine(talia().cards)
		self.karty.tasuj()
		tpr = rozd(self.karty)
		self.gracze = (gracz(1,'b',tpr[0]), gracz(2,'c',tpr[1]))
		self.karty = tpr[2]
		self.kupki = ([self.karty.cards.pop()], [self.karty.cards.pop()])
		self.szach = False
		self.mat = False
		self.pat = False
		self.spalone = []
		self.historia = [self.plansza.fen()]
		self.zamiana = False
		self.to_move = 'b'
		self.burned = False
		self.now_card = None
		self.jack = None
		self.four = False
		self.capture = True

		# self.blotki = (5,6,7,8,9,10)
		# self.indy = (2,'K')
		# self.roz = ('A', 3, 4, 'J', 'K', 'Q')

	def __str__(self):
		print('\r{}'.format(self.plansza))
		print('\r\nKupki:   |{0:>3} |  |{1:>3} |'.format(str(self.kupki[0][-1]), str(self.kupki[1][-1])))
		print('\rGracz 1: {}, kolor: {}'.format(self.gracze[0].reka, self.gracze[0].kol))
		print('Gracz 2: {}. kolor: {}'.format(self.gracze[1].reka, self.gracze[1].kol))
		print('\nTalia: \n{} ...\n'.format(self.karty.cards[-5:][::-1]))
		return ''

	def do_card_buisness(self, kar):
		player = self.get_gracz(self.to_move)
		if self.burned:
			player.reka = odejmij(player.reka, kar)
			self.spalone.extend(kar)
			if len(self.karty.cards)<len(kar):
				self.przetasuj()
			tas = self.karty.deal(len(kar))
			player.reka.extend(tas)
		else:
			if self.szach:
				assert kar[-1].ran!='A'
			player.reka = odejmij(player.reka, kar)
			self.kupki[ktora_kupka(kar, self.kupki, player.bot)].extend(kar)
			if len(self.karty.cards)<len(kar):
				self.przetasuj()
			tas = self.karty.deal(len(kar))
			player.reka.extend(tas)

	def graj(self, rnd = False, test=False):
		while not self.mat and not self.pat:
			# os.system('clear')
			self.get_card()
			m = self.get_move()
			self.move(self.now_card, m)
			# print('\r{}'.format(self))
			# os.system('clear')
			# time.sleep(3)
			# self.to_move = odwrot(self.to_move)
		return True

	def get_card(self):
		# clearing self.capture
		self.capture = True

		player = self.get_gracz(self.to_move)
		# tu trzeba dopisać, że jak jest król pik to zmykam od razu i cofnąć przy tej okazji plansze!

		w  = self.what_happened()
		if w[0]==2:
			self.cofnij(self.to_move, w[1])
			card = w[2]
			# tu jeszcze jest kłopot co z waletem
		else:
			# tu powinno być jakieś checkowanie kart...
			card = player.choose_card(self.kupki, self.plansza)
			while(not self.card_ok_to_play(card)):
				card = player.choose_card(self.kupki, self.plansza)
		self.burned = card[0]
		if w[0]!=2: self.do_card_buisness(card[1])
		self.now_card = card[1][0]
		if len(card)==3:
			self.jack = card[2]
			assert self.jack in jaki_typ_zostal(self.plansza, odwrot(self.to_move))
		else:
			self.jack = None
		if self.now_card.ran == '4' and not self.burned:
			self.capture = False


	def get_move(self):
		self.zamiana = False
		player = self.get_gracz(self.to_move)
		# after ace or king of spikes there is no move
		if not self.burned and (self.now_card.ran=='A' or (self.now_card.ran=='K' and self.now_card.kol==1)):
			return []

		w = self.what_happened()
		all_moves = all_ruchy(self.plansza, self.to_move, self.capture, self.now_card, self.burned, w)
		if len(all_moves)==0:
			return []
		move = player.choose_move(all_moves)
		return move

	def move(self, card, where):
		player = self.get_gracz(self.to_move)
		# passing a move 
		if where == []:
			# changing the color to move
			self.to_move = odwrot(self.to_move)
			#udapting check and mate although i think it shoudln't change
			self.szach = self.czy_szach(self.to_move)	
			if self.szach and self.czy_pat(self.to_move):
				self.szach = False
				self.mat = True
			elif self.czy_pat(self.to_move):
				self.pat = True


			#udpating history
			record = '{color} {car} '.format(color=odwrot(self.to_move), car=card)
			self.historia.append(record)

			#checking for Ace, and switching color
			if self.now_card.ran == 'A' and not self.burned:
				self.to_move = odwrot(self.to_move)
				for g in self.gracze:
					g.kol = odwrot(g.kol)

			return None

		# actual move happens
		if self.burned:
			self.plansza.rusz(where[0], where[1])
		else:
			self.plansza.rusz(where[0], where[1], card)

		#checking if pawn is getting promoted
		q = 'BŁĄD!!'
		zam = czy_pion_na_koncu(self.plansza, self.to_move)
		if zam>0:
			self.zamiana = True	
			q = player.choose_prom()
			if q == 'E':
				return 'exit'
			elif q=='D':
				self.plansza.brd[zam] = dama(self.to_move, zam)
			elif q=='G':
				self.plansza.brd[zam] = goniec(self.to_move, zam)
			elif q=='S':
				self.plansza.brd[zam] = skoczek(self.to_move, zam)
			elif q=='W':
				self.plansza.brd[zam] = wieza(self.to_move, zam)
			else:
				print('wrong input')

		# after my move I must not be checked
		assert not self.czy_szach(self.to_move)

		# changing the color to move
		self.to_move = odwrot(self.to_move)

		#udapting check and mate
		self.szach = self.czy_szach(self.to_move)

		if self.szach and self.czy_pat(self.to_move):
			self.szach = False
			self.mat = True
		elif self.czy_pat(self.to_move):
			self.pat = True
		#updating history
		record = '{color} {burn}{car}{jack}  {piece}{fro}:{to}{prom}{check}{mate}'.format(color=odwrot(self.to_move), burn = '!' if self.burned else '', car=card, jack = ';'+self.jack[0] if self.jack != None else '', piece = get_fen_rep(self.plansza.get_piece(where[1])), fro = where[0], to = where[1], prom = '='+q if self.zamiana else '', check = '+' if self.szach else '', mate = '#' if self.mat else '')
		self.historia.append(record)
		return True

	def czy_szach(self, k):
		s = self.plansza.czy_szach()
		if s == (True, k):
			return True
		elif s == 2:
			return 2
		return False

	def czy_pat(self, k):
		if len(self.plansza.all_taken())==2:
			return True
		szach = self.czy_szach(k)
		for kar in self.get_gracz(k).reka:
			if ok_karta([kar], self.kupki):
				if szach and kar.ran=='Q':
					continue
				res = all_ruchy(self.plansza, k, True, kar)
				if len(res)>0:
					return False
			else:
				res = all_ruchy(self.plansza, k)
				if len(res)>0:
					return False
		return True

	def get_gracz(self, k):
		return [g for g in self.gracze if g.kol == k][0]

	def cofnij(self, kolor, ruch):
		assert len(self.historia)>1
		# assert self.historia[-1][-1]==karta(1,'K')
		# tu problem w przypadku omijania kolejki
		# ruch = self.historia[-2][-2:]
		# assert 
		a = self.plansza.mapdict[ruch[0]]
		b = self.plansza.mapdict[ruch[1]]

		# tu niweluje enpassant jeśli było, ale problem jak cofnąć ruszoność, jeśli była pierwsza. 
		self.plansza.enpass = 300

		if self.zamiana:
			self.plansza.brd[b] = pionek(kolor,b)
		if self.plansza.bicie:
			assert self.plansza.is_empty(a)
			rezurekt = self.plansza.zbite.pop()
			self.plansza.brd[a] = rezurekt
			self.plansza.swap(a,b)
		else:
			self.plansza.swap(a,b)
		assert not self.plansza.is_empty(a) or not self.plansza.is_empty(b)

	def przetasuj(self):
		kup_1=self.kupki[0][-1]
		kup_2=self.kupki[1][-1]
		do_tasu = self.kupki[0][:-1] + self.kupki[1][:-1] + self.spalone
		# assert len(do_tasu) > 3
		out = talia(do_tasu)
		# assert len(out.cards) < 100
		# assert len(out.cards) > 3
		self.spalone = []
		out.tasuj()
		out.combine(self.karty.cards)
		self.karty = out
		self.kupki=([kup_1], [kup_2])
		all_cards = len(self.karty.cards)+len(self.kupki[0])+len(self.kupki[1])+len(self.spalone)+len(self.gracze[0].reka)+len(self.gracze[1].reka)
		if all_cards!=104:
			print('\nALL CARDS: {}'.format(all_cards))
		assert all_cards==104

	def what_happened(self):
	# this function is parsing the history to make sense of the situation. returns ints that code a situation.
	# 1 = turn loosing, 2 - king of spades, 3 - king of hearts, 4 - jack
		s = self.historia[-1]
		s2 = self.historia[-2] if len(self.historia)>1 else ''
		ind = s2.index(':') if ':' in s2 else None
		what = s[2]
		# if the card was burned or there is a check, last card doesn't matter
		if what == '!' or self.szach:
			return (0,)
		elif what == '4' and self.now_card.ran != '4':
			return (1,)
		elif what == 'K' and s[3] == '♤' and ind != None:
			# r = re.search('\s(.+)\s',s2)
			c = self.from_history_get_card(-2)
			return (2, [s2[:ind][-2:],s2[ind+1:][:2]], c)
		elif what == 'K' and s[3] == '♡' and ind != None:
			if self.plansza.get_piece(s2[ind+1:][:2]).kolor!=self.to_move:
				return (1,)
			return (3, s2[ind+1:][:2])
		elif what == 'J' and self.now_card.ran != 'J':
			if self.jack not in jaki_typ_zostal(self.plansza, self.to_move):
				return (1,)
			return (4, self.jack)
		else:
			return (0,)

	def check_if_move(self, n):
	# check if n turnes ago there was a move made
	# if true this means three possible scenarios happened - kspades,ace or lost turn
		return ':' in self.historia[-n]

	def check_card(self, n, r, cl=None):
	# check if card played n turns ago has a rank==ran (and color = col)
	#if card was burned returns
		c = from_history_get_card(n)
		if c[0] == 1:
			return False
		return c[1].ran == r and c[1].kol == cl if cl != None else c[1].ran == r

	def from_history_get_card(self, n):
	# returns a card played n turns ago 
		if n > len(self.historia):
			return None
		s = self.historia[-n]
		r = re.search('\s(.+?)\s',s)
		c = r.group(1)
		return decode_card(c)

	def card_ok_to_play(self, crd):
		# conditions that if met block the card
		if crd[0] == 1:
			return True

		c = crd[1][0]
		cond1 = self.szach and (c.ran=='A' or c.ran=='Q')
		# war2 = (kar[-1].ran=='K' and kar[-1].kol==1) and (last_card.ran=='A' or licznik<3 or temp=='ominięta')
		# war3 = (kar[-1].ran=='K' and kar[-1].kol==2) and (licznik<2 or temp=='ominięta')
		# war4 = last_card.ran=='J' and kar[-1].ran=='4' and ok_karta(kar,self.kupki)
		# war5 = kar[-1].ran=='4' and self.szach and len(all_ruchy(self.plansza, kolej, False, kar[-1]))==0

		if cond1:
			return False

		return True
#### bugi

# ♤
# ♡

# co kiedy król zagrywa specjalnego króla i ma w zasięgu króla przeciwnego?
# - dokleiłem jeszcze w dozwolonym damki warunek na typ ktory zostal
# król się zbija w pewnym momencie (jakim?)
# - dokleilem w all_ruchy by wywalal pozycje krola
# kkier unhashable type karta
#  problem w tempie, zmienilem troche na glupa, zeby bral dobre miejsce jak widzie ze cos zle ale olewam to dla k pika.
# co kiedy zagrywam waleta, żądam ruchu damą, którą następnie zbijam?
# robię tak, że tracisz kolejkę.
# czy mogę dać czwórkę na waleta?
# robię, że nie
# może się wydarzyć taka sytuacja: czarne szachują białe. biały król ucieka. czarne zagrywają króla pik. (co w efekcie połowicznie realizuje króla pik - cofa rozgrywkę, ale zaraz karta już przestaje działać bo jest szach ) biały król zagrywa króla pik. -> system się jebie


# może być też tak, że król się gracz się sam wpierdoli w pata. Białe zagrywają 4, więc nie mogą zbijać, ale został im już tylko król, który ma jeden ruch -- zbić coś. Czy dopuszczamy taką opcję? Samopodpierdolenie na remis?
# roboczo - tak 

# co jesli chce zagrać roszadę na królu trefl?
# wprowadzam rozwiazanie ze roszady nie można zrobić na królu..


# rozgrywka zawsze zaczyna się od białych więc nie można konynuować...