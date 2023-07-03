import sys
import csv
import json
import typing
import smtplib
from dotenv import load_dotenv
import os
from datetime import date, time, datetime


from PyQt6 import QtCore

from server.utils import *

from PyQt6.QtWidgets import (
    QApplication, QFileDialog, QMainWindow, QDialog, QWidget
)
from PyQt6.uic import loadUi
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QTextCursor

from ui_mw import Ui_MainWindow
import ui_edit_dt, ui_new_rmd, ui_new_av

class EditDateTimeDialog(QDialog, ui_edit_dt.Ui_Dialog):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setupUi(self)

    def get_data(self):
        selected_date = self.calendarWidget.selectedDate().toPyDate()
        selected_time = self.timeEdit.time().toPyTime()
        selected_datetime = datetime.combine(selected_date, selected_time)
        return selected_datetime

class NewReminderDialog(QDialog, ui_new_rmd.Ui_Dialog):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setupUi(self)

    def get_data(self):
        frequencies = [
            'Once',
            'Daily',
            'Weekly',
            'Monthly',
            'Yearly',
            'Other'            
        ]
        reminder_name = self.lineEdit.text()
        reminder_time = self.timeEdit.time().toPyTime()
        reminder_freq = frequencies[self.comboBox.currentIndex()]
        reminder_fuzz = self.spinBox.value()
        data = {
            'reminder_name': reminder_name,
            'target_time': reminder_time,
            'frequency': reminder_freq,
            'fuzziness': reminder_fuzz
        }
        return data
    
class NewAvenueDialog(QDialog, ui_new_av.Ui_Dialog):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setupUi(self)
    
    def get_data(self):
        data = []
        return data

class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.connectSignalsSlots()
        self.save_location = ''
        self.reminders = []
        self.avenues = []
        self.frequencies = [
            'Once',
            'Daily',
            'Weekly',
            'Monthly',
            'Yearly',
            'Other'
        ]
        self.comboBoxFrequency.addItems(self.frequencies)
        self.listViewRemindersModel = QStandardItemModel()

    def connectSignalsSlots(self):
        self.actionNew_Reminder.triggered.connect(self.new_reminder_dialog)
        self.actionNew_Set.triggered.connect(self.placeholder_command)
        self.actionLoad_Set.triggered.connect(self.placeholder_command)
        self.actionSave.triggered.connect(self.placeholder_command)
        self.actionSave_as.triggered.connect(self.placeholder_command)

        self.pushButtonEditDueDate.clicked.connect(self.edit_date_time_dialog)
        self.pushButtonSaveChanges.clicked.connect(self.placeholder_command)
        self.pushButtonCancelChanges.clicked.connect(self.placeholder_command)
        self.pushButtonAddAvenue.clicked.connect(self.placeholder_command)
        self.pushButtonAPI.clicked.connect(self.placeholder_command)
        self.pushButtonTest.clicked.connect(self.placeholder_command)

    def edit_date_time_dialog(self):
        self.dialog = EditDateTimeDialog(self)
        self.dialog.setModal(True)
        if self.dialog.exec() == QDialog.DialogCode.Accepted:
            selected_date_time = self.dialog.get_data()
        # Change the datetime of the task selected here
        return selected_date_time

    def new_reminder_dialog(self):
        self.dialog = NewReminderDialog(self)
        self.dialog.setModal(True)
        self.dialog.comboBox.addItems(self.frequencies)
        if self.dialog.exec() == QDialog.DialogCode.Accepted:
            new_reminder_data = self.dialog.get_data()
        self.reminders.append(Reminder(**new_reminder_data))
        self.refresh_ui()

    def save_as(self, filepath=None):
        def save_it(file_location):
            try:
                with open(file_location, 'w') as f:
                    json_data = {
                            'save_location': self.save_location,
                            'reminders': self.reminders
                    }
                    json.dump(json_data, f, ensure_ascii=False, indent=4)
            except Exception as e:
                print(e)
        if not filepath:
            self.dialog = QFileDialog()
            self.dialog.setFileMode(QFileDialog.FileMode.AnyFile)
            if self.dialog.exec():
                selected_files = self.dialog.selectedFiles()
            self.save_location = selected_files[0]
            save_it(file_location=selected_files[0])
        else:
            self.save_location = filepath
            save_it(file_location=self.save_location)
        self.refresh_ui()
    
    def quicksave(self):
        try:
            self.save_as(filepath=self.save_location)
        except Exception as e:
            print(e)
        finally:
            pass

    def refresh_ui(self):
        self.listViewRemindersModel = QStandardItemModel()
        for i in self.reminders:
            new_item = QStandardItem(str(i))
            self.listViewRemindersModel.appendRow(new_item)
            self.listViewReminders.setModel(self.listViewRemindersModel)

    def add_avenue_window(self):
        self.dialog = NewAvenueDialog(self)
        self.dialog.setModal(True)
        if self.dialog.exec() == QDialog.DialogCode.Accepted:
            new_reminder_data = self.dialog.get_data()

    def placeholder_command(self):
        pass

    def test(self):
        self.save_as('C:/Users/bohnd/Documents/_codingProjects/reminders-app/ignore/test.json')

if __name__ == '__main__':
    load_dotenv()
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    win.test()
    sys.exit(app.exec())