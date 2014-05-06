all:
	python simulator.py inst.txt data.txt reg.txt config.txt result.txt

clean:
	rm *.pyc
