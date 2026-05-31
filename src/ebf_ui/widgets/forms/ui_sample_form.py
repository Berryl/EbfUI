# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'sample_form.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QVBoxLayout, QWidget)

class Ui_personForm(object):
    def setupUi(self, personForm):
        if not personForm.objectName():
            personForm.setObjectName(u"personForm")
        personForm.resize(345, 128)
        personForm.setMinimumSize(QSize(300, 100))
        self.verticalLayout = QVBoxLayout(personForm)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(12)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.nameLabel = QLabel(personForm)
        self.nameLabel.setObjectName(u"nameLabel")
        font = QFont()
        font.setBold(True)
        self.nameLabel.setFont(font)

        self.horizontalLayout.addWidget(self.nameLabel)

        self.nameLineEdit = QLineEdit(personForm)
        self.nameLineEdit.setObjectName(u"nameLineEdit")

        self.horizontalLayout.addWidget(self.nameLineEdit)

        self.saveButton = QPushButton(personForm)
        self.saveButton.setObjectName(u"saveButton")
        self.saveButton.setEnabled(False)
        self.saveButton.setMinimumSize(QSize(100, 0))

        self.horizontalLayout.addWidget(self.saveButton)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(personForm)

        self.saveButton.setDefault(True)


        QMetaObject.connectSlotsByName(personForm)
    # setupUi

    def retranslateUi(self, personForm):
        personForm.setWindowTitle(QCoreApplication.translate("personForm", u"Samplw Form", None))
        self.nameLabel.setText(QCoreApplication.translate("personForm", u"Name", None))
        self.nameLineEdit.setPlaceholderText(QCoreApplication.translate("personForm", u"Enter name....", None))
        self.saveButton.setText(QCoreApplication.translate("personForm", u"Save", None))
    # retranslateUi

