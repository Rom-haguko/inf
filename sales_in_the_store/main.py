import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel, QSpinBox,
    QMessageBox, QHeaderView, QAbstractItemView, QGroupBox, QDateEdit,
    QTextEdit
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
import database as db

class ShoppingCartApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Система Учета Товаров Магазина")
        self.setGeometry(100, 100, 1000, 700)

        self.cart = []
        self.selected_product_id = None
        self.selected_product_details = None

        db.initialize_database()

        self.initUI()
        self.load_products()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        left_panel_layout = QVBoxLayout()

        products_group = QGroupBox("Доступные товары на складе")
        products_layout = QVBoxLayout()
        self.product_table = QTableWidget()
        self.product_table.setColumnCount(5)
        self.product_table.setHorizontalHeaderLabels(["ID", "Название", "Категория", "Цена", "На складе"])
        self.product_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.product_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.product_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.product_table.verticalHeader().setVisible(False)
        self.product_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.product_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.product_table.setMinimumHeight(300)
        self.product_table.itemSelectionChanged.connect(self.on_product_selected)
        products_layout.addWidget(self.product_table)
        products_group.setLayout(products_layout)
        left_panel_layout.addWidget(products_group)

        add_to_cart_group = QGroupBox("Добавить в корзину")
        add_to_cart_layout = QGridLayout()

        self.selected_product_label = QLabel("Товар не выбран")
        self.selected_product_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        add_to_cart_layout.addWidget(self.selected_product_label, 0, 0, 1, 2)

        add_to_cart_layout.addWidget(QLabel("Количество:"), 1, 0)
        self.quantity_spinbox = QSpinBox()
        self.quantity_spinbox.setMinimum(1)
        self.quantity_spinbox.setEnabled(False)
        add_to_cart_layout.addWidget(self.quantity_spinbox, 1, 1)

        self.add_to_cart_button = QPushButton("Добавить в корзину")
        self.add_to_cart_button.setEnabled(False)
        self.add_to_cart_button.clicked.connect(self.add_item_to_cart)
        add_to_cart_layout.addWidget(self.add_to_cart_button, 2, 0, 1, 2)

        add_to_cart_group.setLayout(add_to_cart_layout)
        left_panel_layout.addWidget(add_to_cart_group)

        left_panel_layout.addStretch(1)

        right_panel_layout = QVBoxLayout()

        cart_group = QGroupBox("Корзина")
        cart_layout = QVBoxLayout()
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(4)
        self.cart_table.setHorizontalHeaderLabels(["Название", "Кол-во", "Цена за шт.", "Сумма"])
        self.cart_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.cart_table.verticalHeader().setVisible(False)
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.cart_table.setMinimumHeight(200)
        cart_layout.addWidget(self.cart_table)

        cart_buttons_layout = QHBoxLayout()
        self.total_amount_label = QLabel("Итого: 0.00 руб.")
        self.total_amount_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        cart_buttons_layout.addWidget(self.total_amount_label)
        cart_buttons_layout.addStretch(1)

        self.clear_cart_button = QPushButton("Очистить корзину")
        self.clear_cart_button.clicked.connect(self.clear_cart)
        cart_buttons_layout.addWidget(self.clear_cart_button)

        self.checkout_button = QPushButton("Оформить покупку")
        self.checkout_button.clicked.connect(self.checkout)
        self.checkout_button.setEnabled(False)
        cart_buttons_layout.addWidget(self.checkout_button)
        cart_layout.addLayout(cart_buttons_layout)

        cart_group.setLayout(cart_layout)
        right_panel_layout.addWidget(cart_group)

        report_group = QGroupBox("Отчеты по продажам")
        report_layout = QVBoxLayout()
        report_controls_layout = QHBoxLayout()

        report_controls_layout.addWidget(QLabel("Дата:"))
        self.report_date_edit = QDateEdit()
        self.report_date_edit.setDate(QDate.currentDate())
        self.report_date_edit.setCalendarPopup(True)
        self.report_date_edit.setDisplayFormat("yyyy-MM-dd")
        report_controls_layout.addWidget(self.report_date_edit)

        self.generate_report_button = QPushButton("Сформировать отчет")
        self.generate_report_button.clicked.connect(self.generate_sales_report)
        report_controls_layout.addWidget(self.generate_report_button)
        report_controls_layout.addStretch(1)
        report_layout.addLayout(report_controls_layout)

        self.report_output = QTextEdit()
        self.report_output.setReadOnly(True)
        self.report_output.setMinimumHeight(150)
        report_layout.addWidget(self.report_output)

        report_group.setLayout(report_layout)
        right_panel_layout.addWidget(report_group)

        main_layout.addLayout(left_panel_layout, 1)
        main_layout.addLayout(right_panel_layout, 1)

    def load_products(self):
        self.product_table.setRowCount(0)
        try:
            products = db.get_available_products()
            self.product_table.setRowCount(len(products))
            for row_idx, product in enumerate(products):
                self.product_table.setItem(row_idx, 0, QTableWidgetItem(str(product['product_id'])))
                self.product_table.setItem(row_idx, 1, QTableWidgetItem(product['name']))
                self.product_table.setItem(row_idx, 2, QTableWidgetItem(product['category']))
                self.product_table.setItem(row_idx, 3, QTableWidgetItem(f"{product['price']:.2f}"))
                self.product_table.setItem(row_idx, 4, QTableWidgetItem(str(product['stock_quantity'])))
                self.product_table.item(row_idx, 0).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.product_table.item(row_idx, 3).setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.product_table.item(row_idx, 4).setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить товары: {e}")
        self.clear_selection_and_controls()

    def on_product_selected(self):
        selected_rows = self.product_table.selectionModel().selectedRows()
        if not selected_rows:
            self.clear_selection_and_controls()
            return

        selected_row = selected_rows[0].row()
        product_id_item = self.product_table.item(selected_row, 0)
        product_name_item = self.product_table.item(selected_row, 1)
        stock_item = self.product_table.item(selected_row, 4)
        price_item = self.product_table.item(selected_row, 3)

        if not all([product_id_item, product_name_item, stock_item, price_item]):
            self.clear_selection_and_controls()
            return

        try:
            self.selected_product_id = int(product_id_item.text())
            product_name = product_name_item.text()
            stock_quantity = int(stock_item.text())
            price = float(price_item.text())

            self.selected_product_details = {
                'product_id': self.selected_product_id,
                'name': product_name,
                'price': price,
                'max_quantity': stock_quantity
            }

            self.selected_product_label.setText(f"Выбрано: {product_name} (макс: {stock_quantity})")
            self.quantity_spinbox.setMaximum(stock_quantity)
            self.quantity_spinbox.setValue(1)
            self.quantity_spinbox.setEnabled(True)
            self.add_to_cart_button.setEnabled(True)

        except (ValueError, TypeError) as e:
            QMessageBox.warning(self, "Ошибка данных", f"Некорректные данные в таблице: {e}")
            self.clear_selection_and_controls()

    def clear_selection_and_controls(self):
        self.product_table.clearSelection()
        self.selected_product_id = None
        self.selected_product_details = None
        self.selected_product_label.setText("Товар не выбран")
        self.quantity_spinbox.setValue(1)
        self.quantity_spinbox.setEnabled(False)
        self.add_to_cart_button.setEnabled(False)

    def add_item_to_cart(self):
        if not self.selected_product_details:
            QMessageBox.warning(self, "Внимание", "Сначала выберите товар из списка.")
            return

        quantity_to_add = self.quantity_spinbox.value()
        product_id = self.selected_product_details['product_id']
        product_name = self.selected_product_details['name']
        price = self.selected_product_details['price']
        max_quantity = self.selected_product_details['max_quantity']

        if quantity_to_add <= 0:
            QMessageBox.warning(self, "Внимание", "Количество должно быть больше нуля.")
            return

        existing_item = None
        for item in self.cart:
            if item['product_id'] == product_id:
                existing_item = item
                break

        if existing_item:
            new_quantity = existing_item['quantity'] + quantity_to_add
            if new_quantity > max_quantity:
                 QMessageBox.warning(self, "Ошибка", f"Нельзя добавить больше {max_quantity} шт. товара '{product_name}'. В корзине уже {existing_item['quantity']} шт.")
                 return
            existing_item['quantity'] = new_quantity
        else:
            if quantity_to_add > max_quantity:
                 QMessageBox.warning(self, "Ошибка", f"Нельзя добавить больше {max_quantity} шт. товара '{product_name}'.")
                 return
            self.cart.append({
                'product_id': product_id,
                'name': product_name,
                'quantity': quantity_to_add,
                'price': price,
                'max_quantity': max_quantity
            })

        self.update_cart_display()
        self.clear_selection_and_controls()

    def update_cart_display(self):
        self.cart_table.setRowCount(0)
        total_amount = 0.0

        if not self.cart:
            self.total_amount_label.setText("Итого: 0.00 руб.")
            self.checkout_button.setEnabled(False)
            return

        self.cart_table.setRowCount(len(self.cart))
        for row_idx, item in enumerate(self.cart):
            item_total = item['quantity'] * item['price']
            total_amount += item_total

            self.cart_table.setItem(row_idx, 0, QTableWidgetItem(item['name']))
            self.cart_table.setItem(row_idx, 1, QTableWidgetItem(str(item['quantity'])))
            self.cart_table.setItem(row_idx, 2, QTableWidgetItem(f"{item['price']:.2f}"))
            self.cart_table.setItem(row_idx, 3, QTableWidgetItem(f"{item_total:.2f}"))

            self.cart_table.item(row_idx, 1).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.cart_table.item(row_idx, 2).setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.cart_table.item(row_idx, 3).setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.total_amount_label.setText(f"Итого: {total_amount:.2f} руб.")
        self.checkout_button.setEnabled(True)

    def clear_cart(self):
        self.cart = []
        self.update_cart_display()

    def checkout(self):
        if not self.cart:
            QMessageBox.warning(self, "Корзина пуста", "Нечего оформлять.")
            return

        reply = QMessageBox.question(self, "Подтверждение покупки",
                                     f"Оформить покупку на сумму {self.total_amount_label.text()}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            success, message = db.record_sale(self.cart)
            if success:
                QMessageBox.information(self, "Успешно", message)
                self.clear_cart()
                self.load_products()
            else:
                QMessageBox.critical(self, "Ошибка оформления", message)
                self.load_products()

    def generate_sales_report(self):
        report_date_str = self.report_date_edit.date().toString("yyyy-MM-dd")
        self.report_output.clear()

        try:
            items_sold, total_revenue = db.get_sales_report_by_date(report_date_str)

            report_text = f"--- Отчет по продажам за {report_date_str} ---\n\n"
            report_text += "Проданные товары:\n"
            if items_sold:
                 max_name_len = 0
                 if items_sold:
                     max_name_len = max(len(item['name']) for item in items_sold)

                 for item in items_sold:
                     report_text += f"- {item['name']:<{max_name_len}} : {item['total_quantity']:>5} шт.\n"
            else:
                report_text += "- За эту дату продаж не найдено.\n"

            report_text += f"\nОбщая выручка за {report_date_str}: {total_revenue:.2f} руб."

            self.report_output.setText(report_text)

        except Exception as e:
            self.report_output.setText(f"Ошибка при генерации отчета: {e}")
            QMessageBox.critical(self, "Ошибка отчета", f"Не удалось сформировать отчет: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ShoppingCartApp()
    window.show()
    sys.exit(app.exec())
