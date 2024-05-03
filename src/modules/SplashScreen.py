import os 
from PyQt5.QtWidgets import QSplashScreen, QApplication
from PyQt5.uic import loadUi 
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize 
from PyQt5.QtGui import QPixmap, QMovie


class SplashScreen(QSplashScreen):
    def __init__(self):
        super(QSplashScreen, self).__init__()
        
        fileLocatioin = os.path.join('ui', 'Splashscreen.ui')
        
        loadUi(fileLocatioin, self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.centerOnScreen()

        self.setWindowOpacity(0.9)
        
        pixmap = QPixmap('assets/logo.png')
        self.logo.setPixmap(pixmap)
        self.logo.setFixedSize(pixmap.size())
        self.logo.setAlignment(Qt.AlignCenter)
         
        loadingGIF = QMovie('assets/loading.gif')
        loadingGIF.setScaledSize(QSize(100, 100))
        self.loading.setMovie(loadingGIF)
        #loadingGIF.start()
        
        self.loading.setMinimumSize(QSize(240, 240)) 
        self.loading.setMaximumSize(QSize(240, 240)) 
        #self.loading.setFixedSize(QSize(150, 150))
        self.loading.setAlignment(Qt.AlignCenter)

        loadingGIF.start()


    def centerOnScreen(self):
        # Get the available geometry of the screen
        screen_geometry = QApplication.desktop().availableGeometry()

        # Calculate the center point of the screen
        center_point = screen_geometry.center()

        # Calculate the top-left point of the splash screen
        top_left_point = center_point - self.rect().center()

        # Move the splash screen to the calculated top-left point
        self.move(top_left_point)


