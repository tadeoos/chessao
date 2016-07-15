from sz_roz import *
import traceback


print('-----------------')
print('SZACHAO TESTY')

li = [
[karta(1, '5'), karta(1, '6'),karta(1, '7'),karta(1, '8')],
[karta(1, '5'), karta(2, '6'),karta(1, '7'),karta(1, '8')],
[karta(1, '5'), karta(2, '5'),karta(1, '7'),karta(1, '8')],
[karta(1, '5'), karta(2, '5'),karta(2, '6'),karta(2, '7')],
[karta(1, '5'), karta(2, '5'),karta(3, '5'),karta(3, '5')],
[karta(1, '5'), karta(1, '6'),karta(1, '8'),karta(1, '9')]
]

def test(n, rnd = True, test = True):
	t1 = time.time()
	print('n: {}'.format(n))
	m = 0
	p = 0
	err = 0
	bad = []
	licznik = 0
	for i in range(n):
		print ("\rPostęp: {:.0f}%".format((licznik/n)*100), end="")
		licznik+=1
		roz = rozgrywka()
		# while(roz.plansza.czy_szach()==2 or karta(1,'K') not in roz.gracze[1].reka):
		while(roz.plansza.czy_szach()==2 or roz.plansza.czy_szach()==(True, 'c')):
			roz = rozgrywka()
		try:
			roz.graj(rnd, test)
		except Exception as e:
			print('\n ERROR')
			print(roz)
			print(roz.historia[-10:])
			traceback.print_exc()
			if n ==1:
				print(e)
			bad.append((e,roz))
		# except KeyError as ek:
			# print(ek)
		# print(roz.historia[-10:])
		# print(roz)
		if roz.mat:
			m += 1
		elif roz.pat:
			p += 1
		else:
			err += 1
	print ("\rPostęp: {:.1f}%".format((licznik/n)*100))		
	print('\nMatów: {}, Patów: {}, Błędów: {}'.format(m,p,err))
	t2 = time.time()
	print('czas: {:.2f} min'.format((t2-t1)/60))
	return bad

bad = test(30, True, True)




def test_err():
	roz = rozgrywka()
	
	while(roz.plansza.czy_szach()==2 or roz.plansza.czy_szach()==(True, 'c')):
		roz = rozgrywka()
	print('po rozgrywce')
	
	
	licznik = 0
	a = roz.graj(rnd=1, test=1)
	print('po pierwszej')
	while (a == 'koniec' and licznik<100):
		licznik += 1
		print ("\rPostęp: {:.0f}%".format(licznik), end="")
		roz = rozgrywka()
		while(roz.plansza.czy_szach()==2 or roz.plansza.czy_szach()==(True, 'c')):
			roz = rozgrywka()
		a = roz.graj(rnd=1, test=1)

# test_err()

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
