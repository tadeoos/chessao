# Author: Tadek Teleżyński

from szachao import *
import random
import time
import re
import os

def odwrot(a):
	if a=='b':
		return 'c'
	else:
		return 'b'

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
	# out = [x for x in a if x not in b]
	for k in b:
		a.remove(k)
	return a
	# if len(out) == len(a) - len(b):
	# 	return out
	# elif len(b)==1:
	# 	assert len(out)==3
	# 	out.extend(b)
	# 	return out
	# else:
	# 	try:
	# 		assert len(out)==5 or len(out)==2 or len(out)==0
	# 	except Exception as e:
	# 		print('\n out: {} a: {} b: {}'.format(out,a ,b))
	# 		raise AssertionError
	# 	return out


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
			los = random.randint(0,4)
			burn = 1 if los==0 else 0
			card = random.choice(self.reka)
			if not ok_karta([card], talie):
				burn = 1
			if not burn and card.ran=='J':
				ch = [s[0] for s in plansza.jaki_typ_zostal(odwrot(self.kol)) if s!='krol']
				# here is a problem with jack loosing its ability when there is only king left..
				if len(ch)==0:
					return (burn, [card])
				choice = random.choice(ch)
				return (burn, [card], nawaleta(choice))
			return (burn, [card])
		else:
			ask = int(input('Karta: (1,2,3,4,5)?')) - 1
			return self.reka[ask]
			# trza dokończyć..

	def get_three(self, n):
		if self.bot:
			return random.sample(self.reka, n)
		else:
			# functionality for humans
			return None

	def choose_move(self, d, plansza, karta):
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

class gracz_str(gracz):

	def choose_move(self, d, plansza, karta):
		move_list = [[skad,gdzie] for skad in d.keys() for gdzie in d[skad]]
		rating_list = []
		for m in move_list:
			brd = plansza.simulate_move(m[0],m[1], karta)
			check = 0.5 if brd.czy_szach(odwrot(self.kol)) else 0
			# mat = 100 if brd.czy_szach(odwrot(self.kol)) and brd.czy_pat(odwrot(self.kol)) else 0
			broniony = 12 if pod_biciem(plansza.mapdict[m[1]],plansza,self.kol) else 0
			atakowany = 2 if pod_biciem(plansza.mapdict[m[1]],plansza,odwrot(self.kol)) else 0
			rating = (brd.get_points(self.kol) - brd.get_points(odwrot(self.kol))) + (check * broniony) + broniony/3 - atakowany
			rating_list.append((rating, m))
		maks = sorted(rating_list)[-1][0]
		return random.choice([move for (a,move) in rating_list if a==maks])

	def choose_prom(self):
		return 'D'


######## SZACHAO CLASS

