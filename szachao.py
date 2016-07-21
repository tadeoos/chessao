# próby do szachao
import random
from copy import deepcopy
from termcolor import colored, cprint

def odwrot(a):
	if a=='b':
		return 'c'
	else:
		return 'b'

def get_fen_rep(piece):
	if piece.kolor=='b':
		return piece.name[0].upper()
	else:
		return piece.name[0].lower()

def fen_row(row):
	res = ''
	empty_counter = 0
	for i in row:
		if i==' ':
			empty_counter += 1
		elif empty_counter==0:
			res += get_fen_rep(i)
		else:
			res += str(empty_counter)+get_fen_rep(i)
			empty_counter = 0
	if empty_counter > 0:
		res += str(empty_counter)
	return res

def pod_biciem(pole, plansza, kolor):
	for i in (1,-1,10,-10,9,11,-9,-11):
		a = pole + i
		if (type(plansza.brd[a])==krol and plansza.brd[a].kolor!=kolor):
			return True

	for i in (-12,-21,-19,-8,8,19,21,12):
		a = pole + i
		if (type(plansza.brd[a])==skoczek and plansza.brd[a].kolor!=kolor):
			return True
	for i in (1,10,-1,-10):
		a = pole + i
		while (plansza.brd[a]!=0):
			if plansza.is_empty(a)==0:
				if plansza.brd[a].kolor!=kolor:
				 	if type(plansza.brd[a])==wieza or type(plansza.brd[a])==dama:
				 		return True
				 	else:
				 		break
				else:
					break
			a += i
	for i in (9,11,-11,-9):
		a = pole + i
		while (plansza.brd[a]!=0):
			if plansza.is_empty(a)==0:
				if plansza.brd[a].kolor!=kolor:
				 	if type(plansza.brd[a])==goniec or type(plansza.brd[a])==dama:
				 		return True
				 	else:
				 		break
				else:
					break
			a += i

	if kolor == 'b':
		for i in (9,11):
			a = pole + i
			if (type(plansza.brd[a])==pionek and plansza.brd[a].kolor!=kolor):

				return True
	else:
		for i in (-9,-11):
			a = pole + i
			if (type(plansza.brd[a])==pionek and plansza.brd[a].kolor!=kolor):
				return True

	return False





################ KARTY


class karta:

	def __init__(self, kolor, ranga):
		self.kol = kolor
		self.ran = ranga


	def __eq__(self, other):
		return karta == type(other) and self.kol == other.kol and self.ran == other.ran 

	def __str__(self):
		if self.kol == 1:
			return self.ran+'♤'
		elif self.kol == 2:
			return self.ran+'♡'
		elif self.kol == 3:
			return self.ran+'♢'
		elif self.kol == 4:
			return self.ran+'♧'
		else:
			return 'zła wartość koloru'

	def __repr__(self):
		return str(self)

class talia:
	def __init__(self, lista_kart=[]):
		a = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J','Q', 'K']
		k = [1,2,3,4]
		if len(lista_kart)==0:
			self.cards = [karta(b,c) for b in k for c in a]
		else:
			self.cards = lista_kart
	def deal(self, n=1):
		return [self.cards.pop() for i in range(n)]
	def combine(self, karty):
		self.cards.extend(karty)
	def __str__(self):
		return str(self.cards)
	def tasuj(self):
		random.shuffle(self.cards)





#######  ALL RUCHY

def jaki_typ_zostal(plansza, kolor):
	a = plansza.all_taken()
	res = {plansza.brd[i].name for i in a if plansza.brd[i].kolor == kolor}
	return res


