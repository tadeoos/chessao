# Author: Tadek Teleżyński
# Board and Pieces classes from Szachao module
# pieces value according to Hans Berliner's system (https://en.wikipedia.org/wiki/Chess_piece_relative_value)

from copy import deepcopy
from math import floor
from termcolor import colored, cprint
import random




####### CARDS #######

KOLORY_KART = {1:'♤', 2:'♡', 3: '♢', 4: '♧'}
class karta:
	def __init__(self, kolor, ranga):
		self.kol = kolor
		self.ran = ranga

	def __eq__(self, o):
		assert karta == type(o)
		return self.kol == o.kol and self.ran == o.ran 

	def __str__(self):
		return self.ran + KOLORY_KART[self.kol]

	def __repr__(self):
		return str(self)

class talia:
	def __init__(self, lista_kart=None):
		if lista_kart is None:
			a = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J','Q', 'K']
			k = [1, 2, 3, 4]
			self.cards = [karta(b,c) for b in k for c in a]
		else:
			self.cards = lista_kart

	def deal(self, n=1):
		return [self.cards.pop() for _ in range(n)]

	def combine(self, karty):
		self.cards.extend(karty)

	def tasuj(self):
		random.shuffle(self.cards)

	def __str__(self):
		return str(self.cards)


class board:
	def __init__(self, rnd=False, fenrep=False):
		self.brd = [0 for i in range(120)]

		for a in range(21,99+1):
			if (a % 10 != 0) and (a % 10 != 9):
					self.brd[a] = ' '

		if not rnd and fenrep==False:
			for i in range(31,39):
				self.brd[i] = pionek('b', i)
			for i in range(81,89):
				self.brd[i] = pionek('c', i)
			fun = [wieza,skoczek,goniec,dama,krol,goniec,skoczek,wieza]
			for i in ([20,'b'],[90,'c']): 
				for j in range(1,9):
					self.brd[i[0]+j] = fun[j-1](i[1], i[0]+j)
		elif fenrep==False:
			for k in ('c', 'b'):
				rand2 = random.choice(self.all_empty())
				self.brd[rand2] = krol(k, rand2)
				for (t,s,a) in [(pionek,8,True),(goniec,2,False),(skoczek,2,False),(wieza,2,False),(dama,1,False)]:
					rand = random.randint(0,s)
					for i in range(rand):
						pos = random.choice(self.all_empty(random_pawn=a))
						self.brd[pos] = t(k,pos)
		else:
			for (k,v) in self.parse_fen(fenrep).items():
				self.brd[k]=v

		self.mapdict = {l+str(j-1) : 10*j+1+'ABCDEFGH'.index(l) for j in range(2,10) for l in 'ABCDEFGH'}
		self.bicie = False
		self.zbite = []
		self.enpass = 300
		self.fullmove = 0
		self.halfmoveclock = 0


	def rusz(self, c, d=None, karta=karta(1, '5'), only_bool=False):
		self.bicie = False
		a = self.mapdict[c]
		if self.is_empty(a):
			raise ValueError
		b = self.mapdict[d]

		# first check if the move is an enappsant one
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
			self.brd[b].position = b
			self.brd[b].mvs_number += 1
			self.brd[a] = ' '
			self.halfmoveclock = 0
			if self.brd[b].kolor == 'c':
				self.fullmove += 1
			#clearing enpass after enpass -> problem in pat functiong
			self.enpass = 300
			return True
		# then set enpassant if possible
		if self.brd[a].name=='pionek' and self.brd[a].mvs_number == 0 and abs(a-b)==20:
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
			self.brd[b].position = b
			self.brd[b].mvs_number += 1
			self.brd[a] = ' '
			# moving the rook
			self.brd[rook_pos[1]] = self.brd[rook_pos[0]]
			self.brd[rook_pos[1]].position = rook_pos[1]
			self.brd[rook_pos[1]].mvs_number += 1
			self.brd[rook_pos[0]] = ' '
			self.halfmoveclock += 1
			if self.brd[b].kolor == 'c':
				self.fullmove += 1
			return True

		# checking for Queen card and valid Queen move
		if karta.ran == 'Q' and self.brd[a].name == 'dama' and self.jaki_typ_zostal(self.brd[a].kolor) != {'krol', 'dama'}:
			if b in self.brd[a].dozwolony(karta,self):
				if only_bool:
					return True
				self.swap(a,b)
				self.brd[b].mvs_number += 1
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
				self.brd[b].position = b
				self.brd[b].mvs_number += 1
				self.brd[a] = ' '
				if self.brd[b].kolor == 'c':
					self.fullmove += 1
				return True

		print('skad {} dokad {} karta {} mvs {}, enpas {}'.format(c,d,karta, self.brd[a].mvs_number, self.enpass))
		raise ValueError
		return False

	def __str__(self):
		print('    {:<2}{:<2}{:<2}{:<2}{:>2}{:>2}{:>2}{:>2}'.format('A','B', 'C', 'D', 'E','F','G','H'))
		# print('    -----------------')
		for i in range(len(self.brd)):
			r = int(((i-(i%10))/10)-1)
			if self.brd[i]==0:
				continue
			if r%2==1:
				if i%10 == 1:
					print('    ', end="")
				if i%10!=8 and (i%10)%2==1:
					print(colored('{!s:} '.format(self.brd[i]), 'grey', attrs=['reverse']),end='')
				elif i%10!=8:
					print(colored('{!s:} '.format(self.brd[i]), 'white', attrs=['reverse']),end='')
				else:
					print(colored('{!s:} '.format(self.brd[i]), 'white', attrs=['reverse'] ), end=' {}\n'.format(r))
			else:
				if i%10 == 1:
					print('    ', end="")
				if i%10!=8 and (i%10)%2==1:
					print(colored('{!s:} '.format(self.brd[i]), 'white', attrs=['reverse']),end='')
				elif i%10!=8:
					print(colored('{!s:} '.format(self.brd[i]), 'grey', attrs=['reverse']),end='')
				else:
					print(colored('{!s:} '.format(self.brd[i]), 'grey', attrs=['reverse'] ), end=' {}\n'.format(r))
				
		return ''

	def is_empty(self, i):
		return self.brd[i]==' '

	def all_empty(self, random_pawn=False):
		if random_pawn:
			return [i for i in range(len(self.brd)) if self.brd[i]==' ' and floor(i/10) not in (2,9)]
		return [i for i in range(len(self.brd)) if self.brd[i]==' ']

	def all_taken(self):
		return [i for i in range(len(self.brd)) if self.brd[i]!=' ' and self.brd[i]!=0]		

	def position_bierki(self, naz, kol):
		return [i for i in self.all_taken() if self.brd[i].name==naz and self.brd[i].kolor==kol]

	def jaki_typ_zostal(self, kolor):
		a = self.all_taken()
		return {self.brd[i].name for i in a if self.brd[i].kolor == kolor}

	def get_piece(self, pos):
		return self.brd[self.mapdict[pos]]

	def get_points(self, col):
		return sum([self.brd[i].val for i in self.all_taken() if self.brd[i].kolor == col])

	def simulate_move(self, fro, to, card):
		fenstr = self.fen().split()[0]
		enp = self.fen().split()[2]
		copy = board(fenrep=fenstr)
		copy.enpass = 300 if enp=='-' else self.mapdict[enp]
		copy.rusz(fro, to, card)
		return copy

	def swap(self, a, b):
		tym = self.brd[b]
		self.brd[b] = self.brd[a]
		self.brd[a] = tym
		if not self.is_empty(b):
			self.brd[b].position = b
		self.brd[a].position = a

	def czy_szach(self, color):
		res = []
		poz_k = self.position_bierki('krol', color)			
		assert len(poz_k) == 1
		return (True, color) if self.pod_biciem(poz_k[0],color) else False

	def check_castle(self, kol):
		k = self.position_bierki('krol', kol)[0]
		w = self.position_bierki('wieza', kol)
		d = {'if': 0, 'lng': 0, 'shrt': 0}
		if self.brd[k].mvs_number > 0 or len(w)==0 or self.czy_szach(kol)==(True, kol):	
			return d
		cntr = 0
		for r in w:
			if self.brd[r].mvs_number > 0:
				continue
			if r<k:
				where = [i for i in range(r+1, k)]
			else:
				where = [i for i in range(k+1, r)]
			c = 0
			for pos in where:
				if self.is_empty(pos)==0 or self.pod_biciem(pos,kol):
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
			res += self.fen_row(row)+'/'
		wc = self.fen_castle('b')
		bc = self.fen_castle('c').lower()
		jc = wc+bc
		c = '-' if jc == '--' else jc
		enp = '-' if self.enpass not in self.mapdict.values() else [k for (k,v) in self.mapdict.items() if v == self.enpass][0]
		ret = [res[:-1], c, str(enp), str(self.halfmoveclock), str(self.fullmove)]
		return ' '.join(ret)

	def fen_castle(self, kol):
		res = ''
		k = self.position_bierki('krol', kol)[0]
		w = self.position_bierki('wieza', kol)
		w.sort()
		if self.brd[k].mvs_number > 0:
			return '-'
		# just temporarily
		if len(w)<2:
			return	'-'
		if self.brd[w[1]].mvs_number == 0:
			res += 'K'
		if self.brd[w[0]].mvs_number == 0:
			res += 'Q'
		if len(res)==0:
			res = '-'
		return res

	def parse_fen(self, fen):
		# return dictionary (pos:piece)
		rows = fen.split('/')
		res_dict = {}
		for i in range(len(rows)):
			res_dict.update(self.parse_row_fen(rows[i], (i+2)*10))
		return res_dict

	def parse_row_fen(self, s, i):
		pos = i + 1
		dic = {}
		y=0
		while y<len(s) and pos<i+9:
			if s[y].isnumeric():
				pos += int(s[y])
			elif s[y]=='P':
				dic[pos]=pionek('b', pos)
				pos += 1
			elif s[y]=='W':
				dic[pos]=wieza('b', pos)
				pos += 1
			elif s[y]=='S':
				dic[pos]=skoczek('b', pos)
				pos += 1
			elif s[y]=='G':
				dic[pos]=goniec('b', pos)
				pos += 1
			elif s[y]=='D':
				dic[pos]=dama('b', pos)
				pos += 1
			elif s[y]=='K':
				dic[pos]=krol('b', pos)
				pos += 1
			elif s[y]=='p':
				dic[pos]=pionek('c', pos)
				pos += 1
			elif s[y]=='w':
				dic[pos]=wieza('c', pos)
				pos += 1
			elif s[y]=='s':
				dic[pos]=skoczek('c', pos)
				pos += 1
			elif s[y]=='g':
				dic[pos]=goniec('c', pos)
				pos += 1
			elif s[y]=='d':
				dic[pos]=dama('c', pos)
				pos += 1
			elif s[y]=='k':
				dic[pos]=krol('c', pos)
				pos += 1
			else:
				raise ValueError
			y+=1
		return dic
	
	def get_fen_rep(self, piece):
		if piece.kolor=='b':
			return piece.name[0].upper()
		else:
			return piece.name[0].lower()

	def fen_row(self, row):
		res = ''
		empty_counter = 0
		for i in row:
			if i==' ':
				empty_counter += 1
			elif empty_counter==0:
				res += self.get_fen_rep(i)
			else:
				res += str(empty_counter)+self.get_fen_rep(i)
				empty_counter = 0
		if empty_counter > 0:
			res += str(empty_counter)
		return res

	def pod_biciem(self, pole, kolor):
		for i in (1,-1,10,-10,9,11,-9,-11):
			a = pole + i
			if (type(self.brd[a])==krol and self.brd[a].kolor!=kolor):
				return True

		for i in (-12,-21,-19,-8,8,19,21,12):
			a = pole + i
			if (type(self.brd[a])==skoczek and self.brd[a].kolor!=kolor):
				return True
		for i in (1,10,-1,-10):
			a = pole + i
			while (self.brd[a]!=0):
				if self.is_empty(a)==0:
					if self.brd[a].kolor!=kolor:
					 	if type(self.brd[a])==wieza or type(self.brd[a])==dama:
					 		return True
					 	else:
					 		break
					else:
						break
				a += i
		for i in (9,11,-11,-9):
			a = pole + i
			while (self.brd[a]!=0):
				if self.is_empty(a)==0:
					if self.brd[a].kolor!=kolor:
					 	if type(self.brd[a])==goniec or type(self.brd[a])==dama:
					 		return True
					 	else:
					 		break
					else:
						break
				a += i

		where = (9,11) if kolor == 'b' else (-9,-11)
		for i in where:
			a = pole + i
			if (type(self.brd[a])==pionek and self.brd[a].kolor!=kolor):
				return True

		return False



