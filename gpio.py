import time
import RPi.GPIO as GPIO
from multiprocessing import Queue
from multiprocessing import Process

class MembraneMatrix():
	teclas = Queue()
	palabraIngresada = ''
	MATRIX = [	[1,2,3,'A'],
				[4,5,6,'B'],
				[7,8,9,'C'],
				['*',0,'#','D']]
								
	ROW = [29,31,33,35]
	COL = [37,36,38,40]

	def __init__(self):
		GPIO.setmode(GPIO.BOARD)
		for j in range(4):
			GPIO.setup(MembraneMatrix.COL[j],GPIO.OUT)
			GPIO.output(MembraneMatrix.COL[j],1)
			
		for i in range(4):
			GPIO.setup(MembraneMatrix.ROW[i],GPIO.IN,pull_up_down = GPIO.PUD_UP)
		self.p = Process(target=self.loop, args=())
		self.p.start()

	def loop(self):
		try:
			while(True):
				#time.sleep(0.05)
				for j in range(4):
					GPIO.output(MembraneMatrix.COL[j],0)
					for i in range(4):
						if GPIO.input(MembraneMatrix.ROW[i]) == 0:
							#print(MembraneMatrix.MATRIX[i][j])
							MembraneMatrix.teclas.put(MembraneMatrix.MATRIX[i][j])
							#print(MembraneMatrix.MATRIX[i][j])
							"""
							MembraneMatrix.palabraIngresada += MembraneMatrix.MATRIX[i][j]
							if MembraneMatrix.MATRIX[i][j] == '*':
								MembraneMatrix.teclas.put(MembraneMatrix.palabraIngresada)
								print('Ingreso: ',MembraneMatrix.palabraIngresada)
								MembraneMatrix.palabraIngresada = ''
							"""
							while(GPIO.input(MembraneMatrix.ROW[i])==0):
								pass
					GPIO.output(MembraneMatrix.COL[j],1)
		except KeyboardInterrupt:
			GPIO.cleanup()

	def __del__(self):
		GPIO.cleanup()
		self.p.join()

if __name__ == '__main__':
	miMembrana = MembraneMatrix()