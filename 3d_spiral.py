import sys
from PyQt5 import QtCore, QtWidgets
import numpy as np
import pyqtgraph.opengl as gl
import pyqtgraph as pg
from mainwindow import Ui_MainWindow

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.doubleSpinBox = {
            'n'    :{'l':self.ui.doubleSpinBox_n_l, 'u':self.ui.doubleSpinBox_n_u, 'v':self.ui.doubleSpinBox_n_v},
            'r'    :{'l':self.ui.doubleSpinBox_r_l, 'u':self.ui.doubleSpinBox_r_u, 'v':self.ui.doubleSpinBox_r_v},
            'h'    :{'l':self.ui.doubleSpinBox_h_l, 'u':self.ui.doubleSpinBox_h_u, 'v':self.ui.doubleSpinBox_h_v},
            'plots':{'l':self.ui.doubleSpinBox_plots_l, 'u':self.ui.doubleSpinBox_plots_u, 'v':self.ui.doubleSpinBox_plots_v},
            'rrc'  :{'l':self.ui.doubleSpinBox_rrc_l, 'u':self.ui.doubleSpinBox_rrc_u, 'v':self.ui.doubleSpinBox_rrc_v},
        }

        self.horizontalSlider = {
            'n'    :self.ui.horizontalSlider_n,
            'r'    :self.ui.horizontalSlider_r,
            'h'    :self.ui.horizontalSlider_h,
            'plots':self.ui.horizontalSlider_plots,
            'rrc'  :self.ui.horizontalSlider_rrc,
        }

        self.ui.graphicsView.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.ui.graphicsView.opts['distance'] = 60
        self.g = gl.GLGridItem()
        self.ui.graphicsView.addItem(self.g)
        
        pg.setConfigOption('foreground', 'k')
        pg.setConfigOption('background', 'w')

        self.setParameter()

        # doubleSpinBoxイベント
        for key1 in self.doubleSpinBox:
            for key2 in self.doubleSpinBox[key1]:
                self.doubleSpinBox[key1][key2].valueChanged.connect( self.doubleSpinBoxChanged )
        
        # horizontalSliderイベント
        for key in self.horizontalSlider:
            self.horizontalSlider[key].valueChanged.connect(self.horizontalSliderMoved)

    def horizontalSliderMoved(self):
        def key(horizontalSlider_):
            for key1 in self.horizontalSlider:
                if self.horizontalSlider[key1] is horizontalSlider_:
                    return key1
        horizontalSlider = self.sender()
        key_ = key(horizontalSlider)
        value = horizontalSlider.value()/100*self.doubleSpinBox[key_]['u'].value()
        self.doubleSpinBox[key_]['v'].setValue( value )

    def doubleSpinBoxChanged(self, value):

        def keys(doubleSpinBox_):
            for key1 in self.doubleSpinBox:
                for key2 in self.doubleSpinBox[key1]:
                    if self.doubleSpinBox[key1][key2] is doubleSpinBox_:
                        return key1, key2
        
        doubleSpinBox = self.sender()
        key1, key2 = keys(doubleSpinBox)
        
        # プロット更新
        if key2 == 'v':
            self.setParameter()
            self.horizontalSlider[key1].setValue( doubleSpinBox.value() )
            return

        # スライドバー更新
        if key2 == 'u':
            self.horizontalSlider[key1].setMaximum( doubleSpinBox.value() )
            return
        
        if key2 == 'l':
            self.horizontalSlider[key1].setMinimum( doubleSpinBox.value() )
            return

    def setParameter(self):
        n = self.doubleSpinBox['n']['v'].value()
        r = self.doubleSpinBox['r']['v'].value()
        h = self.doubleSpinBox['h']['v'].value()
        plots = self.doubleSpinBox['plots']['v'].value()
        rrc = self.doubleSpinBox['rrc']['v'].value()

        theta = np.linspace(-n * np.pi, n * np.pi, int(plots))
        Z = np.linspace(0, h, int(plots))
        R = r + (Z/h-0.5)**2*(4*rrc*r)
        X = R * np.sin(theta)
        Y = R * np.cos(theta)
        
        length = 0
        for i in range(len(X)-1):
            length += ( (X[i]-X[i+1])**2 + (Y[i]-Y[i+1])**2 + (Z[i]-Z[i+1])**2 )**0.5

        self.doubleSpinBox['l']['v'].setValue(length)

        pos = np.array([[x, y, z] for x, y, z in zip(X, Y, Z) ])
        self.scttrPlt = gl.GLScatterPlotItem(pos=pos, size=0.1, color=(1,1,1,1), pxMode=False)
        self.scttrPlt.translate(5,5,0)
        self.graphicsViewItemsClear()
        self.ui.graphicsView.addItem(self.scttrPlt)

    def graphicsViewItemsClear(self):
        for item in self.ui.graphicsView.items:
            item._setView(None)
        self.ui.graphicsView.items = []
        self.ui.graphicsView.update()     


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
    
if __name__ == '__main__':
    main()