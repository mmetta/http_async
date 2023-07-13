from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QColor, QPixmap, QPainter, QIcon

from sqlite_data import select_all


def cor_icon(path):
    config = select_all()
    color = config['color_primary']
    if path[-9:] == 'timer.svg':
        ico_cor = QColor('#000') if config['theme'] == 'dark' else QColor('#fff')
    else:
        ico_cor = QColor(color)
    pixmap = QPixmap(path)
    rect = QRect(1, 1, 24, 24)

    painter = QPainter(pixmap)
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)

    painter.setPen(Qt.NoPen)
    painter.fillRect(rect, ico_cor)

    painter.drawPixmap(22, 22, pixmap)
    painter.end()

    return QIcon(pixmap)