#######
######## SZACHY  ########

# class Piece():
# 	def __init__(self, color, position, mvs = 0):
# 		self._color = color
# 		self._position = position
# 		self._mvs_number = mvs
# 		self._history = []
# 		self._name = 'piece'
# 		self._val = 1

class pionek:
	def __init__(self, kolor, position, mvs = 0):
		self.kolor = kolor
		self.position = position
		self.val = 1
		self.mvs_number = mvs
		self.name = 'pionek'

	def dozwolony(self, karta, plansza):
		dop = [10,20] if self.mvs_number == 0 else [10]
		if karta.ran == '2':
			dop.append(dop[-1]+10)
		if self.kolor == 'b':
			for d in dop[::-1]:
				if self.position+d > 119:
					continue
				if plansza.is_empty(self.position+d)==0:
					ind = dop.index(d) 
					dop = dop[:ind]
			a = (9,11)
		else:
			for d in dop[::-1]:
				if self.position-d < 0:
					continue
				if plansza.is_empty(self.position-d)==0:
					ind = dop.index(d) 
					dop = dop[:ind]
			a = (-9, -11)

		for i in a:
			if (plansza.brd[self.position+i]!=0 and plansza.brd[self.position+i]!=' ' and plansza.brd[self.position+i].kolor!=self.kolor) or (plansza.enpass==self.position+i):
				dop.append(abs(i))

		res = [self.position+i if self.kolor=='b' else self.position-i for i in dop]

		return res

	def __str__(self):
		if self.kolor=='b':
			return '♙'
		else:
			return '♟'

