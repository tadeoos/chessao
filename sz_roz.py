from szachao import *

def rozd(tal):
	a=[]
	b=[]
	for i in range(5):
		a.append(tal.cards.pop())
		b.append(tal.cards.pop())
	return (a,b,tal)

def karta_z_str(s):
	return karta(int(s[-1]), s[:-1])

def schodki_check(lis):
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

def ktora_kupka(karta, kupki):
	for i in range(2):
		if karta[0].kol == kupki[i][-1].kol or karta[0].ran == kupki[i][-1].ran or kupki[i][-1].ran=='Q'or karta[0].ran=='Q':
			return i
	return 3

def rozpakuj_input(inp):
	a = inp.split()
	if len(a)==3:
		a[0] = [karta_z_str(s) for s in a[0].split(',')]
	elif len(a)==1:
		a[0] = [karta_z_str(s) for s in a[0].split(',')]
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



class gracz:
	def __init__(self, ida, kol, reka=[]):
		self.nr = ida
		self.kol = kol
		self.reka = reka

	def __str__(self):
		return 'Gracz {}'.format(self.nr)
	def __repr__(self):
		return 'Gracz {}'.format(self.nr)


class rozgrywka:
	def __init__(self):
		self.plansza = board(rnd=1)
		self.karty = talia()
		self.karty.combine(talia().cards)
		self.karty.tasuj()
		tpr = rozd(self.karty)
		self.gracze = (gracz(1,'b',tpr[0]), gracz(2,'c',tpr[1]))
		self.karty = tpr[2]
		self.kupki = ([self.karty.cards.pop()], [self.karty.cards.pop()])
		self.szach = False
		self.mat = False
		self.spalone = []
		self.historia = []

		# self.blotki = (5,6,7,8,9,10)
		# self.indy = (2,'K')
		# self.roz = ('A', 3, 4, 'J', 'K', 'Q')

	def __str__(self):
		print(self.plansza)
		print('\nKupki:   |{0:>3} |  |{1:>3} |\n'.format(str(self.kupki[0][-1]), str(self.kupki[1][-1])))
		print('Gracz 1: {}, kolor: {}'.format(self.gracze[0].reka, self.gracze[0].kol))
		print('Gracz 2: {}. kolor: {}'.format(self.gracze[1].reka, self.gracze[1].kol))
		return '\nTalia: \n{} ...\n'.format(self.karty.cards[-5:][::-1])

	def graj(self):
		kolej = 'b'
		last_card = karta(1,'5')

		## ROZGRYWKA
		while(self.mat==0):
			
			print('----------------------------------------')
			print(self)

			spalona = False
			gr = self.get_gracz(kolej)

			self.szach = self.czy_szach(kolej)
			print("\nRUCH: {} {}\n".format(kolej, gr))

			if czy_pion_na_koncu(self.plansza, odwrot(kolej))>0:
				print('Coś nie halo, bo niezamieniony pion poprzedniego gracza na końcu stoi')

			if self.szach:
				print('Szachao...')
				if self.czy_pat(kolej):
					print('PO SZACHALE!\n{} wygrał grę'.format(gr))
					self.mat = True
					return 'koniec'
			elif self.czy_pat(kolej):
				print('PAT')
				return 'koniec'

# 			a = input('''jaka karte zagrywasz, którym pionkiem chcesz się ruszyć, gdzie
# [1 - Pik, 2 - Kier, 3 - Karo, 4 - Trefl]
# (siódemka pik, ruch z A2 na A3)
# np. '71 A2 A3' 
# (schodki 7,8,9 w pikach - oddziel karty przecinkiem bez spacji)
# '71,81,91 A2 A3' 

