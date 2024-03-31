import sys, datetime
from PySide6 import QtWidgets, QtCore

from PySide6.QtCore import QAbstractTableModel, Qt


def check_float(text: str) -> float | None:
    try:
        return float(text)
    except ValueError:
        return None


class PandasModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole or role == Qt.EditRole:
                value = self._data[index.row()][index.column()]
                return str(value)

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            if check_float(value) is not None:
                self._data[index.row()][index.column()] = value
                return True
        return False

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable


class CategoryWindow(QtWidgets.QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """

    def __init__(self, parent, categoryes: list):
        super().__init__()
        self.par = parent
        self.categoryes = categoryes
        self.correct_category()

    def correct_category(self):
        delete_button = QtWidgets.QPushButton("Удалить категорию")
        plus_button = QtWidgets.QPushButton("Добавить категорию")
        self.success_del_label = QtWidgets.QLabel(" ")
        self.success_add_label = QtWidgets.QLabel(" ")
        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(delete_button, 0, 1)
        self.layout.addWidget(self.category_combo_edit(), 0, 0)
        self.layout.addWidget(self.success_del_label, 1, 0)
        self.layout.addWidget(plus_button, 2, 1)
        self.layout.addWidget(self.category_input(), 2, 0)
        self.layout.addWidget(self.success_add_label, 3, 0)
        self.setLayout(self.layout)

        delete_button.clicked.connect(self.on_delete_button_click)
        plus_button.clicked.connect(self.on_plus_button_click)

        # self.setWindowTitle("Редактирование категорий")
        self.setGeometry(300, 100, 600, 200)

    def on_delete_button_click(self):
        text = self.combo_edit.currentText()
        self.combo_edit.removeItem(self.combo_edit.currentIndex())
        count = self.combo_edit.count()
        categoryes = [self.combo_edit.itemText(i) for i in range(count)]
        self.par.delete_category(categoryes=categoryes)
        self.success_del_label.setText(f'категория "{text}" удалена')
        self.layout.addWidget(self.success_del_label, 1, 0, 1, -1)

    def on_plus_button_click(self):
        text = self.category_input_field.text()
        count = self.combo_edit.count()
        categoryes = [self.combo_edit.itemText(i) for i in range(count)]
        if text not in categoryes:
            self.combo_edit.addItem(text)
            self.par.add_category(str(text))
            self.success_add_label.setText(f'категория "{text}" добавлена')
            self.layout.addWidget(self.success_add_label, 3, 0, 1, -1)
        else:
            self.success_add_label.setText(f'категория "{text}" уже существует')
            self.layout.addWidget(self.success_add_label, 3, 0, 1, -1)

    def category_combo_edit(self):
        self.combo_edit = QtWidgets.QComboBox()
        for i in self.categoryes:
            self.combo_edit.addItem(f"{i}")
        return self.combo_edit

    def category_input(self):
        self.category_input_field = QtWidgets.QLineEdit("Введите новую категорию")
        return self.category_input_field


class MainWindow(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_ui()

    def init_ui(self):
        expenses_label = QtWidgets.QLabel("Расходы")
        self.status_label = QtWidgets.QLabel(" ")
        control_label = QtWidgets.QLabel("Бюджет")
        add_button = QtWidgets.QPushButton("Добавить расход")
        invite_label = QtWidgets.QLabel("Сумма")
        category_label = QtWidgets.QLabel("Категория")
        correct_budget_button = QtWidgets.QPushButton("Редактировать бюджет")
        correct_category_button = QtWidgets.QPushButton("Редактировать категории")
        correct_list_button = QtWidgets.QPushButton("Редактировать записи")

        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(expenses_label, 0, 0)
        self.layout.addWidget(
            self.status_label, 0, 2, alignment=QtCore.Qt.AlignmentFlag.AlignRight
        )
        self.layout.addWidget(self.expenses_table_func(), 1, 0, 1, -1)
        self.layout.addWidget(control_label, 2, 0)
        self.layout.addWidget(self.control_table_func(), 3, 0, 1, -1)
        self.layout.addWidget(
            invite_label, 4, 0, 1, 1, alignment=QtCore.Qt.AlignmentFlag.AlignRight
        )
        self.layout.addWidget(
            self.expenses_input("Введите сумму расходов"), 4, 1, 1, -1
        )
        self.layout.addWidget(
            category_label, 5, 0, 1, 1, alignment=QtCore.Qt.AlignmentFlag.AlignRight
        )
        self.category_combobox()
        self.layout.addWidget(self.combo, 5, 1, 1, -1)
        self.layout.addWidget(add_button, 6, 0, 1, -1)

        self.layout.addWidget(correct_budget_button, 7, 0, 1, 1)
        self.layout.addWidget(correct_category_button, 7, 1, 1, 1)
        self.layout.addWidget(correct_list_button, 7, 2, 1, 1)

        self.setLayout(self.layout)

        add_button.clicked.connect(self.on_add_button_click)
        correct_budget_button.clicked.connect(self.on_budget_button_click)
        correct_category_button.clicked.connect(self.on_category_button_click)

        self.setWindowTitle("The Bookkeeper App")
        self.setGeometry(900, 100, 700, 500)

    def on_add_button_click(self):
        category_text = str(self.reading_combobox())
        sum_text = str(self.reading_sum())
        if check_float(sum_text) is None:
            dlg = QtWidgets.QErrorMessage()
            dlg.showMessage("Сумма должна быть введена в числовом формате.\n")
            dlg.setWindowTitle("QDialog")
            dlg.resize(200, 50)
            dlg.exec()
        else:
            self.expenses_table.setItem(0, 1, QtWidgets.QTableWidgetItem(sum_text))
            self.expenses_table.setItem(0, 2, QtWidgets.QTableWidgetItem(category_text))
            self.expenses_table.setItem(
                0,
                0,
                QtWidgets.QTableWidgetItem(
                    str(datetime.date.today().strftime("%d/%m/%Y"))
                ),
            )
            self.status_label.setText("Расходы добавлены")

    def on_category_button_click(self):
        count = self.combo.count()
        categoryes = [self.combo.itemText(i) for i in range(count)]
        self.w = CategoryWindow(self, categoryes=categoryes)
        self.w.show()

    def on_budget_button_click(self):

        day_budget, ok = QtWidgets.QInputDialog.getText(
            self,
            "Бюджет на день",
            "Введите бюджет на день",
        )
        if ok:
            self.control_table.setItem(
                0, 1, QtWidgets.QTableWidgetItem(str(day_budget))
            )

        week_budget, ok = QtWidgets.QInputDialog.getText(
            self,
            "Бюджет на неделю",
            "Введите бюджет на неделю",
        )
        if ok:
            self.control_table.setItem(
                1, 1, QtWidgets.QTableWidgetItem(str(week_budget))
            )
        month_budget, ok = QtWidgets.QInputDialog.getText(
            self,
            "Бюджет на месяц",
            "Введите бюджет на месяц",
        )
        if ok:
            self.control_table.setItem(
                2, 1, QtWidgets.QTableWidgetItem(str(month_budget))
            )

    def expenses_table_func(self):
        self.expenses_table = QtWidgets.QTableWidget(4, 20)
        self.expenses_table.setColumnCount(4)
        self.expenses_table.setRowCount(20)
        self.expenses_table.setHorizontalHeaderLabels(
            "Дата Сумма Категория Комментарий".split()
        )
        header = self.expenses_table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        self.expenses_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.expenses_table.verticalHeader().hide()
        return self.expenses_table

    def control_table_func(self):
        self.control_table = QtWidgets.QTableWidget(2, 3)

        self.control_table.setColumnCount(2)
        self.control_table.setRowCount(3)
        self.control_table.setHorizontalHeaderLabels("Сумма Бюджет".split())
        self.control_table.setVerticalHeaderLabels("День Неделя Месяц".split())
        hor_header = self.control_table.horizontalHeader()
        hor_header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        hor_header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        # hor_header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.control_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        ver_header = self.control_table.verticalHeader()
        ver_header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        ver_header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        ver_header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        self.control_table.setSizeAdjustPolicy(
            QtWidgets.QAbstractScrollArea.AdjustToContents
        )
        self.control_table.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )

        return self.control_table

    def expenses_input(self, text):
        self.expenses_input_field = QtWidgets.QLineEdit(f"{text}")
        return self.expenses_input_field

    def category_combobox(self):
        self.combo = QtWidgets.QComboBox()
        self.combo.addItem("Продукты")
        self.combo.addItem("Образование")
        self.combo.addItem("Транспорт")
        self.combo.addItem("Дом")
        return self.combo

    def reading_combobox(self):
        return self.combo.currentText()

    def reading_sum(self):
        return self.expenses_input_field.text()

    def add_category(self, text):
        self.combo.addItem(f"{text}")

    def delete_category(self, categoryes):
        self.combo.clear()
        for i in categoryes:
            self.combo.addItem(f"{i}")


app = QtWidgets.QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
app.exec_()