class wieza:
	def __init__(self, kolor, position):
		self.kolor = kolor
		self.position = position
		self.val = 5.1
		self.name = 'wieza'
		self.mvs_number = 0
	def dozwolony(self, karta, plansza):
		# plansza.brd[self.position] = ' '
		# if plansza.czy_szach(self.kolor)==(True, self.kolor):
		# 	plansza.brd[self.position] = self
		# 	return []
		# plansza.brd[self.position] = self
		res = []
		for i in (1,10,-1,-10):
			a = self.position + i
			while (plansza.brd[a]!=0):
				if plansza.is_empty(a)==0:
					if plansza.brd[a].kolor!=self.kolor:
						res.append(a)
						break
					else:
						break
				res.append(a)
				a+=i

		# res2 = deepcopy(res)
		# for r in res2:
		# 	pln = plansza.simulate_move(self.position, r, karta)
		# 	if pln.czy_szach(self.kolor)==(True, self.kolor):
		# 		res.remove(r)

		return res

	def __str__(self):
		if self.kolor=='b':
			return '♖'
		else:
			return '♜'

class skoczek:
	def __init__(self, kolor, position):
		self.kolor = kolor
		self.position = position
		self.val = 3.2
		self.name='skoczek'
		self.mvs_number = 0

	def dozwolony(self, karta, plansza):
		res = []
		for i in (-12,-21,-19,-8,8,19,21,12):
			# print(self.position)
			# print(i)
			a = self.position + i
			if plansza.brd[a]!=0:
				if plansza.is_empty(a)==1 or plansza.brd[a].kolor!=self.kolor:
					res.append(a)

		# res2 = deepcopy(res)
		# for r in res2:
		# 	pln = plansza.simulate_move(self.position, r, karta)
		# 	if pln.czy_szach(self.kolor)==(True, self.kolor):
		# 		res.remove(r)
		return res

	def __str__(self):
		if self.kolor=='b':
			return '♘'
		else:
			return '♞'

