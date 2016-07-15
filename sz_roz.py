from szachao import *
import random
import time

def rozd(tal):
	a=[]
	b=[]
	for i in range(5):
		a.append(tal.cards.pop())
		b.append(tal.cards.pop())
	return (a,b,tal)

def karta_z_str(s):
	return karta(int(s[-1]), s[:-1])

def nawaleta(c):
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



class gracz:
	def __init__(self, ida, kol, reka=[], name='gracz'):
		self.nr = ida
		self.kol = kol
		self.reka = reka
		self.name = name

	def __str__(self):
		return 'Gracz {}'.format(self.nr)
	def __repr__(self):
		return 'Gracz {}'.format(self.nr)

class rozgrywka:
	def __init__(self, rnd=1):
		self.plansza = board(rnd)
		self.karty = talia()
		self.karty.combine(talia().cards)
		self.karty.tasuj()
		self.karty.tasuj()
		tpr = rozd(self.karty)
		self.gracze = (gracz(1,'b',tpr[0]), gracz(2,'c',tpr[1]))
		self.karty = tpr[2]
		self.kupki = ([self.karty.cards.pop()], [self.karty.cards.pop()])
		self.szach = False
		self.mat = False
		self.pat = False
		self.spalone = []
		self.historia = []
		self.zamiana = False

		# self.blotki = (5,6,7,8,9,10)
		# self.indy = (2,'K')
		# self.roz = ('A', 3, 4, 'J', 'K', 'Q')

	def __str__(self):
		print(self.plansza)
		print('\nKupki:   |{0:>3} |  |{1:>3} |\n'.format(str(self.kupki[0][-1]), str(self.kupki[1][-1])))
		print('Gracz 1: {}, kolor: {}'.format(self.gracze[0].reka, self.gracze[0].kol))
		print('Gracz 2: {}. kolor: {}'.format(self.gracze[1].reka, self.gracze[1].kol))
		return '\nTalia: \n{} ...\n'.format(self.karty.cards[-5:][::-1])

	def graj(self, rnd = False, test=False):
		kolej = 'b'
		last_card = karta(1,'5')
		last_move = []
		now_card = None
		walet = False
		trojka = 0
		czworka = False
		ok_zbicie = True
		kpik = []
		kkier = []
		gr = self.get_gracz('c')
###########
		###  ROZGRYWKA

		licznik = 0
		while(self.mat==0):
			licznik += 1
			# if rnd:
				# print ("\rRuchów: ", licznik, end="")
			if not test:
				print('----------------------------------------')
				print(self)

			self.szach = self.czy_szach(kolej)

			if self.szach:
				if not test:
					print('Szachao...\n')
				last_card = karta(1,'5')
				if self.czy_pat(kolej):

					if not test:
						print('\nPO SZACHALE!\n{} wygrał grę\nRuchów: {}'.format(gr, len(self.historia)))
					self.mat = True
					return 'koniec'
			elif self.czy_pat(kolej):
				if not test:
					print('\nPAT\nRuchów: {}'.format(len(self.historia)))
				self.pat = True
				return 'koniec'



			spalona = False
			gr = self.get_gracz(kolej)
			assert gr.kol == kolej

			if not test:
				print("RUSZA SIĘ: {} ({})\n{}\n".format(gr, kolej, gr.reka))

			if czy_pion_na_koncu(self.plansza, odwrot(kolej))>0 and not rnd:
				print('Coś nie halo, bo niezamieniony pion poprzedniego gracza na końcu stoi')

# 			a = input('''jaka karte zagrywasz, którym pionkiem chcesz się ruszyć, gdzie
# [1 - Pik, 2 - Kier, 3 - Karo, 4 - Trefl]
# (siódemka pik, ruch z A2 na A3)
# np. '71 A2 A3' 
# (schodki 7,8,9 w pikach - oddziel karty przecinkiem bez spacji)
# '71,81,91 A2 A3' 

