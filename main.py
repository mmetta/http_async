import os
import sys
from pathlib import Path

from PySide6.QtCore import QCoreApplication, QProcess
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow, QApplication

import qdarktheme

from atual_path import local_path
from consult_view import ConsultView
from sqlite_data import create_db, select_all, update_data

appData = os.getenv('APPDATA') + '\\BinanceAsync'
db_dir = os.path.isdir(appData)
if not db_dir:
    os.makedirs(os.path.join(os.environ['APPDATA'], 'BinanceAsync'))
    create_db()


class MainWin(QMainWindow):
    def __init__(self):
        super().__init__()
        path = Path(local_path())
        self.config = select_all()
        self.setWindowTitle('Binance Async')
        self.setWindowIcon(QIcon(f'{path}/icons/bit_icon.png'))
        self.setFixedSize(620, 500)
        self.consult_view = ConsultView()
        self.theme_change()
        self.setCentralWidget(self.consult_view)

        self.consult_view.ev_theme.connect(self.theme_change)
        self.consult_view.ev_color.connect(self.restart_app)

    @staticmethod
    def restart_app():
        QCoreApplication.quit()
        QProcess.startDetached(sys.executable, sys.argv)

    def theme_change(self):
        txt = self.consult_view.btn_dark.text()
        color = self.config['color_primary']
        if txt == 'dark':
            self.consult_view.btn_dark.setText('light')
            qdarktheme.setup_theme('dark', custom_colors={'primary': color})
            self.config['theme'] = 'light'
            update_data(self.config)
        else:
            self.consult_view.btn_dark.setText('dark')
            qdarktheme.setup_theme('light', custom_colors={'primary': color})
            self.config['theme'] = 'dark'
            update_data(self.config)


if __name__ == '__main__':
    app = QApplication([])
    window = MainWin()
    window.show()
    app.exec()