def all_ruchy(plansza, kolor=2, okzbi=True, kar=karta(1,'5'), burned = False, flag = (0,)):
	if burned:
		kar = karta(1,'5')

	d = {v:k for (k,v) in plansza.mapdict.items()}
	
	if kolor==2:
		a = plansza.all_taken()
	
	elif flag[0]==1:
		return {}

	elif kar.ran=='Q' and len(plansza.pozycja_bierki('dama',kolor))>0:
		assert flag[0]==0 or flag[0]==3 or flag[0]==4
		if jaki_typ_zostal(plansza, kolor) != {'krol', 'dama'}:
			a = plansza.pozycja_bierki('dama',kolor)
		else:
			kar = karta(1, '5')
			a = [i for i in plansza.all_taken() if plansza.brd[i].kolor == kolor]
	elif flag[0]==2: # king of spades
		a = [plansza.mapdict[flag[1][0]]]
	elif flag[0]==3: # king of hearts
		a = [plansza.mapdict[flag[1]]]
	elif flag[0]==4:
		a = [i for i in plansza.all_taken() if plansza.brd[i].kolor == kolor and plansza.brd[i].name==flag[1]]
	else:
		a = [i for i in plansza.all_taken() if plansza.brd[i].kolor == kolor]


	res = {}
	for i in a:
		skad = d[i]
		if okzbi:
			gdzie = [d[a] for a in plansza.brd[i].dozwolony(kar, plansza) if type(plansza.brd[a])!=krol]
		else:
			gdzie = [d[a] for a in plansza.brd[i].dozwolony(kar, plansza) if type(plansza.brd[a])!=krol and (plansza.is_empty(a) or plansza.brd[a].kolor == kolor)]

		if flag[0]==2:
			gdzie.remove(flag[1][1])

		if len(gdzie)>0:
			res[skad]=gdzie
	return res





########## PLANSZA
#######



