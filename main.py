from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import TwoLineListItem
from kivymd.uix.snackbar import Snackbar
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.metrics import dp
from datetime import datetime
import sqlite3
import os

# --- KV LAYOUT (The User Interface Design) ---
KV = '''
MDScreenManager:
    HomeScreen:
    HistoryScreen:

<HomeScreen>:
    name: "home"
    MDBoxLayout:
        orientation: "vertical"
        
        MDTopAppBar:
            title: "Expense Manager"
            elevation: 4
            pos_hint: {"top": 1}
            right_action_items: [["history", lambda x: app.switch_screen("history")]]

        MDScrollView:
            MDBoxLayout:
                orientation: "vertical"
                padding: dp(20)
                spacing: dp(20)
                adaptive_height: True

                MDLabel:
                    id: balance_label
                    text: "Wallet Balance: ₹0.00"
                    font_style: "H5"
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: 0, 0.5, 0, 1

                MDTextField:
                    id: date_field
                    hint_text: "Date"
                    icon_right: "calendar"
                    on_focus: if self.focus: app.show_date_picker()

                MDTextField:
                    id: company_field
                    hint_text: "Company"
                    icon_right: "domain"

                MDTextField:
                    id: payee_field
                    hint_text: "Payee"
                    icon_right: "account"

                MDTextField:
                    id: category_field
                    hint_text: "Category"
                    icon_right: "shape"
                    on_focus: if self.focus: app.open_category_menu()

                MDTextField:
                    id: amount_field
                    hint_text: "Amount (₹)"
                    input_filter: "float"
                    icon_right: "currency-inr"

                MDRaisedButton:
                    text: "SAVE EXPENSE"
                    pos_hint: {"center_x": .5}
                    size_hint_x: 1
                    on_release: app.save_expense()

<HistoryScreen>:
    name: "history"
    MDBoxLayout:
        orientation: "vertical"
        
        MDTopAppBar:
            title: "Recent Transactions"
            left_action_items: [["arrow-left", lambda x: app.switch_screen("home")]]
            elevation: 4

        MDScrollView:
            MDList:
                id: history_list
'''

class ExpenseApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        
        # --- DATABASE SETUP (Same logic as your old app) ---
        # On Android, we must store the DB in the user data directory
        self.db_name = os.path.join(self.user_data_dir, 'expenses_mobile.db')
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
        
        return Builder.load_string(KV)

    def on_start(self):
        # Initialize default categories if empty
        if not self.get_master_data('categories'):
            for n in ['Travel', 'Food', 'Office Supplies', 'Salary']:
                self.cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (n,))
            self.conn.commit()
            
        # Initialize simple wallet balance if 0
        self.update_balance_display()

        # Set today's date
        today = datetime.now()
        self.root.get_screen("home").ids.date_field.text = today.strftime("%Y-%m-%d")

        # Setup Category Dropdown
        categories = self.get_master_data('categories')
        menu_items = [
            {
                "text": f"{i}",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"{i}": self.set_category(x),
            } for i in categories
        ]
        self.menu = MDDropdownMenu(
            caller=self.root.get_screen("home").ids.category_field,
            items=menu_items,
            width_mult=4,
        )

    def create_tables(self):
        # Kept your exact schema to maintain logic consistency
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS companies (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS payees (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS categories (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL)''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, 
                company TEXT, payee TEXT, category TEXT, amount REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def get_master_data(self, table):
        try:
            self.cursor.execute(f"SELECT name FROM {table}")
            return [row[0] for row in self.cursor.fetchall()]
        except: return []

    def open_category_menu(self):
        self.menu.open()

    def set_category(self, text_item):
        self.root.get_screen("home").ids.category_field.text = text_item
        self.menu.dismiss()

    def show_date_picker(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_date_save)
        date_dialog.open()

    def on_date_save(self, instance, value, date_range):
        self.root.get_screen("home").ids.date_field.text = str(value)

    def update_balance_display(self):
        # Simple calculation of total expenses for this demo
        self.cursor.execute("SELECT SUM(amount) FROM expenses")
        res = self.cursor.fetchone()[0]
        total_exp = res if res else 0.0
        # Assuming a dummy wallet start of 50,000 for demo
        balance = 50000.0 - total_exp
        self.root.get_screen("home").ids.balance_label.text = f"Wallet Balance: ₹{balance:,.2f}"

    def save_expense(self):
        screen = self.root.get_screen("home")
        date = screen.ids.date_field.text
        company = screen.ids.company_field.text
        payee = screen.ids.payee_field.text
        category = screen.ids.category_field.text
        amount = screen.ids.amount_field.text

        if not amount or not category:
            Snackbar(text="Please fill Amount and Category").open()
            return

        try:
            amt_float = float(amount)
            # Insert logic (Simplified for mobile)
            self.cursor.execute(
                "INSERT INTO expenses (date, company, payee, category, amount) VALUES (?,?,?,?,?)",
                (date, company, payee, category, amt_float)
            )
            self.conn.commit()
            
            Snackbar(text="Expense Saved Successfully!").open()
            self.update_balance_display()
            
            # Clear fields
            screen.ids.amount_field.text = ""
            screen.ids.payee_field.text = ""
            
        except ValueError:
            Snackbar(text="Invalid Amount").open()

    def switch_screen(self, screen_name):
        self.root.current = screen_name
        if screen_name == "history":
            self.load_history()

    def load_history(self):
        history_list = self.root.get_screen("history").ids.history_list
        history_list.clear_widgets()
        
        self.cursor.execute("SELECT date, category, amount, payee FROM expenses ORDER BY id DESC LIMIT 20")
        rows = self.cursor.fetchall()
        
        for row in rows:
            # row: 0=date, 1=cat, 2=amt, 3=payee
            history_list.add_widget(
                TwoLineListItem(
                    text=f"₹{row[2]:,.2f} - {row[1]}",
                    secondary_text=f"{row[0]} | {row[3]}"
                )
            )

if __name__ == "__main__":
    ExpenseApp().run()