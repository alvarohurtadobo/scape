# Developed by Alvaro Hurtado
# a.hurtado.bo@gmail.com
# Oruro, Bolivia

import sys
import multiprocessing
from PyQt4 import QtGui, QtCore, QtTest
from PyQt4.phonon import Phonon
from time import sleep, strftime
try:
    from gpio import MembraneMatrix
except:
    pass

class GUIParalela():
    """
    La presente clase representa una interfaz visual de alarma Activada/Desactivada
    Su función principal es la de gestionar la activación y desactivación de la alarma.
    Al Desactivar la alarma Identifica a la persona ingresando
    Al Activar la alarma se regresa al estado inicial
    Presionar ESC para cerrar el GUI
    """
    myQueue = multiprocessing.Queue()
    try:
        miTeclado = MembraneMatrix()
    except:
        pass
    valorActual = ''

    def __init__(self,fullScreen=True):
        """
        Constructor de la clase tiene dos opciones a activar o desactivar:
        bool simulation = Falso por defecto, corre una simulación de la activación y desactivación de la alarma por un minuto con datos simulados en forma de variable de clase
        bool fullScreen = True por defecto, corre la GUI en modo de pantalla total, lo que se espera en su funcionamiento normal
        """
        self.process = multiprocessing.Process(target=self._correrGui,args=(fullScreen,))
        self.process.start()
        

    def _correrGui(self,fullScreen):
        """
        Metodo auxiliar para paralelizar la interfaz
        """
        app = QtGui.QApplication(sys.argv)
        interfaz = InterfazVideo(GUIParalela.myQueue,pantallaTotal=fullScreen)
        sys.exit(app.exec_())

class PopUp(QtGui.QWidget):         #QWidget #QMainWindow
    """
    Pop up
    """

    def __init__(self):
        #super(InterfazPreguntas, self).__init__(parent)
        QtGui.QWidget.__init__(self, None, QtCore.Qt.WindowStaysOnTopHint)
        # Parámetros constantes:
        self.titulo = 'Revisando'
        self.etiqueta = QtGui.QLabel('Correcta')
        self.imagen = QtGui.QLabel(self)
        self.imagenCorrecta = QtGui.QPixmap('./imagenes/pensando.png')

        self.miLayout = QtGui.QVBoxLayout()
        self.miLayout.addWidget(self.imagen)
        self.miLayout.addWidget(self.etiqueta)
        self.miLayout.setAlignment(self.etiqueta, QtCore.Qt.AlignHCenter)
        self.setLayout(self.miLayout)
        self.setWindowTitle(self.titulo)
        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),(resolution.height() / 2) - (self.frameSize().height() / 2)) 

    def showEspera(self):
        self.etiqueta.setText('Veamos .....')
        self.imagen.setPixmap(self.imagenCorrecta)
        self.show()
        QtTest.QTest.qWait(2000)
        self.hide()