class board:
	def __init__(self, rnd=False):
		self.brd = [0 for i in range(120)]
		a = 21
		while(a < 99):
			if (a % 10 != 0):
				if(a % 10 != 9):
					self.brd[a] = ' '
			a += 1
		if not rnd:
			for i in range(31,39):
				self.brd[i] = pionek('b', i)
			for i in range(81,89):
				self.brd[i] = pionek('c', i)
			for i in ([20,'b'],[90,'c']):
				self.brd[i[0]+1] = wieza(i[1], i[0]+1)
				self.brd[i[0]+2] = skoczek(i[1], i[0]+2)
				self.brd[i[0]+3] = goniec(i[1], i[0]+3)
				self.brd[i[0]+4] = dama(i[1], i[0]+4)
				self.brd[i[0]+5] = krol(i[1], i[0]+5)
				self.brd[i[0]+6] = goniec(i[1], i[0]+6)
				self.brd[i[0]+7] = skoczek(i[1], i[0]+7)
				self.brd[i[0]+8] = wieza(i[1], i[0]+8)
		else:
			for k in ('c', 'b'):
				for i in range(1):
					rand2 = random.randint(21,98)
					while(self.brd[rand2]!=' '):
						rand2 = random.randint(21,98)
					self.brd[rand2] = krol(k, rand2)
				rand = random.randint(0,8)
				for i in range(rand):
					rand2 = random.randint(31,78)
					while(self.brd[rand2]!=' '):
						rand2 = random.randint(21,98)
					self.brd[rand2] = pionek(k, rand2)
				rand = random.randint(0,2)
				for i in range(rand):
					rand2 = random.randint(21,98)
					while(self.brd[rand2]!=' '):
						rand2 = random.randint(21,98)
					self.brd[rand2] = goniec(k, rand2)
				rand = random.randint(0,2)
				for i in range(rand):
					rand2 = random.randint(21,98)
					while(self.brd[rand2]!=' '):
						rand2 = random.randint(21,98)
					self.brd[rand2] = skoczek(k, rand2)
				rand = random.randint(0,2)
				for i in range(rand):
					rand2 = random.randint(21,98)
					while(self.brd[rand2]!=' '):
						rand2 = random.randint(21,98)
					self.brd[rand2] = wieza(k, rand2)
				rand = random.randint(0,1)
				for i in range(rand):
					rand2 = random.randint(21,98)
					while(self.brd[rand2]!=' '):
						rand2 = random.randint(21,98)
					self.brd[rand2] = dama(k, rand2)
				# rand = random.randint(0,1)



		self.mapdict = {'A1': 21,'A2': 31,'A3': 41,'A4': 51,'A5': 61,'A6': 71,'A7': 81,'A8': 91,'B1': 22,'B2': 32,'B3': 42,'B4': 52,'B5': 62,'B6': 72,'B7': 82,'B8': 92,'C1': 23,'C2': 33,'C3': 43,'C4': 53,'C5': 63,'C6': 73,'C7': 83,'C8': 93,'D1': 24,'D2': 34,'D3': 44,'D4': 54,'D5': 64,'D6': 74,'D7': 84,'D8': 94,'E1': 25,'E2': 35,'E3': 45,'E4': 55,'E5': 65,'E6': 75,'E7': 85,'E8': 95,'F1': 26,'F2': 36,'F3': 46,'F4': 56,'F5': 66,'F6': 76,'F7': 86,'F8': 96,'G1': 27,'G2': 37,'G3': 47,'G4': 57,'G5': 67,'G6': 77,'G7': 87,'G8': 97,'H1': 28,'H2': 38,'H3': 48,'H4': 58,'H5': 68,'H6': 78,'H7': 88, 'H8': 98}
		self.bicie = False
		self.zbite = []
		self.enpass = 300
		self.stanpocz = self.repdict()
		self.fullmove = 0
		self.halfmoveclock = 0


	def rusz(self, c, d=None, karta=karta(1, '5'), only_bool=False):
		self.bicie = False
		a = self.mapdict[c]
		if self.is_empty(a):
			return False
		if d == None:
			res = [key for (key,val) in self.mapdict.items() if val in self.brd[a].dozwolony(karta,self.brd)]
			return 'Gdzie chcesz się ruszyć?\nMożliwe pola: {}'.format(res)
		b = self.mapdict[d]
		# en passant

		#najpierw sprawdzam czy jest bicie w przelocie
		if self.brd[a].name == 'pionek' and self.enpass == b:
			if only_bool:
					return True
			assert self.is_empty(b)
			self.bicie = True
			if self.brd[a].kolor == 'b':
				self.zbite.append(self.brd[b-10])
				self.brd[b-10] = ' '
			else:
				self.zbite.append(self.brd[b+10])
				self.brd[b+10] = ' '				
			self.brd[b] = self.brd[a]
			self.brd[b].pozycja = b
			self.brd[b].ruszony = True
			self.brd[a] = ' '
			self.halfmoveclock = 0
			if self.brd[b].kolor == 'c':
				self.fullmove += 1
			return True
		# potem ustawiam enpassant
		if self.brd[a].name == 'pionek'and self.brd[a].ruszony==False and abs(a-b)==20:
			self.enpass = (a+b)/2
		else:
			self.enpass = 300
		#checking for castle
		if (karta.ran != 'K' or karta.kol not in (3,4)) and self.brd[a].name == 'krol' and abs(b-a)==2:
			if only_bool:
				return True
			# determining rook position
			rook_pos = (b-1,b+1) if b<a else (b+1,b-1)
			# moving the king
			self.brd[b] = self.brd[a]
			self.brd[b].pozycja = b
			self.brd[b].ruszony = True
			self.brd[a] = ' '
			# moving the rook
			self.brd[rook_pos[1]] = self.brd[rook_pos[0]]
			self.brd[rook_pos[1]].pozycja = rook_pos[1]
			self.brd[rook_pos[1]].ruszony = True
			self.brd[rook_pos[0]] = ' '
			self.halfmoveclock += 1
			if self.brd[b].kolor == 'c':
				self.fullmove += 1
			return True

		# checking for Queen card and valid Queen move
		if karta.ran == 'Q' and self.brd[a].name == 'dama' and jaki_typ_zostal(self, self.brd[a].kolor) != {'krol', 'dama'}:
			if b in self.brd[a].dozwolony(karta,self):
				if only_bool:
					return True
				self.swap(a,b)
				self.brd[b].ruszony = True
				self.halfmoveclock += 1
				if self.brd[b].kolor == 'c':
					self.fullmove += 1
				return True
		else:
		# default move
			if b in self.brd[a].dozwolony(karta,self):
				if only_bool:
					return True
				if self.brd[a].name == 'pionek':
					self.halfmoveclock = 0
				else:
					self.halfmoveclock += 1
				if self.is_empty(b)==0:
					self.bicie = True
					self.halfmoveclock = 0
					self.zbite.append(self.brd[b])
				self.brd[b] = self.brd[a]
				self.brd[b].pozycja = b
				self.brd[b].ruszony = True
				self.brd[a] = ' '
				if self.brd[b].kolor == 'c':
					self.fullmove += 1
				return True
		print('\n !!! ERROR W BOARD.RUSZ DOSTAŁEM ZŁY INPUT!!!!')
		return False

	def __str__(self):
		for i in range(len(self.brd)):
			tpr = [[]]
			r = int(((i-(i%10))/10)-1)
			if self.brd[i]==0:
				continue
			if r%2==1:
				if i%10!=8 and (i%10)%2==1:
					print(colored('{!s:} '.format(self.brd[i]), 'grey', attrs=['reverse']),end='')
				elif i%10!=8:
					print(colored('{!s:} '.format(self.brd[i]), 'white', attrs=['reverse']),end='')
				else:
					print(colored('{!s:} '.format(self.brd[i]), 'white', attrs=['reverse'] ), end=' | {}\n'.format(r))
			else:
				if i%10!=8 and (i%10)%2==1:
					print(colored('{!s:} '.format(self.brd[i]), 'white', attrs=['reverse']),end='')
				elif i%10!=8:
					print(colored('{!s:} '.format(self.brd[i]), 'grey', attrs=['reverse']),end='')
				else:
					print(colored('{!s:} '.format(self.brd[i]), 'grey', attrs=['reverse'] ), end=' | {}\n'.format(r))
				
		print('-----------------')
		return '{} {} {} {} {} {} {} {}'.format('A','B', 'C', 'D', 'E','F','G','H')

	def is_empty(self, i):
		return self.brd[i]==' '

	def all_empty(self):
		return [i for i in range(len(self.brd)) if self.brd[i]==' ']

	def all_taken(self):
		return [i for i in range(len(self.brd)) if self.brd[i]!=' ' and self.brd[i]!=0]		

	def pozycja_bierki(self, naz, kol):
		return [i for i in self.all_taken() if self.brd[i].name==naz and self.brd[i].kolor==kol]

	def get_piece(self, pos):
		return self.brd[self.mapdict[pos]]

	def repdict(self):
		return { p : self.brd[p] for p in range(21,89) }

	def swap(self, a, b):
		tym = self.brd[b]
		self.brd[b] = self.brd[a]
		self.brd[a] = tym
		if not self.is_empty(b):
			self.brd[b].pozycja = b
		self.brd[a].pozycja = a

	def czy_szach(self, karta=karta(1,'5')):
		res = []
		for k in ('c','b'):
			poz_k = self.pozycja_bierki('krol', k)

			if len(poz_k) != 1:
				print('\n{}'.format(self))
				
			assert len(poz_k) == 1

			if pod_biciem(poz_k[0],self,k):
				res.append((True, k))
		if len(res)==1:
			return res[0]
		elif len(res)==2:
			# print('mam oba')
			return 2
			# for i in [a for a in self.all_taken() if self.brd[a].kolor!=k]:
			# 	if poz_k[0] in self.brd[i].dozwolony(karta, self):
			# 		return (True, k)
		return False

	def check_castle(self, kol):
		k = self.pozycja_bierki('krol', kol)[0]
		w = self.pozycja_bierki('wieza', kol)
		d = {'if': 0, 'lng': 0, 'shrt': 0}
		if self.brd[k].ruszony == True or len(w)==0 or self.czy_szach()==(True, kol):	
			return d
		cntr = 0
		for r in w:
			if self.brd[r].ruszony == True:
				continue
			if r<k:
				where = [i for i in range(r+1, k)]
			else:
				where = [i for i in range(k+1, r)]
			c = 0
			for pos in where:
				if self.is_empty(pos)==0 or pod_biciem(pos,self,kol):
					break
				else:
					c+=1
			if c == len(where):
				cntr+=1
				if r<k:
					d['lng']=r+1
				else:
					d['shrt']=r-1
		d['if']=cntr
		return d

	def fen(self):
		res = ''
		for i in range(2,10):
			start = i*10 + 1
			end = start + 8
			row = self.brd[start:end]
			res += fen_row(row)+'/'
		wc = self.fen_castle('b')
		bc = self.fen_castle('c').lower()
		jc = wc+bc
		c = '-' if jc == '--' else jc
		enp = '-' if self.enpass not in self.mapdict.values() else [k for (k,v) in self.mapdict.items() if v == self.enpass][0]

		return [res[:-1], c, enp, self.halfmoveclock, self.fullmove]


	def fen_castle(self, kol):
		res = ''
		k = self.pozycja_bierki('krol', kol)[0]
		w = self.pozycja_bierki('wieza', kol)
		w.sort()
		if self.brd[k].ruszony:
			return '-'
		# just temporarily
		if len(w)<2:
			return	'-'
		if self.brd[w[1]].ruszony == False:
			res += 'K'
		if self.brd[w[0]].ruszony == False:
			res += 'Q'
		if len(res)==0:
			res = '-'
		return res

