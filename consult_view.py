from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QListWidget, QListWidgetItem, QVBoxLayout, QPushButton, \
    QColorDialog

from atual_path import local_path
# from binance_api import BinanceAPI
from binance_trio import BinanceTrio
from dialog_config import CustomDialog
from icon_color import cor_icon
from sqlite_data import select_all, update_data


class CustomWidget(QWidget):
    def __init__(self, par, theme, parent=None):
        super().__init__(parent)
        self.label1 = QLabel(par['symbol'])
        self.label1.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.label1.setFont(QFont('Arial', 14, 700))
        self.label1.setStyleSheet('background: transparent;')
        cor_g = '#0f0' if theme == 'light' else '#0c0'
        cor = cor_g if float(par['priceChangePercent']) > 0 else 'red'
        # cor = '#55ff00' if float(par['priceChangePercent']) > 0 else '#ff5500'
        self.label2 = QLabel(par['bidPrice'])
        self.label2.setAlignment(Qt.AlignRight)
        self.label2.setStyleSheet(f'background: transparent; color: {cor}; font-size: 14pt;')
        self.label3 = QLabel(f"{par['priceChangePercent']}%")
        self.label3.setAlignment(Qt.AlignRight)
        self.label3.setStyleSheet(f'background: transparent; color: {cor}; font-size: 14pt;')

        layout = QHBoxLayout()
        layout.addWidget(self.label1)
        layout.addWidget(self.label2)
        layout.addWidget(self.label3)

        self.setLayout(layout)