# (type e to exit)\n''').upper()



			if last_card.ran!='K' or last_card.kol != 1:
				if rnd:
					if self.szach or len(all_ruchy(self.plansza,kolej))==0:
						if karta(3,'K') in gr.reka and ok_karta([karta(3,'K')],self.kupki):
							kar = [karta(3,'K')]
						elif karta(4,'K') in gr.reka and ok_karta([karta(4,'K')],self.kupki):
							kar = [karta(4,'K')]
						else:
							rando = random.randint(0,4)
							kar = [gr.reka[rando]]
					else:
						rando = random.randint(0,4)
						kar = [gr.reka[rando]]
					if not test:
						print('karta: {}'.format(kar[0]))
				else:
					a = input('KARTA: ').upper()
					if a == 'E':
						return 'exit';
					kar = rozpakuj_input(a)


				# warunki kiedy nie można wyłożyć jakiejś karty..
				if licznik>2:
					temp = self.historia[-1][-1:][0]
					if type(temp) != str:
						temp = self.historia[-1][-2]
						# print('\nbłąd w tempie, licznik {} temp: {}\nhistoria {}'.format(licznik, temp, self.historia[-5:]))
				else:
					temp = 'nic'

				war1 = self.szach and (kar[-1].ran=='Q' or kar[-1].ran=='A')
				war2 = (kar[-1].ran=='K' and kar[-1].kol==1) and (last_card.ran=='A' or licznik<3 or temp=='ominięta')
				war3 = (kar[-1].ran=='K' and kar[-1].kol==2) and (licznik<2 or temp=='ominięta')


				while(war1 or war2 or war3):
					if rnd:
						rando = random.randint(0,4)
						kar = [gr.reka[rando]]
						if not test:
							print('karta: {}'.format(kar[0]))
					else:
						if not test:
							print('Nie możesz zagrać tej karty.. !')
						a = input('KARTA: ').upper()
						if a == 'E':
							return 'exit';
						kar = rozpakuj_input(a)
					war1 = self.szach and (kar[-1].ran=='Q' or kar[-1].ran=='A')
					war2 = (kar[-1].ran=='K' and kar[-1].kol==1) and (last_card.ran=='A' or licznik<3 or temp=='ominięta')
					war3 = (kar[-1].ran=='K' and kar[-1].kol==2) and (licznik<2 or temp=='ominięta')

				
				for p in kar:
					assert p in gr.reka
				
				now_card = kar[-1] 	
				if not ok_karta(kar,self.kupki):
					assert len(kar)==1
					if not test:
						print('palę tę kartę')
					spalona = True

					gr.reka = odejmij(gr.reka, kar)
					# if ktora_kupka(kar, self.kupki) == 3:
					self.spalone.extend(kar)
					if len(self.karty.cards)<len(kar):
						if not test:
							print('przetasowuje!')
						self.przetasuj()
					tas = self.karty.deal(len(kar))
					gr.reka.extend(tas)


				else:
					if self.szach:
						assert kar[-1].ran!='A'

					gr.reka = odejmij(gr.reka, kar)
					self.kupki[ktora_kupka(kar, self.kupki, rnd)].extend(kar)
					
					if len(self.karty.cards)<len(kar):
						if not test:
							print('przetasowuje!')
						self.przetasuj()
					tas = self.karty.deal(len(kar))
					gr.reka.extend(tas)

				assert len(gr.reka)==5

				# if len(self.karty.cards)<len(kar):
				# 		pass #przetasowanie talii

				if not spalona:
					# AS
					if kar[-1].ran == 'A':
						self.historia.append([gr]+kar+last_move)
						for g in self.gracze:
							g.kol = odwrot(g.kol)
						last_card = kar[-1]
						continue
					# WALET
					if kar[-1].ran == 'J' and jaki_typ_zostal(self.plansza, odwrot(kolej))!={'krol'}:
						waltym = 'pies'
						licz = 0
						while(waltym not in jaki_typ_zostal(self.plansza, odwrot(kolej))):
							licz += 1
							if licz > 1000:
								print(licz)
								print(waltym)
							if rnd:
								c = random.choice(['p', 'w', 's', 'g', 'd'])
							else:
								c = input('Ruchu jaką figurą żądasz?\nP W S G D ?\n').lower()
							waltym = nawaleta(c)

						assert waltym != False
						assert waltym in jaki_typ_zostal(self.plansza, odwrot(kolej))
						walet = nawaleta(c)
						
					if kar[-1].ran == '3':
						trojka = 3
					if kar[-1].ran == '4':
						czworka == True
						ok_zbicie = False
					if kar[-1].ran == 'K' and kar[-1].kol==1:
						assert licznik > 2
						# tu jeszcze nie działa bo losowo można zagrać króla pik za wcześnie
						kpik = self.historia[-1][-2:]
						self.historia.append([gr]+kar)
						last_card = kar[-1]
						self.cofnij(odwrot(kolej))
						kolej = odwrot(kolej)
						continue
					if kar[-1].ran == 'K' and kar[-1].kol==2:
						assert licznik>1
						kkier = self.historia[-1][-1]
						assert type(kkier)==str


			### RUCH

			# tu jest jeszcze bug ze krolowka moze na damie sie ruszac do woli..
			self.zamiana = False
			if last_card.ran=='K' and last_card.kol == 1:
				if self.historia[-2][-4] != 'spalona':
					now_card = self.historia[-2][-3]
				else:
					spalona = True

			# zbieram wszystkie dozwolone ruchy
			if not spalona:
				ruchy = all_ruchy(self.plansza,kolej,ok_zbicie,now_card)
			else:
				ruchy = all_ruchy(self.plansza,kolej,ok_zbicie)

			# warunki dla krola pik
			if last_card.ran=='K' and last_card.kol == 1:
				ruchy = {k:v for (k,v) in ruchy.items() if k==kpik[0]}
				if kpik[1] in ruchy[kpik[0]]:
					ruchy[kpik[0]].remove(kpik[1])
				if len(ruchy[kpik[0]])==0:

					if not test:
						print('nie mam ruchu!!! KPIK')
					self.historia.append([gr, 'ominięta'])
					last_card = karta(1,'5')
					kolej = odwrot(kolej)
					continue

			# warunki dla krola kier
			if last_card.ran=='K' and last_card.kol == 2:
				if kkier not in ruchy.keys():
					if not test:
						print('bierka zbita, tracisz kolejke, KKIER')
					self.historia.append([gr, 'ominięta']+kar)
					last_card = now_card
					kolej = odwrot(kolej)
					continue
				ruchy = {k:v for (k,v) in ruchy.items() if k==kkier}
				# ruchy[kkier[0]].remove(kkier[1])
				if len(ruchy[kkier])==0:
					if not test:
						print('nie mam ruchu!!! KKIER')
					self.historia.append([gr, 'ominięta']+kar)
					last_card = now_card
					kolej = odwrot(kolej)
					continue

			#warunki dla waleta
			if last_card.ran=='J' and (now_card.ran != 'J' or spalona):
				ruchy = {k:v for (k,v) in ruchy.items() if self.plansza.brd[self.plansza.mapdict[k]].name==walet}
				if last_card.ran=='J' and now_card.ran == 'Q' and walet=='dama' and not spalona:
					# print('walet')
					pass
				if len(ruchy)==0:
					if not test:
						print('nie możesz się ruszyć, tracisz kolejke, WALET')
					self.historia.append([gr, 'ominięta']+kar)
					last_card = now_card
					kolej = odwrot(kolej)
					continue

			# warunki dla 4
			# if czworka:
			# if now_card.ran=='4':
			# 		ok_zbicie = False
			if last_card.ran=='4' and (now_card.ran != '4' or spalona):
					self.historia.append([gr, 'ominięta']+kar)
					last_card = now_card
					kolej = odwrot(kolej)
					ok_zbicie = False
					continue

			# if not ok_zbicie:




			if not test:
				print('możliwe ruchy:\n{}'.format(ruchy))


			## zaczyna się właściwy ruch	
			if rnd:
				random_ruch = random.choice(list(ruchy.keys()))

				random_nr = random.randint(0,len(ruchy[random_ruch])-1)
				z = [random_ruch, ruchy[random_ruch][random_nr]]
				if not test:
					print('ruch: {}'.format(z))
			else:
				b = input('RUCH: ').upper()
				if b == 'E':
					return 'exit'
				z = rozpakuj_input(b)

				while(not self.plansza.rusz(z[0],z[1],now_card, only_bool=True) or self.plansza.brd[self.plansza.mapdict[z[0]]].kolor != kolej):
					if len(z)==1:
						if not test:
							print('wpisz drugą pozycję!')
						continue
					if z[0] not in ruchy.keys() or z[1] not in ruchy[z[0]]:
						print('\nwybranego ruchu nie ma w ruchach')
						continue
					if not test:
						print('Ruch nie dozwolony! Wybierz inny...')
					b = input('RUCH: ').upper()
					if b == 'E':
						return 'exit'
					z = rozpakuj_input(b)

			assert len(z)==2
				# for p in z[0]:
				# 	assert p in gr.reka
			assert z[1] in self.plansza.mapdict
			assert z[0] in self.plansza.mapdict

			if last_card.ran=='K' and last_card.kol == 1:
				assert z[0] == kpik[0]
				assert z[1] != kpik[1]

			if last_card.ran=='K' and last_card.kol == 2:
				assert z[0] == kkier

			if last_card.ran=='J' and now_card.ran != 'J' and not spalona:
				self.plansza.brd[self.plansza.mapdict[z[0]]].name==walet
			
			## CZYSZCZENIA
			# czyszczenie waleta, może nie warto?
			walet = False
			ok_zbicie = True

			if not spalona:
				ruch = self.plansza.rusz(z[0],z[1],now_card)
			else:
				ruch = self.plansza.rusz(z[0],z[1])

			if ruch:
				if self.czy_szach(kolej):
					print('SZACH PO MOIM RUCHU, KOŃCZĘ PRACĘ')
					self.mat=True
					break
				zam = czy_pion_na_koncu(self.plansza, kolej)
				if zam>0:
					self.zamiana = True
					if rnd:
						q = random.choice(['D','G','S','W'])
					else:
						q = input('Na jaką figurę chcesz zamienić piona?\nD - Dama\nG - Goniec\nS - Skoczek\nW - Wieża\n').upper()
					
					if q == 'E':
						return 'exit'
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


				# po ruchu, dopisuje hisorie i zamieniam switche

				if spalona:
					self.historia.append([gr,'spalona']+[now_card]+z)
					last_card = karta(1,'5')
				else:
					self.historia.append([gr]+[now_card]+z)
					last_card = now_card
				
				last_move = z
				kolej = odwrot(kolej)
			
			else:
				print('\n!!! ruch nie dozwolony !!!\n\n')
				print('''Plansza:
					{}
					last_card: {}
					now_card: {}
					ruch: {}
					{}{}{}
					'''.format(self, last_card, now_card, z, last_move, kkier, kpik) )
				print(self.historia[-5:])
				# break

			if rnd and not test:
				time.sleep(2)


		assert self.mat != self.pat
		return 'koniec'

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

	def cofnij(self, kolor):
		assert len(self.historia)>1
		assert self.historia[-1][-1]==karta(1,'K')
		# tu problem w przypadku omijania kolejki
		ruch = self.historia[-2][-2:]
		# assert 
		a = self.plansza.mapdict[ruch[0]]
		b = self.plansza.mapdict[ruch[1]]
		if self.zamiana:
			self.plansza.brd[b] = pionek(kolor,b)
		if self.plansza.bicie:
			assert self.plansza.is_empty(a)
			rezurekt = self.plansza.zbite.pop()
			self.plansza.brd[a] = rezurekt
			self.plansza.swap(a,b)
		else:
			self.plansza.swap(a,b)

	def przetasuj(self):
		kup_1=self.kupki[0][-1]
		kup_2=self.kupki[1][-1]
		do_tasu = self.kupki[0][:-1] + self.kupki[1][:-1] + self.spalone
		out = talia(do_tasu)
		self.spalone = []
		assert len(out.cards) < 94
		talia(do_tasu).tasuj()
		out.combine(self.karty.cards)
		self.karty = out
		self.kupki=([kup_1], [kup_2])




#### bugi

# co kiedy król zagrywa specjalnego króla i ma w zasięgu króla przeciwnego?
# - dokleiłem jeszcze w dozwolonym damki warunek na typ ktory zostal
# król się zbija w pewnym momencie (jakim?)
# - dokleilem w all_ruchy by wywalal pozycje krola
# kkier unhashable type karta
#  problem w tempie, zmienilem troche na glupa, zeby bral dobre miejsce jak widzie ze cos zle ale olewam to dla k pika.
# co kiedy zagrywam waleta, żądam ruchu damą, którą następnie zbijam?
# robię tak, że tracisz kolejkę.


#####
# fajny licznik
# values = range(0, 100)
# for i in values:
# 	time.sleep(0.1)
# 	print ("\rComplete: ", i, "%", end="")
# print ("\rComplete: 100% ")