#######
######## SZACHY
########




class pionek:
	def __init__(self, kolor, pozycja):
		self.kolor = kolor
		self.pozycja = pozycja
		self.ruszony = False
		self.name = 'pionek'
	def dozwolony(self, karta, plansza):
		# poz = self.pozycja
		# plansza.brd[self.pozycja] = ' '
		# if plansza.czy_szach()==(True, self.kolor):
		# 	plansza.brd[self.pozycja] = self
		# 	print('jestem tu')
		# 	return []
		# plansza.brd[self.pozycja] = self
		dop = [10,20]
		if self.ruszony:
			dop = [10]
		if karta.ran == '2':
			dop.append(dop[-1]+10)
		if self.kolor == 'b':
			for d in dop[::-1]:
				if self.pozycja+d > 119:
					continue
				if plansza.is_empty(self.pozycja+d)==0:
					ind = dop.index(d) 
					dop = dop[:ind]
			a = (9,11)
		else:
			for d in dop[::-1]:
				if self.pozycja-d < 0:
					continue
				if plansza.is_empty(self.pozycja-d)==0:
					ind = dop.index(d) 
					dop = dop[:ind]
			a = (-9, -11)

		for i in a:
			if (plansza.brd[self.pozycja+i]!=0 and plansza.brd[self.pozycja+i]!=' ' and plansza.brd[self.pozycja+i].kolor!=self.kolor) or plansza.enpass==self.pozycja+i:
				# print('bicie pionka', self.pozycja, i)
				dop.append(abs(i))

		# if karta in (3,4,5,6,7,8,9,10):
		res = [self.pozycja+i if self.kolor=='b' else self.pozycja-i for i in dop]

		res2 = deepcopy(res)
		pln = deepcopy(plansza)

		for r in res2:
			x = pln.brd[r]
			pln.brd[self.pozycja] = ' '
			pln.brd[r] = self
			if pln.czy_szach()==(True, self.kolor) or pln.czy_szach()==2:
				# print(r)
				res.remove(r)
			pln.brd[self.pozycja] = self
			pln.brd[r] = x

		return res

	def __str__(self):
		if self.kolor=='b':
			return '♙'
		else:
			return '♟'