class goniec:
	def __init__(self, kolor, position):
		self.kolor = kolor
		self.position = position
		self.val = 3.33
		self.name='goniec'
		self.mvs_number = 0

	def dozwolony(self, karta, plansza):
		res = []
		for i in (9,11,-11,-9):
			a = self.position + i
			while (plansza.brd[a]!=0):
				if plansza.is_empty(a)==0:
					if plansza.brd[a].kolor!=self.kolor:
						res.append(a)
						break
					else:
						break
				res.append(a)
				a+=i

		# res2 = deepcopy(res)
		# for r in res2:
		# 	pln = plansza.simulate_move(self.position, r, karta)
		# 	if pln.czy_szach(self.kolor)==(True, self.kolor):
		# 		res.remove(r)
		return res

	def __str__(self):
		if self.kolor=='b':
			return '♗'
		else:
			return '♝'


class dama:
	def __init__(self, kolor, position):
		self.kolor = kolor
		self.position = position
		self.val = 8.8
		self.name='dama'
		self.mvs_number = 0

	def dozwolony(self, karta, plansza):
		if karta.ran == 'Q' and plansza.jaki_typ_zostal(self.kolor) != {'krol', 'dama'}:
			res = [i for i in plansza.all_taken() if (plansza.brd[i].kolor == self.kolor and plansza.brd[i].name in ('pionek', 'goniec','skoczek','wieza'))]
			return res

		res = []
		for i in (9,11,-11,-9,1,-1,10,-10):
			a = self.position + i
			while (plansza.brd[a]!=0):
				if plansza.is_empty(a)==0:
					if plansza.brd[a].kolor!=self.kolor:
						res.append(a)
						break
					else:
						break
				res.append(a)
				a+=i
		return res

	def __str__(self):
		if self.kolor=='b':
			return '♕'
		else:
			return '♛'


