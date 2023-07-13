from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QStandardItemModel, QStandardItem, QDoubleValidator
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QPushButton, QListView, QAbstractItemView, \
    QHBoxLayout, QLineEdit, QFrame

from atual_path import local_path
from binance_all import consult_all
from icon_color import cor_icon
from sqlite_data import select_all, update_data


class CustomDialog:
    def __init__(self, title, msg):
        super().__init__()

        path = Path(local_path())
        self.config = select_all()
        ico_win = cor_icon(f'{path}/icons/cog.svg')

        self.dialog_confirm = QDialog(None, Qt.WindowSystemMenuHint | Qt.WindowTitleHint)
        self.dialog_confirm.setWindowTitle(title)
        self.dialog_confirm.setFixedWidth(320)
        self.dialog_confirm.setWindowIcon(ico_win)
        self.chosen = ''
        self.list_my = self.config['my_list']

        self.list_all = None
        self.lbl_total = QLabel()

        if len(self.config['all_list']) == 0:
            self.upd_list_all()
        else:
            self.list_all = self.config['all_list']

        h_btn_box = QHBoxLayout()
        self.buttonBox = QPushButton('Fechar')
        self.buttonBox.setFixedWidth(100)
        self.buttonBox.clicked.connect(self.accept)
        h_btn_box.addWidget(self.buttonBox)

        self.layout = QVBoxLayout()
        message = QLabel(msg)

        count = len(self.config['all_list'])
        self.lbl_total.setText(f'Você tem {count} pares na lista.')

        self.lv_all = QListView()
        self.lv_all.setMaximumHeight(120)
        self.model = QStandardItemModel()
        self.lv_all.setSelectionMode(QAbstractItemView.SingleSelection)
        self.pop_model(self.list_all)
        self.lv_all.setModel(self.model)
        self.lv_all.clicked.connect(self.all_selected)

        h_btn_lay = QHBoxLayout()
        ico_all = cor_icon(f'{path}/icons/update.svg')
        self.btn_all = QPushButton('Atualizar')
        self.btn_all.setIcon(ico_all)
        self.btn_all.setFixedWidth(100)
        self.btn_all.setStyleSheet('border-radius: 0; border-right: 8 solid #888;')
        self.btn_all.clicked.connect(self.update_clicked)

        ico_add = cor_icon(f'{path}/icons/arrow-down.svg')
        self.btn_add = QPushButton('Adicionar')
        self.btn_add.setIcon(ico_add)
        self.btn_add.setFixedWidth(100)
        self.btn_add.setDisabled(True)
        self.btn_add.setStyleSheet('border-radius: 0; border-right: 8 solid #888;')
        self.btn_add.clicked.connect(self.list_add)
        h_btn_lay.addWidget(self.btn_all)
        h_btn_lay.addWidget(self.btn_add)

        self.lv_my = QListView()
        self.lv_my.setMaximumHeight(120)
        self.my_model = QStandardItemModel()
        self.lv_my.setSelectionMode(QAbstractItemView.SingleSelection)
        self.pop_my_model(self.list_my)
        self.lv_my.setModel(self.my_model)
        self.lv_my.clicked.connect(self.del_selected)

        h_lay_del = QHBoxLayout()
        ico_del = cor_icon(f'{path}/icons/close.svg')
        self.btn_del = QPushButton('Deletar')
        self.btn_del.setIcon(ico_del)
        self.btn_del.setDisabled(True)
        self.btn_del.setFixedWidth(100)
        self.btn_del.setStyleSheet('border-radius: 0; border-right: 8 solid #888;')
        self.btn_del.clicked.connect(self.del_list_my)
        h_lay_del.addWidget(self.btn_del)

        line = QFrame()
        line.setContentsMargins(5, 10, 5, 10)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        h_wallet = QHBoxLayout()
        lbl_wallet = QLabel('Carteira (BTC):')
        self.btn_wallet = QPushButton()
        self.btn_wallet.setDisabled(True)
        self.edt_wallet = QLineEdit()
        self.edt_wallet.setValidator(QDoubleValidator())
        self.edt_wallet.setText(self.config['wallet'])
        self.edt_wallet.textChanged.connect(lambda: self.btn_wallet.setDisabled(False))
        ico_wallet = cor_icon(f'{path}/icons/wallet.svg')
        self.btn_wallet.setIcon(ico_wallet)
        self.btn_wallet.clicked.connect(self.upd_wallet)
        h_wallet.addWidget(lbl_wallet)
        h_wallet.addWidget(self.edt_wallet)
        h_wallet.addWidget(self.btn_wallet)

        self.layout.addWidget(message)
        self.layout.addWidget(self.lbl_total)
        self.layout.addWidget(self.lv_all)
        self.layout.addLayout(h_btn_lay)
        self.layout.addWidget(self.lv_my)
        self.layout.addLayout(h_lay_del)
        self.layout.addLayout(h_wallet)
        self.layout.addWidget(line)
        self.layout.addLayout(h_btn_box)
        self.dialog_confirm.setLayout(self.layout)

        self.buttonBox.setFocus()

        self.dialog_confirm.exec()

    def list_add(self):
        item = None
        for index in self.lv_all.selectedIndexes():
            item = self.lv_all.model().itemFromIndex(index)
        if item:
            self.config['my_list'].append(item.text())
            self.upd_sqlite()
            self.btn_add.setDisabled(True)
            self.pop_my_model(self.list_my)

    def pop_model(self, items):
        for item in items:
            row = QStandardItem(item['symbol'])
            self.model.appendRow(row)

    def pop_my_model(self, array):
        self.my_model.clear()
        items = sorted(array)
        for item in items:
            row = QStandardItem(item)
            self.my_model.appendRow(row)

    def all_selected(self):
        self.btn_add.setDisabled(False)
        self.btn_del.setDisabled(True)

    def del_selected(self):
        self.btn_del.setDisabled(False)
        self.btn_add.setDisabled(True)

    def del_list_my(self):
        sel = None
        for index in self.lv_my.selectedIndexes():
            sel = self.lv_my.model().itemFromIndex(index)
        if sel:
            array = []
            for item in self.config['my_list']:
                if item != sel.text():
                    array.append(item)
            self.config['my_list'] = array
            self.upd_sqlite()
            self.btn_del.setDisabled(True)
            self.pop_my_model(self.list_my)

    def update_clicked(self):
        self.btn_all.setDisabled(True)
        self.btn_all.setText('Aguarde...')
        self.btn_all.setStyleSheet('border-radius: 0; border-right: 8 solid #0f0;')
        QTimer.singleShot(100, lambda: self.upd_list_all())
        QTimer.singleShot(1500, lambda: self.upd_normal())

    def upd_normal(self):
        self.btn_all.setText('Atualizar')
        self.btn_all.setStyleSheet('border-radius: 0; border-right: 8 solid #888;')
        self.btn_all.setDisabled(False)

    def upd_wallet(self):
        txt = self.edt_wallet.text()
        val = txt.replace(',', '.')
        self.config['wallet'] = val
        self.upd_sqlite()
        self.btn_wallet.setDisabled(True)

    def upd_list_all(self):
        list0 = []
        items = consult_all
        for item in items:
            if float(item['bidPrice']) > 0:
                obj = {
                    'symbol': item['symbol'],
                    'bidPrice': item['bidPrice'],
                    'priceChangePercent': item['priceChangePercent']
                }
                list0.append(obj)
        result = sorted(list0, key=lambda x: x['symbol'])
        self.config['all_list'] = result
        self.list_all = result
        self.upd_sqlite()
        count = len(self.list_all)
        self.lbl_total.setText(f'Você tem {count} pares na lista.')

    def upd_sqlite(self):
        update_data(self.config)
        self.config = select_all()
        self.list_my = self.config['my_list']
        self.list_all = self.config['all_list']

    def accept(self):
        self.chosen = "Success"
        self.dialog_confirm.close()
