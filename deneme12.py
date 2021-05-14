import sys
import uuid, re  # ip adresi ve mac adresi bulmak için gerekli modül
from PyQt5 import QtWidgets  # PyQt5 modülü
from PyQt5.QtChart import QChartView, QChart, QPieSeries  # pasta grafik oluşturmak için gerekli modül
from PyQt5.QtCore import QTimer  # timer modülü
import psutil
from pynvml import *  # ekran kartı bulmak için gerekli modül
import subprocess  # wifi ağları bulmak için gerekli modül
import platform, socket, psutil, logging  # Sistem bilgileri
from PyQt5.QtWidgets import QLabel  # label modülü
from tkinter import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
import sys
import tkinter as tk
import PySimpleGUI as sg


# import PySimpleGUIQt as sg
# set window color
def getSystemInfo():
    try:
        nvmlInit()
        info = {}  # boş sözlük oluşturduk

        info['İşletim sistemi'] = platform.system()
        info['platform-release'] = platform.release()
        info['platform-version'] = platform.version()
        info['architecture'] = platform.machine()
        info['bilgisayar adı'] = socket.gethostname()
        info['ip-address'] = socket.gethostbyname(socket.gethostname())
        info['mac-address'] = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
        info['İşlemci bilgileri'] = platform.processor()
        info['RAM'] = str(round(psutil.virtual_memory().total / (1024.0 ** 3))) + " GB"
        hdd = psutil.disk_usage('/')
        info['hard-drive total'] = str(hdd.total / (2 ** 30))
        info['hard-drive used'] = str(hdd.used / (2 ** 30))
        info['hard-drive free'] = str(hdd.free / (2 ** 30))
        handle = nvmlDeviceGetHandleByIndex(0)
        info['Ekran Kartı'] = str(nvmlDeviceGetName(handle))
        """
        meta_data = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles'])
        data = meta_data.decode('utf-8', errors="backslashreplace")
        data = data.split('\n')
        names = []
        for i in data:
            if "All User Profile" in i:
                i = i.split(":")
                i = i[1]
                i = i[1:-1]
                names.append(i)
        info['Wi-Fi Ağı'] = names[0]
        """
        return info  # oluşturduğumuz sözlüğümüzü döndük
    except Exception as e:
        logging.exception(e)