class rozgrywka:
	def __init__(self, rnd=1):
		random.seed()
		self.plansza = board(rnd)
		self.karty = talia()
		self.karty.combine(talia().cards)
		self.karty.tasuj()
		tpr = rozd(self.karty)
		self.gracze = (gracz(1,'b',tpr[0]), gracz_str(2,'c',tpr[1]))
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
		self.now_move = None
		self.jack = None
		self.three = 0
		self.four = False
		self.capture = True


	def __str__(self):
		gb = self.get_gracz('b')
		gc = self.get_gracz('c')
		print('\nKupki: |{0:>3} |  |{1:>3} |'.format(str(self.kupki[0][-1]), str(self.kupki[1][-1])))
		print('\nKARTA:  {}{}'.format('!' if self.burned else '',self.now_card))
		print('\n{} {} (white): {}\n'.format(gb.name, gb.nr, gb.reka))
		print('{}'.format(self.plansza))
		print('{} {} (black): {}'.format(gc.name, gc.nr, gc.reka))
		
		
		
		# print('\nTalia: \n{} ...\n'.format(self.karty.cards[-5:][::-1]))
		return ''

	def do_card_buisness(self, kar, three = False):
		player = self.get_gracz(self.to_move)
		
		if self.burned:
			if not three:
				assert len(kar) == 1
			try:
				player.reka = odejmij(player.reka, kar)
				# assert len(player.reka)==5
			except AssertionError as e:
				print('\n three: {} reka {}, kar {}'.format(self.three, player.reka, kar))
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

		assert len(player.reka)==5

	def graj(self, video = False):
		while not self.mat and not self.pat:
			if video:
				os.system('clear')
			self.get_card()
			self.now_move =  self.get_move()
			self.move(self.now_card, self.now_move)
			if video:
				print('{}'.format(self))
				time.sleep(1)

		if video:
			os.system('clear')
			print('\n\n    {}    \n'.format('MAT !' if self.mat else 'PAT !'))
			print(self)

		return True

	def get_card(self):
		# clearing self.capture
		self.capture = True

		player = self.get_gracz(self.to_move)

		w  = self.what_happened()

		# if king of spades was played get card from history (2 halfmoves ago)
		if w[0]==2:
			self.cofnij(self.to_move, w[1])
			card = w[2]

		else:

			card = player.choose_card(self.kupki, self.plansza)
			while(not self.card_ok_to_play(card)):
				card = player.choose_card(self.kupki, self.plansza)

		self.burned = card[0]

		# checking for three
		if self.three > 0 and (card[1][0].ran!='3' or self.burned):
			#if you don't defend yourself on three you have to burn the card (makes three more powerful)
			self.burned = 1
			tmpcar = player.get_three(3) if self.three == 3 else player.get_three(5)
			self.do_card_buisness(tmpcar, three=True)
			self.three = 0
		elif w[0]!=2: self.do_card_buisness(card[1])

		#now_card birth
		self.now_card = card[1][0]

		if len(card)==3:
			self.jack = card[2]
			assert self.jack in self.plansza.jaki_typ_zostal(odwrot(self.to_move))
		else:
			self.jack = None
		if self.now_card.ran == '4' and not self.burned:
			self.capture = False
		if self.now_card.ran == '3' and not self.burned:
			add = sum([3 for c in card[1] if c.ran=='3'])
			assert add>2
			self.three += add

	def get_move(self):
		self.zamiana = False
		player = self.get_gracz(self.to_move)
		# after ace or king of spikes there is no move
		if not self.burned and (self.now_card.ran=='A' or (self.now_card.ran=='K' and self.now_card.kol==1)):
			return []

		w = self.what_happened()
		all_moves = self.possible_moves(self.to_move, self.capture, self.now_card, self.burned, w)
		if len(all_moves)==0:
			return []
		crd = self.now_card if not self.burned else karta(1, '5')
		move = player.choose_move(all_moves, self.plansza, crd)
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
			self.plansza.zbite.append(self.plansza.brd[zam])
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
		s = self.plansza.czy_szach(k)
		if s == (True, k):
			return True
		# elif s == 2:
		# 	return 2
		return False

	def czy_pat(self, k):
		if self.plansza.halfmoveclock==100 or len(self.plansza.all_taken())==2:
			return True
		szach = self.czy_szach(k)
		for kar in self.get_gracz(k).reka:
			if ok_karta([kar], self.kupki):
				if szach and kar.ran=='Q':
					continue
				res = self.possible_moves(k, True, kar)
				if len(res)>0:
					return False
			else:
				res = self.possible_moves(k)
				if len(res)>0:
					return False
		return True

	def get_gracz(self, k):
		return [g for g in self.gracze if g.kol == k][0]

	def cofnij(self, kolor, ruch):
		assert len(self.historia)>2
		a = self.plansza.mapdict[ruch[0]]
		b = self.plansza.mapdict[ruch[1]]

		# clearing enpassant and subtracting move counter
		self.plansza.enpass = 300

		# see if a promotion had been made
		if '=' in self.historia[-2]:
			# if gambit teleżyńskiego occured...
			if 'q' in self.historia[-2].split()[2].lower():
				self.plansza.brd[a] = self.plansza.zbite.pop()
			else:
				self.plansza.brd[b] = self.plansza.zbite.pop() 

		self.plansza.brd[b].mvs_number -= 1

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

		out = talia(do_tasu)

		self.spalone = []
		out.tasuj()
		out.combine(self.karty.cards)
		self.karty = out
		self.kupki=([kup_1], [kup_2])
		all_cards = len(self.karty.cards)+len(self.kupki[0])+len(self.kupki[1])+len(self.spalone)+len(self.gracze[0].reka)+len(self.gracze[1].reka)
		if all_cards!=104:
			print('\nALL CARDS: {}'.format(all_cards))
		# 
		assert all_cards==104

	def what_happened(self):
	# this function is parsing the history to make sense of the situation. returns ints that code a situation.
	# 0 = nothing special, 1 = turn loosing, 2 - king of spades, 3 - king of hearts, 4 - jack
		s = self.historia[-1]
		s2 = self.historia[-2] if len(self.historia)>1 else ''
		ind = s2.index(':') if ':' in s2 else None
		what = s[2]
		# if the card was burned or there is a check, last card doesn't matter
		if what == '!' or self.szach or len(self.historia)==1:
			return (0,)
		elif what == '4' and self.now_card.ran != '4':
			return (1,)
		elif what == 'K' and s[3] == '♤' and ind != None:
			# r = re.search('\s(.+)\s',s2)
			c = self.from_history_get_card(2)
			return (2, [s2[:ind][-2:],s2[ind+1:][:2]], c)
		elif what == 'K' and s[3] == '♡' and ind != None:
			if self.plansza.get_piece(s2[ind+1:][:2]).kolor!=self.to_move:
				return (1,)
			return (3, s2[ind+1:][:2])
		elif what == 'J' and self.now_card.ran != 'J':
			if self.jack not in self.plansza.jaki_typ_zostal(self.to_move):
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
	#if card was burned returns False
		c = from_history_get_card(n)
		if c[0] == 1:
			return False
		return c[1].ran == r and c[1].kol == cl if cl != None else c[1].ran == r

	def from_history_get_card(self, n):
	# returns a card played n turns AGO 
		if n > len(self.historia):
			return None
		s = self.historia[-n]
		r = re.search('\s(.+?)\s',s)
		c = r.group(1)
		return decode_card(c)

	def card_ok_to_play(self, crd):
		# if card is to be burned its always ok to play it
		if crd[0] == 1:
			return True
		c = crd[1][0]
		# conditions that if met block the card
		cond1 = self.szach and (c.ran=='A' or c.ran=='Q')

		# war2 = (kar[-1].ran=='K' and kar[-1].kol==1) and (last_card.ran=='A' or licznik<3 or temp=='ominięta')
		# war3 = (kar[-1].ran=='K' and kar[-1].kol==2) and (licznik<2 or temp=='ominięta')
		# war4 = last_card.ran=='J' and kar[-1].ran=='4' and ok_karta(kar,self.kupki)
		# war5 = kar[-1].ran=='4' and self.szach and len(self.possible_moves(kolej, False, kar[-1]))==0

		if cond1:
			return False

		return True

	def possible_moves(self, kolor, okzbi=True, kar=karta(1,'5'), burned = False, flag = (0,)):
		if burned:
			kar = karta(1,'5')
	
		d = {v:k for (k,v) in self.plansza.mapdict.items()}
		
		if flag[0]==1:
			return {}

		elif flag[0]==2: # king of spades
			a = [self.plansza.mapdict[flag[1][0]]]
		elif flag[0]==3: # king of hearts
			a = [self.plansza.mapdict[flag[1]]]
		elif flag[0]==4: #jack
			a = [i for i in self.plansza.all_taken() if self.plansza.brd[i].kolor == kolor and self.plansza.brd[i].name==flag[1]]
		elif kar.ran=='Q' and len(self.plansza.position_bierki('dama',kolor))>0:
			assert flag[0]==0
			if self.plansza.jaki_typ_zostal(kolor) != {'krol', 'dama'}:
				a = self.plansza.position_bierki('dama',kolor)
			else:
				kar = karta(1, '5')
				a = [i for i in self.plansza.all_taken() if self.plansza.brd[i].kolor == kolor]
		else:
			a = [i for i in self.plansza.all_taken() if self.plansza.brd[i].kolor == kolor]
	
		res = {}
		for i in a:
			skad = d[i]
			if okzbi:
				gdzie = [d[c] for c in self.plansza.brd[i].dozwolony(kar, self.plansza) if type(self.plansza.brd[c])!=krol]
			else:
				gdzie = [d[c] for c in self.plansza.brd[i].dozwolony(kar, self.plansza) if type(self.plansza.brd[c])!=krol and (self.plansza.is_empty(c) or self.plansza.brd[c].kolor == kolor)]
	
			if flag[0]==2:
				try:
					gdzie.remove(flag[1][1])
				except Exception as e:
					print('\n Error in remove! kolor:{} okzbi:{} karta:{} burned: {} flag {} gdzie: {} skad {} a: {}'.format(kolor, okzbi, kar, burned, flag, gdzie, skad, a))
					raise e
			if len(gdzie)>0:
				res[skad]=gdzie

		res2 = deepcopy(res)
		for key in res2:
			for where in res2[key]:
				try:
					pln = self.plansza.simulate_move(key, where, kar)
				except Exception as e:
					print('\n kolor: {} from {} to {} karta {}'.format(kolor, key, where, kar))
					raise e
				if pln.czy_szach(kolor)==(True, kolor):
					res[key].remove(where)
				del pln
		final = {k:v for (k,v) in res.items() if v != []}		
		return final



#### bugi

# [x for x in [] if x not in [szachao.karta(4,'2'), szachao.karta(2,'8'), szachao.karta(2,'10'), szachao.karta(4,'J'), szachao.karta(2,'8')]]

# 
# ♡

# co kiedy król zagrywa specjalnego króla i ma w zasięgu króla przeciwnego?
# - dokleiłem jeszcze w dozwolonym damki warunek na typ ktory zostal
# król się zbija w pewnym momencie (jakim?)
# - dokleilem w self.possible_moves pozycje krola
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

