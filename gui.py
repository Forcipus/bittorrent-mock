import sys
import subprocess
import os
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QLabel, QVBoxLayout, QProgressBar
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import re

class TorrentDownloader(QWidget):
    def __init__(self):
        super().__init__()

        # UI elemanlarını başlat
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Torrent Downloader')
        self.setGeometry(100, 100, 400, 350)  # Pencere boyutunu ayarla
        self.setStyleSheet("background-color: #f0f0f0;")  # Arkaplan rengi

        # Font ayarı
        font = QFont('Arial', 12)
        
        # Etiketler ve butonlar
        self.status_label = QLabel('Durum: Hazır', self)
        self.status_label.setFont(font)
        self.status_label.setAlignment(Qt.AlignCenter)

        self.download_button = QPushButton('Torrent Dosyasını Seç ve İndir', self)
        self.download_button.setFont(font)
        self.download_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px;")
        self.download_button.clicked.connect(self.select_file_and_download)

        self.speed_label = QLabel('İndirme Hızı: 0 kbit/s', self)
        self.speed_label.setFont(font)
        self.speed_label.setAlignment(Qt.AlignCenter)

        # Yükleme çubuğu
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)  # 0 ile 100 arasında
        self.progress_bar.setValue(0)  # Başlangıçta 0
        self.progress_bar.setTextVisible(True)

        # Layout düzeni (dikey ve yatay düzenleme)
        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.download_button)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.speed_label)

        self.setLayout(layout)

    def select_file_and_download(self):
        # Kullanıcıdan torrent dosyasını seçmesini isteyin
        file_path, _ = QFileDialog.getOpenFileName(self, 'Torrent Dosyasını Seç', '', 'Torrent Files (*.torrent)')

        if file_path:
            # Seçilen torrent dosyasını indirmeye başla
            self.status_label.setText('Durum: İndiriliyor...')
            self.progress_bar.setValue(0)  # İndirme başladığında çubuğu sıfırla
            self.download_torrent(file_path)

    def download_torrent(self, file_path):
        """Bir torrent dosyasını aria2c kullanarak indirir."""
        download_dir = './downloads'
        os.makedirs(download_dir, exist_ok=True)

        # aria2c komutunu hazırlayın
        command = [
            'aria2c', 
            '--dir', download_dir, 
            '--continue=true', 
            '--force-sequential=true', 
            '--bt-enable-lpd=false',  # Local Peer Discovery (LPD) kapalı
            '--bt-require-crypto=false',  # Kriptografik bağlantı gereksiz
            '--listen-port=6882',  # TCP bağlantı portu
            '--max-connection-per-server=4',  # Sunucu başına maksimum bağlantı
            '--seed-time=0',  # Seed zamanı 0, daha hızlı indir
            file_path        
            ]

        # Komutu subprocess ile çalıştırın
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # İndirilen dosyanın çıktısını ekrana yazdırın
        for line in process.stdout:
            line = line.decode('utf-8')
            print(line)

            # İlerlemeyi al ve yükleme çubuğunu güncelle
            if "percent" in line:
                percent = self.extract_percentage(line)
                if percent is not None:
                    self.progress_bar.setValue(percent)

            # İndirme hızını al ve hız etiketini güncelle
            speed = self.extract_speed(line)
            if speed is not None:
                self.speed_label.setText(f'İndirme Hızı: {speed} kbit/s')

        # Hata mesajlarını da ekrana yazdırın
        for line in process.stderr:
            line = line.decode('utf-8')
            print(f"Error: {line}")

        # İndirme tamamlandığında durumu güncelleyin
        self.status_label.setText('Durum: İndirme Tamamlandı')

    def extract_percentage(self, line):
        """aria2c çıktısından indirme yüzdesini çıkarır."""
        match = re.search(r'(\d+)%', line)
        if match:
            return int(match.group(1))
        return None

    def extract_speed(self, line):
        """aria2c çıktısından indirme hızını çıkarır (kbit/s olarak)."""
        match = re.search(r'(\d+\.\d+|\d+) kB/s', line)
        if match:
            speed_kbit = float(match.group(1)) * 8  # kB/s to kbit/s
            return round(speed_kbit)
        return None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TorrentDownloader()
    ex.show()
    sys.exit(app.exec_())