class wieza:
	def __init__(self, kolor, pozycja):
		self.kolor = kolor
		self.pozycja = pozycja
		self.name = 'wieza'
		self.ruszony = False
	def dozwolony(self, karta, plansza):
		# plansza.brd[self.pozycja] = ' '
		# if plansza.czy_szach()==(True, self.kolor):
		# 	plansza.brd[self.pozycja] = self
		# 	return []
		# plansza.brd[self.pozycja] = self
		res = []
		for i in (1,10,-1,-10):
			a = self.pozycja + i
			while (plansza.brd[a]!=0):
				if plansza.is_empty(a)==0:
					if plansza.brd[a].kolor!=self.kolor:
						res.append(a)
						break
					else:
						break
				# print(a)
				# print(plansza.is_empty(a))
				res.append(a)
				a+=i

		res2 = deepcopy(res)
		pln = deepcopy(plansza)

		for r in res2:
			x = pln.brd[r]
			pln.brd[self.pozycja] = ' '
			pln.brd[r] = self
			if pln.czy_szach()==(True, self.kolor) or pln.czy_szach()==2:
				# print(r)
				res.remove(r)
			pln.brd[self.pozycja] = self
			pln.brd[r] = x

		# plansza.brd[self.pozycja] = ' '
		# if plansza.czy_szach()==(True, self.kolor):
		# 	plansza.brd[self.pozycja] = self
		# 	return []
		# plansza.brd[self.pozycja] = self

		return res

	def __str__(self):
		if self.kolor=='b':
			return '♖'
		else:
			return '♜'