# Pencere sınıfı
class Pencere(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.timer = QTimer()  # timer nesnesi oluşturduk
        self.init_ui()
        self.w = Pencere2()

    def init_ui(self):  # window(ekranın özellikleri oluyor burada)
        timerDegeri = 1000
        self.ozellikler = getSystemInfo()
        self.timer.start(timerDegeri)  # timer çalıştırdık

        # boş pasta grafiklerimizi oluşturduk
        self.PastaGrafik_islemci = QPieSeries()
        self.PastaGrafik_ram = QPieSeries()
        self.PastaGrafik_hdd = QPieSeries()

        self.timer.timeout.connect(self.Loop)  # her saniye click adlı metodu çağırır

        # Chartları oluşturduk
        chart = QChart()
        chart.legend().hide()
        chart.addSeries(self.PastaGrafik_islemci)
        chart.createDefaultAxes()
        chart.setTitle("CPU Kullanımı")  # Chart isimleri verdik
        chartview = QChartView(chart)
        chart.setOpacity(0.7)
        chart.setTheme(QChart.ChartThemeDark)

        chart2 = QChart()
        chart2.legend().hide()
        chart2.addSeries(self.PastaGrafik_ram)
        chart2.createDefaultAxes()
        chart2.setTitle("RAM Kullanımı")
        chartview2 = QChartView(chart2)
        chart2.setOpacity(0.7)
        chart2.setTheme(QChart.ChartThemeDark)

        chart3 = QChart()
        chart3.legend().hide()
        chart3.addSeries(self.PastaGrafik_hdd)
        chart3.createDefaultAxes()
        chart3.setTitle("Hard Disk Kullanımı")
        chartview3 = QChartView(chart3)
        chart3.setOpacity(0.7)
        chart3.setTheme(QChart.ChartThemeDark)

        # Düzenli bir görünüm için v_box oluşturduk. Grafikleri Vbox'a koyduk
        # Bu sayede grafikler alt alta göründü.
        v_box = QtWidgets.QVBoxLayout()
        v_box.addWidget(chartview)
        v_box.addWidget(chartview2)
        v_box.addWidget(chartview3)

        h_box = QtWidgets.QHBoxLayout()  # h box oluşturup grafiklerin bulunduğu v boxı oluşturduğumuz h boxa koyduk
        h_box.addLayout(v_box)

        v_box2 = QtWidgets.QVBoxLayout()  # Sistem bilgilerinin yazılacağı labeller için ikinci bir vbox oluşturduk

        h_box.addLayout(v_box2)  # 2. vbox'ımızı hbox'ımıza koyduk


        # Pencereye Hbox layoutumuzu atadık
        self.setLayout(h_box)

        self.setStyleSheet("background-color: black;")

        # Pencere boyut ayarlaması ve gösterilmesi
        self.setGeometry(800, 100, 500, 500)

        # this will hide the title bar
        self.setWindowFlag(Qt.FramelessWindowHint)
        # creating a label widget
        # show all the widgets

        self.show()

    def Loop(self):
        # Grafiklerimizi temizledik
        self.PastaGrafik_ram.clear()
        self.PastaGrafik_islemci.clear()
        self.PastaGrafik_hdd.clear()

        # İşlemci kullanımı ve ram kullanımını bulduk
        self.islemci_kullanimi = psutil.cpu_percent(0)
        self.ram_kullanimi = psutil.virtual_memory()[2]

        # İşlemci kullanımını 1. grafiğimize ekledik
        self.PastaGrafik_islemci.append("işlemci Kullanımı", self.islemci_kullanimi * 3.6)
        self.PastaGrafik_islemci.append("Boşta", (100 - self.islemci_kullanimi) * 3.6)

        # Ram kullanımını 2. grafiğimize ekledik
        self.PastaGrafik_ram.append("Ram Kullanımı", self.ram_kullanimi * 3.6)
        self.PastaGrafik_ram.append("Boşta", (100 - self.ram_kullanimi) * 3.6)

        # Hard disk kullanımını 3. grafiğimize ekledik
        self.kullanilan = self.ozellikler['hard-drive used']
        self.bosta = self.ozellikler['hard-drive free']
        self.PastaGrafik_hdd.append("Kullanılan", float(self.kullanilan))
        self.PastaGrafik_hdd.append("Boşta", float(self.bosta))


class Pencere2(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.ozellikler = getSystemInfo()  # sistem bilgilerini sözlük halinde aldık

        # Düzenli bir görünüm için v_box oluşturduk. Grafikleri Vbox'a koyduk
        # Bu sayede grafikler alt alta göründü.
        v_box = QtWidgets.QVBoxLayout()

        h_box = QtWidgets.QHBoxLayout()  # h box oluşturup grafiklerin bulunduğu v boxı oluşturduğumuz h boxa koyduk
        h_box.addLayout(v_box)

        v_box = QtWidgets.QVBoxLayout()  # Sistem bilgilerinin yazılacağı labeller için ikinci bir vbox oluşturduk

        # Sistem bilgilerinin bulunduğu 'ozellikler' isimli sözlüğümüzde gezerek
        # sözlüğün key'ini ve Value'sunu labellere yazdırıp oluşturudğumuz 2. vboxa koyduk
        for key, value in self.ozellikler.items():
            label = QLabel(key + " : " + str(value))
            label.setStyleSheet("color:white")
            v_box.addWidget(label)
        h_box.addLayout(v_box)  # 2. vbox'ımızı hbox'ımıza koyduk
        self.setLayout(h_box)

        self.setStyleSheet("background-color: black;")

        # Pencere boyut ayarlaması ve gösterilmesi
        self.setGeometry(200, 100, 500, 500)

        # this will hide the title bar
        self.setWindowFlag(Qt.FramelessWindowHint)
        # creating a label widget
        # show all the widgets
        self.show()

        # Pencereye Hbox layoutumuzu atadık


# Pencere nesnesi oluşturma ve yürütme
app = QtWidgets.QApplication(sys.argv)
pencere = Pencere()
pencere.setWindowOpacity(0.7)
sys.exit(app.exec_())
# YOLO, darknet, cüda, tensorflow
