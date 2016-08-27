import szachao, roz2

cases = [('8/P7/8/8/8/8/8/8',(1,'4')),('k1K5/8/8/8/8/8/8/8',(3,'K')), ('Wdg5/8/8/8/8/8/8/8',(1,'J'))]

def pos_moves(fen,card):
	c = szachao.karta(card[0],card[1])
	return roz2.rozgrywka(fenrep=fen, ovr=([c],[])).possible_moves(roz.to_move,roz.capture,roz.gracze[0].reka[0],roz.burned,roz.what_happened())


def seq_of_moves(boot, mvs):
	r = roz2.rozgrywka(fenrep=boot[0], ovr=[boot[1][0],boot[1][1]], test=True)
	print(r)
	for card,move in mvs:
		c = r.get_card(ovr=card)
		m = r.get_move(ovr=move)
		r.move(r.now_card,m)
	return r

k = roz2.karta_z_str
roz = seq_of_moves(('Wdg5/8/8/8/8/8/8/8',[[k('J1'),k('Q1'),k('51'),k('61'),k('81')],[k('101'),k('Q2'),k('52'),k('62'),k('82')]]), (((0, [k('J1')], 'dama'), ['A1', 'B1']),))

def test1():
	''' to jest dokumentacja 
	a to jest druga linijka

	>>> test1()
	2
	>>> test1()
	2
	'''
	for frep,card in cases:
		roz = roz2.rozgrywka(fenrep=frep, ovr=([card],[]))

		posmoves = roz