class skoczek:
	def __init__(self, kolor, pozycja):
		self.kolor = kolor
		self.pozycja = pozycja
		self.name='skoczek'
		self.ruszony = False
	def dozwolony(self, karta, plansza):
		res = []
		for i in (-12,-21,-19,-8,8,19,21,12):
			# print(self.pozycja)
			# print(i)
			a = self.pozycja + i
			if plansza.brd[a]!=0:
				if plansza.is_empty(a)==1 or plansza.brd[a].kolor!=self.kolor:
					res.append(a)

		res2 = deepcopy(res)
		pln = deepcopy(plansza)

		for r in res2:
			x = pln.brd[r]
			pln.brd[self.pozycja] = ' '
			pln.brd[r] = self
			if pln.czy_szach()==(True, self.kolor) or pln.czy_szach()==2:
				# print(r)
				res.remove(r)
			pln.brd[self.pozycja] = self
			pln.brd[r] = x
		return res

	def __str__(self):
		if self.kolor=='b':
			return '♘'
		else:
			return '♞'

class goniec:
	def __init__(self, kolor, pozycja):
		self.kolor = kolor
		self.pozycja = pozycja
		self.name='goniec'
		self.ruszony = False
	def dozwolony(self, karta, plansza):
		res = []
		for i in (9,11,-11,-9):
			a = self.pozycja + i
			while (plansza.brd[a]!=0):
				if plansza.is_empty(a)==0:
					if plansza.brd[a].kolor!=self.kolor:
						res.append(a)
						break
					else:
						break
				res.append(a)
				a+=i

		res2 = deepcopy(res)
		pln = deepcopy(plansza)

		for r in res2:
			x = pln.brd[r]
			pln.brd[self.pozycja] = ' '
			pln.brd[r] = self
			if pln.czy_szach()==(True, self.kolor) or pln.czy_szach()==2:
				# print(r)
				res.remove(r)
			pln.brd[self.pozycja] = self
			pln.brd[r] = x
		return res

	def __str__(self):
		if self.kolor=='b':
			return '♗'
		else:
			return '♝'


class dama:
	def __init__(self, kolor, pozycja):
		self.kolor = kolor
		self.pozycja = pozycja
		self.name='dama'
		self.ruszony = False
	def dozwolony(self, karta, plansza):
		if karta.ran == 'Q' and jaki_typ_zostal(plansza, self.kolor) != {'krol', 'dama'}:
			res = [i for i in plansza.all_taken() if (plansza.brd[i].kolor == self.kolor and plansza.brd[i].name in ('pionek', 'goniec','skoczek','wieza'))]
			return res

		res = []
		for i in (9,11,-11,-9,1,-1,10,-10):
			a = self.pozycja + i
			while (plansza.brd[a]!=0):
				if plansza.is_empty(a)==0:
					if plansza.brd[a].kolor!=self.kolor:
						res.append(a)
						break
					else:
						break
				res.append(a)
				a+=i
		res2 = deepcopy(res)
		pln = deepcopy(plansza)

		for r in res2:
			x = pln.brd[r]
			pln.brd[self.pozycja] = ' '
			pln.brd[r] = self
			if pln.czy_szach()==(True, self.kolor) or pln.czy_szach()==2:
				# print(r)
				res.remove(r)
			pln.brd[self.pozycja] = self
			pln.brd[r] = x		
		return res

	def __str__(self):
		if self.kolor=='b':
			return '♕'
		else:
			return '♛'