# (type e to exit)\n''').upper()

			a = input('KARTA: ').upper()

			if a == 'E':
				break;




			z = rozpakuj_input(a)


			if len(z)==3:
				for p in z[0]:
					assert p in gr.reka
				assert z[2] in self.plansza.mapdict
				assert z[1] in self.plansza.mapdict

			if not ok_karta(z[0],self.kupki):
				print('nie możesz wyłożyć tych kart..\n\n')
				if len(z[0])>1:
					continue
				b = input('Chcesz spalić tę kartę? (t/n)')
				if b == 'n':
					continue
				else:
					spalona = True

			if not spalona and z[0][-1].ran == 'A':
				gr.reka = [x for x in gr.reka if x not in z[0]]
				self.kupki[ktora_kupka(z[0], self.kupki)].extend(z[0])
				tas = self.karty.deal(len(z[0]))
				gr.reka.extend(tas)
				self.historia.append([gr]+z)
				for g in self.gracze:
					g.kol = odwrot(g.kol)
				last_card = z[0][-1]
				continue

			if self.plansza.brd[self.plansza.mapdict[z[1]]].kolor != kolej:
				print('to nie twój pionek...\n\n')
			# print(z)

			# print('Możliwe ruchy tej bierki \n {}'.format() )
			if not spalona:
				ruch = self.plansza.rusz(z[1],z[2],z[0][-1])
			else:
				ruch = self.plansza.rusz(z[1],z[2])

			if ruch:
				if self.czy_szach(kolej):
					print('SZACH PO MOIM RUCHU, KOŃCZĘ PRACĘ')
					self.mat=True
					break
				zam = czy_pion_na_koncu(self.plansza, kolej)
				if zam>0:
					q = input('Na jaką figurę chcesz zamienić piona?\nD - Dama\nG - Goniec\nS - Skoczek\nW - Wieża\n').upper()
					if q == 'E':
						break
					elif q=='D':
						self.plansza.brd[zam] = dama(kolej, zam)
					elif q=='G':
						self.plansza.brd[zam] = goniec(kolej, zam)
					elif q=='S':
						self.plansza.brd[zam] = skoczek(kolej, zam)
					elif q=='W':
						self.plansza.brd[zam] = wieza(kolej, zam)
					else:
						print('wrong input')

				gr.reka = [x for x in gr.reka if x not in z[0]]
				# print(z[0])
				# print([x for x in gr.reka if x not in z[0]])
				# print(gr.reka)
				if ktora_kupka(z[0], self.kupki) == 3:
					self.spalone.extend(z[0])
				else:
					self.kupki[ktora_kupka(z[0], self.kupki)].extend(z[0])

				if len(self.karty.cards)<len(z[0]):
					pass #przetasowanie talii
				tas = self.karty.deal(len(z[0]))
				gr.reka.extend(tas)

				if spalona:
					self.historia.append([gr,'spalona']+z)
				else:
					self.historia.append([gr]+z)
				last_card = z[0][-1]
				kolej = odwrot(kolej)	
			else:
				print('\n!!! ruch nie dozwolony !!!\n\n')



		return 'Dzięki za grę'

	def czy_szach(self, k):
		s = self.plansza.czy_szach()
		if s == (True, k):
			return True
		elif s == 2:
			return 2
		return False

	def czy_pat(self, k):
		for kar in self.get_gracz(k).reka:
			if ok_karta([kar], self.kupki):
				res = all_ruchy(self.plansza, k, kar)
				if len(res)>0:
					return False
			else:
				res = all_ruchy(self.plansza, k)
				if len(res)>0:
					return False
		return True

	def get_gracz(self, k):
		return [g for g in self.gracze if g.kol == k][0]



li = [
[karta(1, '5'), karta(1, '6'),karta(1, '7'),karta(1, '8')],
[karta(1, '5'), karta(2, '6'),karta(1, '7'),karta(1, '8')],
[karta(1, '5'), karta(2, '5'),karta(1, '7'),karta(1, '8')],
[karta(1, '5'), karta(2, '5'),karta(2, '6'),karta(2, '7')],
[karta(1, '5'), karta(2, '5'),karta(3, '5'),karta(3, '5')],
[karta(1, '5'), karta(1, '6'),karta(1, '8'),karta(1, '9')]
]

roz = rozgrywka()
while(roz.plansza.czy_szach()==2):
	roz = rozgrywka()
# print(rozpakuj_input('101,53,K3 A1 A2'))
# print(roz)
# for g in roz.gracze:
# 	for k in g.reka:
# 		print(k)
# 		print(ok_karta([k],roz.kupki))
# print(karta_z_str('101'))

roz.graj()
# print(type(roz.kupki[0][-1]))
def test_stat(n=5, m=2000):
	for i in range(n):
		res = [0,0,0,0]
		for i in range(m):
			roz = rozgrywka()
			if roz.czy_szach('c')==2:
				res[3]+=1
			elif roz.czy_szach('c'):
				res[0]+=1
			elif roz.czy_szach('b'):
				res[1]+=1
			else:
				res[2]+=1
		
		print(res)

# test_stat(3)
# print('\n schodki ...')
# for l in li:
# 	print(l)
# 	print(schodki_check(l))
