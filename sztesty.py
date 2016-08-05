# Author: Tadek Teleżyński

from roz2 import *
import traceback
import os

os.system('clear')
print('-----------------')
print('SZACHAO TESTING')

li = [
[karta(1, '5'), karta(1, '6'),karta(1, '7'),karta(1, '8')],
[karta(1, '5'), karta(2, '6'),karta(1, '7'),karta(1, '8')],
[karta(1, '5'), karta(2, '5'),karta(1, '7'),karta(1, '8')],
[karta(1, '5'), karta(2, '5'),karta(2, '6'),karta(2, '7')],
[karta(1, '5'), karta(2, '5'),karta(3, '5'),karta(3, '5')],
[karta(1, '5'), karta(1, '6'),karta(1, '8'),karta(1, '9')]
]

def test(n=5, vid = False):
	t1 = time.time()
	print('Games to play: {}'.format(n))
	avr_moves = 0
	m = 0
	p = 0
	err = 0
	bad = []
	licznik = 0
	for i in range(n):
		print ("\rCALCULATING: {:.1f}% ".format((licznik/n)*100), end="")
		licznik+=1
		if licznik%2==0:
			randa = 1
		else:
			randa = 0
		roz = rozgrywka(randa)
		# while(roz.plansza.czy_szach()==2 or karta(1,'K') not in roz.gracze[1].reka):
		while(roz.plansza.czy_szach('c')==(True, 'c')):
			roz = rozgrywka(randa)

		# print('Rozgrywka nr {}'.format(licznik))
		try:
			# print(i)
			roz.graj(vid)
		except Exception as e:
			# print('\n ERROR')
			os.system('clear')
			print(roz)
			print('spalone {}'.format(roz.spalone[-4:]))
			print('{}\n'.format(roz.historia))
			print('szach: {}, zamiana {}, to_move {}, burned {}, now_card {}, jack {}, four {}, capture {}\n'.format(roz.szach, roz.zamiana, roz.to_move, roz.burned, roz.now_card, roz.jack, roz.four, roz.capture))

			traceback.print_exc()
			bad.append((e,roz))
		# except KeyError as ek:
			# print(ek)
		# print(roz.historia[-10:])
		# print(roz)
		avr_moves += len(roz.historia)
		if roz.mat:
			m += 1
			# print('')
		elif roz.pat:
			p += 1
		else:
			err += 1
	print('\r'+' '*30, end='')
	print ("\rDONE: {:.0f}%".format((licznik/n)*100))		
	print('Matów: {}, Patów: {}, Błędów: {} Średnia ilość ruchów: {:.0f}'.format(m,p,err, avr_moves/n))
	t2 = time.time()
	print('TIME: {:.2f} min'.format((t2-t1)/60))
	return bad


bad = test(10)


# VIDEO
# test(1, True)





def test_err(n):
	print('Testing -- test_err()')
	roz = rozgrywka()
	
	while(roz.plansza.czy_szach('c')==(True, 'c')):
		roz = rozgrywka()
	print('po rozgrywce')
	
	
	licznik = 0
	a = roz.graj()
	print('po pierwszej')
	number_of_games = n
	while (a == True and licznik<number_of_games):
		licznik += 1
		if licznik%2==0:
			randa = 0
		else:
			randa = 1
		print ("\rPostęp: {:.1f}%".format(licznik/number_of_games), end="")
		roz = rozgrywka(randa)
		while(roz.plansza.czy_szach('c')==(True, 'c')):
			roz = rozgrywka(randa)
		try:
			a = roz.graj()
		except Exception as e:
			traceback.print_exc()
			return (e, roz)

# test_err(200)

# prezentacja humana
# roz.graj(rnd=1)

def test_stat(n=5, m=2000):
	res2 = []
	for i in range(n):
		res = [0,0,0,0]
		for i in range(m):
			roz = rozgrywka()
			while(roz.plansza.czy_szach()==2):
				roz = rozgrywka()
			if roz.czy_szach('c')==2:
				res[3]+=1
			elif roz.czy_szach('c'):
				res[0]+=1
			elif roz.czy_szach('b'):
				res[1]+=1
			else:
				res[2]+=1
		
		# print(res)
		res2.append(res)
	return res2

# t = test_stat(50)
# t = test_stat(1000) 
def stat_avr(m=5, n=5, e=2000):
	res = []
	for i in range(m):
		t = test_stat(n,e)
		a = 0
		b = 0
		c = 0
		for r in t:
			a+=r[0]
			b+=r[1]
			c+=r[2]
		x=len(t)
		# print(a/x, b/x, c/x)
		res.append([a/x,b/x,c/x])
	z = [[row[i] for row in res] for i in range(3)]
	out = [sum(l)/len(l) for l in z]
	return out



# print(stat_avr(10))

# print('\n schodki ...')
# for l in li:
# 	print(l)
# 	print(schodki_check(l))


# Matów: 18, Patów: 111, Błędów: 21
# -1702.7965829372406




#####
# fajny licznik
# values = range(0, 100)
# for i in values:
# 	time.sleep(0.1)
# 	print ("\rComplete: ", i, "%", end="")
# print ("\rComplete: 100% ")