class krol:
	def __init__(self, kolor, pozycja):
		self.kolor = kolor
		self.pozycja = pozycja
		self.name = 'krol'
		self.ruszony = False
	def dozwolony(self, karta, plansza):
		res = []
		if karta.ran == 'K' and karta.kol in (3,4):
			zakres = [1,-1,10,-10,9,11,-9,-11,2,-2,20,-20,18,22,-18,-22]
		else:	
			zakres = [1,-1,10,-10,9,11,-9,-11]
		for i in zakres:
			# print(self.pozycja)
			# print(i)
			a = self.pozycja + i
			if a>20 and a<99 and plansza.brd[a]!=0:
				if plansza.is_empty(a):
					res.append(a)
					continue
				elif plansza.brd[a].kolor!=self.kolor:
					b = 2*i
					if b in zakres:
						zakres.remove(b)
					res.append(a)
				else:
					continue

		# print(res)
		res2 = deepcopy(res)
		plansza.brd[self.pozycja] = ' '
		for r in res2:
			if pod_biciem(r, plansza, self.kolor):
				res.remove(r)
		plansza.brd[self.pozycja] = self

		# checking for castle / cannot castle on a special king card
		cstl = plansza.check_castle(self.kolor)
		if cstl['if']>0 and (karta.ran != 'K' or karta.kol not in (3,4)):
			res.extend([i for i in cstl.values() if i > 10])


		return res
	def __str__(self):
		if self.kolor=='b':
			return '♔'
		else:
			return '♚'



## testy
def szach_po_ruchu(plansza, ruch, kol, karta):
	a = ruch[0]
	b = ruch[1]
	plan = deepcopy(plansza)
	if karta.ran == 'Q' and plan.brd[a].name == 'dama':
		plan.swap(a,b)
		return plan.czy_szach() != (True, kol)
	else:
		plan.brd[b] = plan.brd[a]
		plan.brd[b].pozycja = b
		plan.brd[b].ruszony = True
		plan.brd[a] = ' '
		return plan.czy_szach() != (True, kol)
# 
	print('Coś się rozjebało w szach_po_ruchu')
	return 'error'





def testy():
	print('\n------ TESTY -------\n')
	pla = board()
	p1 = pionek('b', 31)
	p2 = pionek('c', 81)
	# w = wieza('c', 91)

	pla_los = board(rnd=1)
	while(pla_los.czy_szach()!=(True, 'b')):
		pla_los = board(rnd=1)
	print(pla_los)
	print('Czy szach? {}'.format(pla_los.czy_szach()) )
	# print(pla)
	# print(p1.dozwolony(2))
	# print(p2.dozwolony(7))
	# print(pla.all_empty())
	# print(pla)
	# print(pla_los.pozycja_bierki("goniec", 'b')[0])
	# print(pla_los.brd[pla_los.pozycja_bierki("goniec", 'b')[0]].dozwolony(karta(1, '5'), pla_los))
	# print(pla_los.brd[pla_los.pozycja_bierki("goniec", 'c')[0]].dozwolony(karta(1, '5'), pla_los))
	# print(pla_los.brd[pla_los.pozycja_bierki('dama', 'b')[0]].dozwolony(karta(1, '5'), pla_los))
	# print(pla_los.brd[pla_los.pozycja_bierki('krol', 'b')[0]].dozwolony(karta(1, '5'), pla_los))
	# print(pla.brd[92].dozwolony(7, pla))
	# print(pla.brd[93].dozwolony(7, pla))
	# print(pla.brd[94].dozwolony(7, pla))
	# print(pla.brd[95].dozwolony(7, pla))
	all_ruchy(pla_los, 'b')
	# for i in pla_los.all_taken():
	# 	d = {v:k for (k,v) in pla_los.mapdict.items()}
	# 	print(d[i])
	# 	print([d[a] for a in pla_los.brd[i].dozwolony(karta(1,'5'), pla_los)])
	# pla.rusz('A7','A6')
	# pla.rusz('E2','E4')
	# print(pla.rusz('G7'))
	# print(pla)

	# tal = talia()
	# print(tal.cards)
	# # tal.deal()
	# tal.tasuj()
	# print(tal.cards)
	# tal.tasuj()
	# print(tal.cards)
	# print(len(tal.cards))
	# print(pla.pozycja_bierki('krol', 'b'))
	# pla.rusz('E7','E6')
	# pla.rusz('F8','B4')
	# pla.rusz('D2','D3')
	# pla.rusz('D7','D6')
	# pla.rusz('D7','D6')
	# print(pla)
	# print(pla.czy_szach())
	# print(pla.pozycja_bierki('krol', 'b'))
	# print(pla.brd[pla.mapdict['B4']].dozwolony(5, pla))
	return pla_los

# t = testy()

# print('module szachao loaded')