class ConsultView(QWidget):
    ev_theme = Signal()
    ev_color = Signal()

    def __init__(self):
        super().__init__()

        path = Path(local_path())
        self.config = select_all()
        v_lay = QVBoxLayout(self)
        self.list_widget = QListWidget()
        h_lay = QHBoxLayout()

        self.lbl_time = QLabel()
        self.lbl_time.setFont(QFont('Arial', 9, 600))
        self.lbl_time.setAlignment(Qt.AlignCenter)

        ico_time = cor_icon(f'{path}/icons/timer.svg')
        self.btn_time = QPushButton('STOP')
        self.btn_time.setIcon(ico_time)
        self.btn_time.setFont(QFont('Arial', 9, 600))
        self.btn_time.setFixedWidth(100)
        self.btn_time.setStyleSheet('background: transparent; border: 0; color: red;')
        self.btn_time.clicked.connect(self.btn_clicked)

        ico_update = cor_icon(f'{path}/icons/update.svg')
        self.btn_update = QPushButton('Atualizar')
        self.btn_update.setIcon(ico_update)
        self.btn_update.setFont(QFont('Arial', 9, 600))
        self.btn_update.setFixedWidth(100)
        self.btn_update.setStyleSheet('border-radius: 0; border-right: 8 solid #888;')
        self.btn_update.clicked.connect(self.upd_clicked)
        self.btn_update.setDisabled(True)

        ico_all = cor_icon(f'{path}/icons/cog.svg')
        self.btn_all = QPushButton('Config')
        self.btn_all.setIcon(ico_all)
        self.btn_all.setFont(QFont('Arial', 9, 600))
        self.btn_all.setFixedWidth(100)
        self.btn_all.setStyleSheet('border-radius: 0; border-right: 8 solid #888;')
        self.btn_all.clicked.connect(self.all_clicked)

        txt = 'dark' if self.config['theme'] == 'light' else 'light'
        self.btn_dark = QPushButton(txt)
        self.btn_dark.setFont(QFont('Arial', 9, 600))
        self.btn_dark.setFixedWidth(100)
        self.btn_dark.setStyleSheet('border-radius: 0; border-right: 8 solid #888;')
        self.btn_dark.clicked.connect(lambda: self.dark_clicked(path))

        self.btn_color = QPushButton()
        self.btn_color.setFixedWidth(20)
        self.btn_color.clicked.connect(self.color_change)
        self.btn_color.setStyleSheet(f'background: {self.config["color_primary"]}; border: 0;')

        h_wallet = QHBoxLayout()
        self.lbl_wallet = QLabel()
        self.lbl_wallet.setFont(QFont('Arial', 10, 600))
        self.lbl_wallet.setAlignment(Qt.AlignCenter)
        h_wallet.addWidget(self.lbl_wallet)

        h_lay.addWidget(self.lbl_time)
        h_lay.addWidget(self.btn_time)
        h_lay.addWidget(self.btn_update)
        h_lay.addWidget(self.btn_all)
        h_lay.addWidget(self.btn_dark)
        h_lay.addWidget(self.btn_color)

        v_lay.addWidget(self.list_widget)
        v_lay.addLayout(h_wallet)
        v_lay.addLayout(h_lay)

        self.consult()
        self.timer = QTimer()
        self.timer.timeout.connect(self.consult)
        self.timer.start(10000)

    def color_change(self):
        cor = self.config['color_primary']
        color_dialog = QColorDialog()
        color = color_dialog.getColor(cor)
        if color.isValid():
            self.config['color_primary'] = color.name()
            self.upd_sqlite()
            self.btn_color.setStyleSheet(f'background: {color.name()}; border: 0;')
            self.ev_color.emit()

    def upd_sqlite(self):
        update_data(self.config)
        self.config = select_all()

    def consult(self):
        # start_time = time.time()
        self.list_widget.clear()
        symbols = self.config['my_list']
        # api = BinanceAPI(symbols)
        api = BinanceTrio(symbols)
        # res = consult_all()
        btc_usd = None
        btc_brl = None
        wallet = float(self.config['wallet'])

        for par in api.res:
            # print(item['symbol'], item['bidPrice'], item['priceChangePercent'])
            # print(item)
            # text = f"{item['symbol']}\t {float(item['bidPrice']):.4f}\t {item['priceChangePercent']}"

            if par['symbol'] == 'BTCBUSD':
                btc_usd = float(par['bidPrice'])
            if par['symbol'] == 'BTCBRL':
                btc_brl = float(par['bidPrice'])
            theme = self.btn_dark.text()
            item = QListWidgetItem()
            custom_widget = CustomWidget(par, theme)
            item.setSizeHint(custom_widget.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, custom_widget)

        if wallet > 0:
            usd = btc_usd * wallet
            brl = btc_brl * wallet
            txt = f'Wallet: US$ {round(usd, 2)} - R$ {round(brl, 2)}'
            self.lbl_wallet.setText(txt)

        self.lbl_time.setText(self.data_hora())

        # end_time = time.time()
        # print(f"Tempo de execução: {end_time - start_time} segundos")

    def btn_clicked(self):
        if self.btn_time.text() == 'STOP':
            self.btn_time.setText('START')
            self.btn_update.setDisabled(False)
            cor = '#0f0' if self.config['theme'] == 'light' else '#0c0'
            self.btn_time.setStyleSheet(f'background: transparent; border: 0; color: {cor};')
            self.timer.stop()
        else:
            self.btn_time.setText('STOP')
            self.btn_update.setDisabled(True)
            self.btn_time.setStyleSheet('background: transparent; border: 0; color: red;')
            self.timer.start(10000)

    def upd_clicked(self):
        self.btn_update.setDisabled(True)
        self.btn_update.setText('Aguarde...')
        self.btn_update.setStyleSheet('border-radius: 0; border-right: 8 solid #0f0;')
        QTimer.singleShot(200, lambda: self.consult())
        QTimer.singleShot(2400, lambda: self.upd_normal())

    def all_clicked(self):
        self.btn_all.setDisabled(True)
        self.btn_all.setStyleSheet('border-radius: 0; border-right: 8 solid #0f0;')
        QTimer.singleShot(500, self.all_normal)

    def upd_normal(self):
        self.btn_update.setText('Atualizar')
        self.btn_update.setStyleSheet('border-radius: 0; border-right: 8 solid #888;')
        self.btn_update.setDisabled(False)

    def all_normal(self):
        res = CustomDialog('Lista geral', 'Deseja atualizar a lista geral?')
        if res.chosen:
            self.config = select_all()
            self.consult()
            self.btn_all.setDisabled(False)
            self.btn_all.setStyleSheet('border-radius: 0; border-right: 8 solid #888;')

    def dark_clicked(self, path):
        self.ev_theme.emit()
        self.consult()
        ico_time = cor_icon(f'{path}/icons/timer.svg')
        self.btn_time.setIcon(ico_time)

    @staticmethod
    def data_hora():
        data_e_hora_atuais = datetime.now()
        data_e_hora_em_texto = data_e_hora_atuais.strftime('%d/%m/%Y %H:%M:%S')
        return data_e_hora_em_texto