class InterfazVideo(QtGui.QWidget):         #QWidget #QMainWindow
    """
    Interfaz gráfica visual
    """
    
    def __init__(self,fila,pantallaTotal = True,parent=None):
        #super(InterfazVideo, self).__init__(parent)
        QtGui.QWidget.__init__(self, None, QtCore.Qt.WindowStaysOnTopHint)
        # Parámetros constantes:
        self.titulo = 'Scape Room'
        self.thread = ThreadClass()
        self.video1 = Phonon.VideoPlayer(self)
        self.video2 = Phonon.VideoPlayer(self)
        self.thread.start()
        self.miPopUp = PopUp()
        
        self.queue = fila
        self.passwords = []
        with open('./database/key', 'r') as f:
            readData = f.read()
        for password in readData.split('\n'):
            if len(password)>4:
                self.passwords.append(password) 
        # Clases auxiliares: 
        self.initUI()
        self.connect(self.thread,QtCore.SIGNAL('REVISAR'),self.revisarRespuesta)
        self.connect(self.video1,QtCore.SIGNAL("finished()"),self._terminoVideo)
        self.connect(self.video2,QtCore.SIGNAL("finished()"),self._terminoVideo)
        self.connect(self.thread,QtCore.SIGNAL("ACTUALIZAR"),self.actualizarTexto)
        self.intro.returnPressed.connect(self.revisarRespuesta)
        #self.intro.editingFinished.connect(self.revisarRespuesta) # Introduce ruido al final
        
        # Al inicializarse la clase se muestra:
        if pantallaTotal:
            self.showFullScreen()
        else:
            self.show()
        #self.displayOverlay()


    def initUI(self):
        """
        Inicialización de sus parámetros
        """
        # Parte visual
        self.imagen = QtGui.QLabel(self)

        self.pixmapAct = QtGui.QPixmap('./imagenes/logoWeb.png')
        self.imagen.setPixmap(self.pixmapAct)

        self.media1 = Phonon.MediaSource('./videos/1.avi')
        self.media2 = Phonon.MediaSource('./videos/2.avi')

        self.video1.load(self.media1)
        self.video2.load(self.media2)

        # Layouts:
        self.layoutVideo1 = QtGui.QVBoxLayout()

        self.layoutVideo1.addWidget(self.imagen)
        self.layoutVideo1.addWidget(self.video1)
        self.layoutVideo1.addWidget(self.video2)
        
        self.layoutVideo1.setAlignment(self.imagen, QtCore.Qt.AlignHCenter)
        
        self.video1.setHidden(True)
        self.video2.setHidden(True)
        self.dataIntroLayout = QtGui.QHBoxLayout()
        self.passwd = QtGui.QLabel('Ingrese respuesta')
        self.passwd.setFont(QtGui.QFont('SansSerif', 36))
        self.intro = QtGui.QLineEdit()
        self.intro.setFont(QtGui.QFont('SansSerif', 36))
        #self.intro.setDisplayFormat("dd/MM/yyyy")
        self.intro.setInputMask("99/99/9999")
        self.dataIntroLayout.addWidget(self.passwd)
        self.dataIntroLayout.addWidget(self.intro)
        self.layoutVideo1.addLayout(self.dataIntroLayout)

        self.setLayout(self.layoutVideo1)
        
        self.setMinimumHeight(450)
        
        #self.setGeometry(300, 300, 300, 150)
        # Algunas visualizaciones:
        self.setWindowIcon(QtGui.QIcon('./imagenes/logo.png')) 
        
        self.setWindowTitle(self.titulo)
        
        
    def revisarRespuesta(self):
        textoSinSimbolo = self.intro.text().replace('/','')
        if textoSinSimbolo in self.passwords:
            print('Signal 1')
            self._mostrarVideo1()
        else:
            print('Signal 2')
            self._mostrarVideo2()
        self.borrarTexto()

    def borrarTexto(self):
        GUIParalela.valorActual = ''
        #self.intro.setText('')

    def displayOverlay(self):
        self.popup = QtGui.QDialog(self,QtCore.Qt.WindowStaysOnTopHint)
        self.popup.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        
        self.passwd = QtGui.QLabel('Contraseña')
        #self.passwd.setMinimumWidth(500)
        self.intro = QtGui.QLineEdit('')
        
        f = self.intro.font()
        f.setPointSize(27)
        self.intro.setFont(f)
        self.intro.setMinimumWidth(500)
        #self.intro.setEchoMode(QtGui.QLineEdit.Password)
        self.intro.updateGeometry()
        self.miMensaje = QtGui.QHBoxLayout()
        #self.miMensaje.addWidget(self.passwd)
        self.miMensaje.addWidget(self.intro)
        self.popup.setLayout(self.miMensaje)
        #position_x = (self.frameGeometry().width()-self.popup.frameGeometry().width())/2
        #position_y = (self.frameGeometry().height()-self.popup.frameGeometry().height())/2
        resolution = QtGui.QDesktopWidget().screenGeometry()
        position_x = (resolution.width() / 2) - (self.popup.frameGeometry().width() / 2)
        position_y = 7/8*((resolution.height()) - (self.popup.frameGeometry().height()))

        self.popup.move(position_x, position_y)
        #event.accept()
        self.popup.show() 

    def keyPressEvent(self, e):
        """
        Se redefine la interacción con el teclado para que la tecla ESC cierre el GUI
        """
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()
    
    def actualizarTexto(self):
        longitud = len(GUIParalela.valorActual)
        if longitud>=5:
            formatoFecha = GUIParalela.valorActual[0:2]+'/'+GUIParalela.valorActual[2:4]+'/'+GUIParalela.valorActual[4:]
        elif longitud>=3:
            formatoFecha = GUIParalela.valorActual[0:2]+'/'+GUIParalela.valorActual[2:]
        elif longitud>=1:
            formatoFecha = GUIParalela.valorActual[0:]
        else:
            formatoFecha = ''
        
        self.intro.setText(formatoFecha)

    def _mostrarVideo1(self):
        """
        Despliega el video 1
        """
        self.imagen.setHidden(True)
        self.video1.setHidden(False)
        self.video1.play()
        self.miPopUp.showEspera()
        
        
    def _mostrarVideo2(self):
        """
        Despliega el video 2
        """
        self.imagen.setHidden(True)
        self.video2.setHidden(False)
        self.video2.play()
        self.miPopUp.showEspera()

    def _terminoVideo(self):
        self.video1.setHidden(True)
        self.video2.setHidden(True)
        self.imagen.setHidden(False)

class ThreadClass(QtCore.QThread):
    """
    Thread para revisión continua de la fila de registros
    """
    def __init__(self,parent = None):
        """
        Constructor
        """
        super(ThreadClass,self).__init__(parent)

    def run(self):
        """
        Re implementación del método
        """
        while True:
            try:
                if not GUIParalela.miTeclado.teclas.empty():
                    valor = GUIParalela.miTeclado.teclas.get() # valor = (estado, id, nombre)
                    
                    if valor == '*':
                        self.emit(QtCore.SIGNAL('REVISAR'))
                        print('Introducido: ',GUIParalela.valorActual)

                        #self.intro.setText(GUIParalela.valorActual)
                    else:
                        if valor == '#':
                            GUIParalela.valorActual = GUIParalela.valorActual[:-1]
                        else:
                            GUIParalela.valorActual+= str(valor)
                        self.emit(QtCore.SIGNAL('ACTUALIZAR'))
                        #self.intro.setText(GUIParalela.valorActual)
            except:
                pass
                
                
if __name__ == '__main__':
    """
    Video response
    """
    pantalla = False
    for input in sys.argv:
        if input == 'Full':
            pantalla = True
    p = GUIParalela(fullScreen=pantalla)

    p.process.join() 