class krol:
	def __init__(self, kolor, position):
		self.kolor = kolor
		self.position = position
		self.val = 10
		self.name = 'krol'
		self.mvs_number = 0
	def dozwolony(self, karta, plansza):
		res = []
		if karta.ran == 'K' and karta.kol in (3,4):
			zakres = [1,-1,10,-10,9,11,-9,-11,2,-2,20,-20,18,22,-18,-22]
		else:	
			zakres = [1,-1,10,-10,9,11,-9,-11]
		for i in zakres:
			# print(self.position)
			# print(i)
			a = self.position + i
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

		# cannot move to a position under check
		res2 = deepcopy(res)
		plansza.brd[self.position] = ' '
		for r in res2:
			if plansza.pod_biciem(r, self.kolor):
				res.remove(r)
		plansza.brd[self.position] = self

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





def testy():
	print('\n------ TESTY -------\n')
	pla = board()
	p1 = pionek('b', 31)
	p2 = pionek('c', 81)
	# w = wieza('c', 91)

	pla_los = board(rnd=1)
	while(pla_los.czy_szach(self.kolor)!=(True, 'b')):
		pla_los = board(rnd=1)
	print(pla_los)
	print('Czy szach? {}'.format(pla_los.czy_szach(self.kolor)) )
	# print(pla)
	# print(p1.dozwolony(2))
	# print(p2.dozwolony(7))
	# print(pla.all_empty())
	# print(pla)
	# print(pla_los.position_bierki("goniec", 'b')[0])
	# print(pla_los.brd[pla_los.position_bierki("goniec", 'b')[0]].dozwolony(karta(1, '5'), pla_los))
	# print(pla_los.brd[pla_los.position_bierki("goniec", 'c')[0]].dozwolony(karta(1, '5'), pla_los))
	# print(pla_los.brd[pla_los.position_bierki('dama', 'b')[0]].dozwolony(karta(1, '5'), pla_los))
	# print(pla_los.brd[pla_los.position_bierki('krol', 'b')[0]].dozwolony(karta(1, '5'), pla_los))
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
	# print(pla.position_bierki('krol', 'b'))
	# pla.rusz('E7','E6')
	# pla.rusz('F8','B4')
	# pla.rusz('D2','D3')
	# pla.rusz('D7','D6')
	# pla.rusz('D7','D6')
	# print(pla)
	# print(pla.czy_szach(self.kolor))
	# print(pla.position_bierki('krol', 'b'))
	# print(pla.brd[pla.mapdict['B4']].dozwolony(5, pla))
	return pla_los

# t = testy()

# print('module szachao loaded')