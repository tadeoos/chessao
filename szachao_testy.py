import coverage, doctest





if __name__ == "__main__":
	cov = coverage.coverage(branch=True)
	cov.erase()
	cov.start()
	import testy2
	import roz2,szachao
	doctest.testmod(testy2)
	cov.stop()
	modules=[szachao,roz2]
	cov.report(modules, ignore_errors=1, show_missing=1)
	cov.html_report(morfs=modules, directory='/tmp')
	cov.erase()

# jakie testy? 
# 1. Czy dane pole NIE jest w możliwym zakresie
# 2. Czy dane pole JEST w możliwym zakresie
# 3. Czy dana figura JEST/NIE MA w możliwym zakresie...
# Pustość ruchu