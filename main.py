from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import TwoLineAvatarIconListItem, OneLineIconListItem, IconLeftWidget, IconRightWidget
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.widget import Widget
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.metrics import dp
from datetime import datetime
import sqlite3
import os
import traceback

# --- KV LAYOUT ---
# મેં અહીંથી બધું જ જટિલ લોજીક કાઢી નાખ્યું છે.
# હવે બટન સીધું 'app.change_screen()' ને કોલ કરશે.
KV = '''
<DrawerClickableItem@OneLineIconListItem>:
    theme_text_color: "Custom"
    text_color: 0, 0, 0, 1

<ContentNavigationDrawer>:
    orientation: "vertical"
    padding: "8dp"
    spacing: "8dp"
    
    MDScrollView:
        MDList:
            DrawerClickableItem:
                text: "Dashboard"
                on_release: app.change_screen("dashboard")
                IconLeftWidget:
                    icon: "view-dashboard"

            DrawerClickableItem:
                text: "Reports"
                on_release: app.change_screen("reports")
                IconLeftWidget:
                    icon: "file-document"

            DrawerClickableItem:
                text: "Wallet History"
                on_release: app.change_screen("wallet_hist")
                IconLeftWidget:
                    icon: "wallet"

            MDLabel:
                text: "Master Data"
                font_style: "Caption"
                size_hint_y: None
                height: self.texture_size[1]
                padding: dp(15), dp(10)

            DrawerClickableItem:
                text: "Manage Companies"
                on_release: app.open_master("companies")
                IconLeftWidget:
                    icon: "domain"

            DrawerClickableItem:
                text: "Manage Payees"
                on_release: app.open_master("payees")
                IconLeftWidget:
                    icon: "account-cash"

            DrawerClickableItem:
                text: "Manage Categories"
                on_release: app.open_master("categories")
                IconLeftWidget:
                    icon: "shape"

<ExpenseListItem>:
    IconRightWidget:
        icon: "delete"
        theme_text_color: "Custom"
        text_color: 1, 0, 0, 1
        on_release: app.confirm_delete_expense(root.id_val)

<MasterListItem>:
    IconRightWidget:
        icon: "pencil"
        on_release: app.show_edit_master_dialog(root.text)

MDScreen:
    MDNavigationLayout:
        MDScreenManager:
            id: screen_manager
            
            # --- DASHBOARD SCREEN ---
            MDScreen:
                name: "dashboard"
                MDBoxLayout:
                    orientation: 'vertical'
                    
                    MDTopAppBar:
                        title: "Expense Manager"
                        elevation: 4
                        pos_hint: {"top": 1}
                        left_action_items: [["menu", lambda x: nav_drawer.set_state("open")]]

                    MDScrollView:
                        MDBoxLayout:
                            orientation: "vertical"
                            padding: dp(20)
                            spacing: dp(15)
                            adaptive_height: True

                            MDCard:
                                orientation: "vertical"
                                padding: dp(15)
                                spacing: dp(5)
                                size_hint_y: None
                                height: dp(180) 
                                elevation: 2
                                radius: [15]
                                
                                MDLabel:
                                    text: "Wallet Balance"
                                    halign: "center"
                                    theme_text_color: "Secondary"
                                    size_hint_y: None
                                    height: dp(30)
                                
                                MDLabel:
                                    id: wallet_bal_label
                                    text: "₹0.00"
                                    halign: "center"
                                    font_style: "H4"
                                    theme_text_color: "Primary"
                                    size_hint_y: None
                                    height: dp(40)

                                # Vertical Space as requested
                                Widget:
                                    size_hint_y: None
                                    height: dp(20)

                                # Centered Buttons
                                MDBoxLayout:
                                    orientation: 'horizontal'
                                    spacing: dp(20)
                                    adaptive_size: True
                                    pos_hint: {"center_x": .5}
                                    
                                    MDRaisedButton:
                                        text: "+ Add Funds"
                                        md_bg_color: 0, 0.7, 0, 1
                                        text_color: 1, 1, 1, 1
                                        on_release: app.show_wallet_dialog("add")
                                        
                                    MDRaisedButton:
                                        text: "- Withdraw"
                                        md_bg_color: 0.8, 0, 0, 1
                                        text_color: 1, 1, 1, 1
                                        on_release: app.show_wallet_dialog("remove")

                            MDLabel:
                                text: "New Expense Entry"
                                font_style: "H6"
                                size_hint_y: None
                                height: dp(30)
                                pady: dp(10)

                            MDTextField:
                                id: date_field
                                hint_text: "Date"
                                icon_right: "calendar"
                                on_focus: if self.focus: app.show_date_picker()

                            MDTextField:
                                id: company_field
                                hint_text: "Company"
                                icon_right: "domain"
                                on_focus: if self.focus: app.open_menu(self, "companies")

                            MDTextField:
                                id: payee_field
                                hint_text: "Payee"
                                icon_right: "account"
                                on_focus: if self.focus: app.open_menu(self, "payees")

                            MDTextField:
                                id: category_field
                                hint_text: "Category"
                                icon_right: "shape"
                                on_focus: if self.focus: app.open_menu(self, "categories")

                            MDTextField:
                                id: amount_field
                                hint_text: "Amount (₹)"
                                input_filter: "float"
                                icon_right: "currency-inr"

                            MDRaisedButton:
                                text: "SAVE EXPENSE"
                                size_hint_x: 1
                                on_release: app.save_expense()
                                elevation: 2

            # --- REPORTS SCREEN ---
            MDScreen:
                name: "reports"
                MDBoxLayout:
                    orientation: 'vertical'
                    MDTopAppBar:
                        title: "Reports"
                        left_action_items: [["menu", lambda x: nav_drawer.set_state("open")]]
                        right_action_items: [["refresh", lambda x: app.load_report_data()]]
                    
                    MDBoxLayout:
                        size_hint_y: None
                        height: dp(50)
                        padding: dp(10)
                        spacing: dp(10)
                        
                        MDLabel:
                            text: "Recent Expenses"
                            bold: True
                            valign: "center"

                    MDRecycleView:
                        id: report_list
                        viewclass: "ExpenseListItem"
                        RecycleBoxLayout:
                            default_size: None, dp(72)
                            default_size_hint: 1, None
                            size_hint_y: None
                            height: self.minimum_height
                            orientation: 'vertical'

            # --- MASTER DATA SCREEN ---
            MDScreen:
                name: "master_data"
                MDBoxLayout:
                    orientation: 'vertical'
                    MDTopAppBar:
                        id: master_toolbar
                        title: "Manage Master"
                        left_action_items: [["arrow-left", lambda x: app.change_screen("dashboard")]]
                    
                    MDRecycleView:
                        id: master_list
                        viewclass: "MasterListItem"
                        RecycleBoxLayout:
                            default_size: None, dp(56)
                            default_size_hint: 1, None
                            size_hint_y: None
                            height: self.minimum_height
                            orientation: 'vertical'

                MDFloatingActionButton:
                    icon: "plus"
                    pos_hint: {"right": .95, "bottom": .05}
                    on_release: app.show_add_master_dialog()

            # --- WALLET HISTORY SCREEN ---
            MDScreen:
                name: "wallet_hist"
                MDBoxLayout:
                    orientation: 'vertical'
                    MDTopAppBar:
                        title: "Wallet History"
                        left_action_items: [["arrow-left", lambda x: app.change_screen("dashboard")]]
                    
                    MDScrollView:
                        MDList:
                            id: wallet_list

        MDNavigationDrawer:
            id: nav_drawer
            ContentNavigationDrawer:
'''

# --- PYTHON LOGIC ---

class ContentNavigationDrawer(MDBoxLayout):
    pass

class ExpenseListItem(TwoLineAvatarIconListItem):
    id_val = NumericProperty(0)

class MasterListItem(OneLineIconListItem):
    pass

class ExpenseApp(MDApp):
    dialog = None # Dialog Object holder
    wallet_input = None # Wallet Input holder

    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        
        try:
            # Database setup
            self.db_name = os.path.join(self.user_data_dir, 'expenses_final_v8.db')
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            self.create_tables()
            
            self.current_master_table = "" 
            return Builder.load_string(KV)
        except Exception as e:
            return MDLabel(text=f"INIT ERROR: {str(e)}", halign="center")

    def on_start(self):
        try:
            # Default Categories
            if not self.get_master_list('categories'):
                for n in ['Travel', 'Food', 'Office', 'Salary']:
                    self.cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (n,))
                self.conn.commit()
                
            self.update_balance_display()
            
            # Set Date
            today = datetime.now()
            screen = self.root.ids.screen_manager.get_screen("dashboard")
            screen.ids.date_field.text = today.strftime("%Y-%m-%d")
        except:
            pass

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS companies (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS payees (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS categories (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, month TEXT, year INTEGER, company TEXT, payee TEXT, category TEXT, amount REAL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS wallet_transactions (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT NOT NULL, amount REAL NOT NULL, remark TEXT, expense_id INTEGER, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        self.conn.commit()

    # --- NAVIGATION HUB (This Fixes Sidebar Crashes) ---
    def change_screen(self, screen_name):
        # Close Drawer first
        self.root.ids.nav_drawer.set_state("close")
        
        # Then Switch Screen
        if screen_name == "reports":
            self.load_report_data()
        elif screen_name == "wallet_hist":
            self.load_wallet_history()
            
        self.root.ids.screen_manager.current = screen_name

    def open_master(self, table_name):
        self.root.ids.nav_drawer.set_state("close")
        self.current_master_table = table_name
        
        screen = self.root.ids.screen_manager.get_screen("master_data")
        screen.ids.master_toolbar.title = f"Manage {table_name.capitalize()}"
        self.load_master_data()
        
        self.root.ids.screen_manager.current = "master_data"

    # --- WALLET DIALOG (This Fixes Wallet Crashes) ---
    def show_wallet_dialog(self, trans_type):
        self.trans_type_temp = trans_type
        title = "Add Funds" if trans_type == 'add' else "Withdraw Funds"
        
        # Create text field and store in SELF so it persists
        self.wallet_input = MDTextField(hint_text="Amount", input_filter="float")
        self.wallet_remark = MDTextField(hint_text="Remark (Optional)")
        
        content = MDBoxLayout(orientation="vertical", spacing="12dp", size_hint_y=None, height="100dp")
        content.add_widget(self.wallet_input)
        content.add_widget(self.wallet_remark)
        
        self.dialog = MDDialog(
            title=title,
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="CONFIRM", on_release=lambda x: self.process_wallet_trans())
            ],
        )
        self.dialog.open()

    def process_wallet_trans(self):
        try:
            # Safely access the text
            if not self.wallet_input: return
            
            amt_text = self.wallet_input.text
            if not amt_text:
                Snackbar(text="Please enter amount").open()
                return

            amt = float(amt_text)
            if amt <= 0:
                Snackbar(text="Amount must be > 0").open()
                return
            
            remark = self.wallet_remark.text if self.wallet_remark else ""
            
            self.cursor.execute('INSERT INTO wallet_transactions (type, amount, remark) VALUES (?, ?, ?)', 
                               (self.trans_type_temp, amt, remark))
            self.conn.commit()
            
            self.dialog.dismiss()
            self.update_balance_display()
            Snackbar(text="Success!").open()
            
        except ValueError:
            Snackbar(text="Invalid Amount").open()
        except Exception as e:
            if self.dialog: self.dialog.dismiss()
            Snackbar(text=f"Error: {str(e)}").open()

    def update_balance_display(self):
        try:
            self.cursor.execute("SELECT SUM(CASE WHEN type = 'add' THEN amount ELSE -amount END) FROM wallet_transactions")
            res = self.cursor.fetchone()[0]
            bal = res if res else 0.0
            screen = self.root.ids.screen_manager.get_screen("dashboard")
            screen.ids.wallet_bal_label.text = f"₹{bal:,.2f}"
        except: pass

    # --- HELPERS ---
    def get_master_list(self, table):
        try:
            self.cursor.execute(f"SELECT name FROM {table}")
            return [row[0] for row in self.cursor.fetchall()]
        except: return []

    def show_date_picker(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_date_save)
        date_dialog.open()

    def on_date_save(self, instance, value, date_range):
        self.root.ids.screen_manager.get_screen("dashboard").ids.date_field.text = str(value)

    def open_menu(self, item, table):
        menu_items = [
            {
                "text": f"{i}",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"{i}": self.set_item(item, x),
            } for i in self.get_master_list(table)
        ]
        self.menu = MDDropdownMenu(caller=item, items=menu_items, width_mult=4)
        self.menu.open()

    def set_item(self, item_widget, text):
        item_widget.text = text
        self.menu.dismiss()

    def save_expense(self):
        screen = self.root.ids.screen_manager.get_screen("dashboard")
        date = screen.ids.date_field.text
        company = screen.ids.company_field.text
        payee = screen.ids.payee_field.text
        category = screen.ids.category_field.text
        amount_str = screen.ids.amount_field.text

        if not amount_str or not company or not payee:
            Snackbar(text="Fill all fields").open()
            return

        try:
            amount = float(amount_str)
            dt_obj = datetime.strptime(date, "%Y-%m-%d")
            
            self.cursor.execute(
                "INSERT INTO expenses (date, month, year, company, payee, category, amount) VALUES (?,?,?,?,?,?,?)",
                (date, dt_obj.strftime("%B"), dt_obj.year, company, payee, category, amount)
            )
            eid = self.cursor.lastrowid
            self.cursor.execute(
                "INSERT INTO wallet_transactions (type, amount, remark, expense_id) VALUES (?,?,?,?)",
                ('expense', amount, f"Exp: {category}", eid)
            )
            self.conn.commit()
            
            self.update_balance_display()
            Snackbar(text="Saved!").open()
            
            screen.ids.amount_field.text = ""
            screen.ids.payee_field.text = ""
            
        except ValueError:
            Snackbar(text="Invalid Data").open()

    def load_report_data(self):
        screen = self.root.ids.screen_manager.get_screen("reports")
        self.cursor.execute("SELECT id, amount, company, payee, category, date FROM expenses ORDER BY id DESC LIMIT 50")
        rows = self.cursor.fetchall()
        data = []
        for r in rows:
            data.append({
                "text": f"₹{r[1]:,.2f} - {r[4]}", 
                "secondary_text": f"{r[5]} | {r[3]} ({r[2]})", 
                "id_val": r[0]
            })
        screen.ids.report_list.data = data

    def confirm_delete_expense(self, eid):
        self.del_eid = eid
        self.dialog = MDDialog(
            title="Delete?", text="Amount will be refunded.",
            buttons=[
                MDFlatButton(text="NO", on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="YES", md_bg_color=(1,0,0,1), on_release=lambda x: self.perform_delete())
            ]
        )
        self.dialog.open()

    def perform_delete(self):
        self.cursor.execute("DELETE FROM expenses WHERE id=?", (self.del_eid,))
        self.cursor.execute("DELETE FROM wallet_transactions WHERE expense_id=?", (self.del_eid,))
        self.conn.commit()
        self.dialog.dismiss()
        self.load_report_data()
        self.update_balance_display()
        Snackbar(text="Deleted").open()

    # --- MASTER DATA ---
    def load_master_data(self):
        items = self.get_master_list(self.current_master_table)
        screen = self.root.ids.screen_manager.get_screen("master_data")
        screen.ids.master_list.data = [{"text": i} for i in items]

    def show_add_master_dialog(self):
        self.master_input = MDTextField(hint_text="Name")
        self.dialog = MDDialog(
            title=f"Add {self.current_master_table}",
            type="custom",
            content_cls=self.master_input,
            buttons=[MDRaisedButton(text="SAVE", on_release=lambda x: self.save_master())]
        )
        self.dialog.open()

    def save_master(self):
        name = self.master_input.text.strip()
        if name:
            try:
                self.cursor.execute(f"INSERT INTO {self.current_master_table} (name) VALUES (?)", (name,))
                self.conn.commit()
                self.load_master_data()
                self.dialog.dismiss()
            except: Snackbar(text="Exists").open()

    def show_edit_master_dialog(self, old_name):
        self.old_master_name = old_name
        self.master_edit_input = MDTextField(text=old_name)
        self.dialog = MDDialog(
            title=f"Edit {old_name}",
            type="custom",
            content_cls=self.master_edit_input,
            buttons=[
                MDFlatButton(text="DELETE", text_color=(1,0,0,1), on_release=lambda x: self.delete_master()),
                MDRaisedButton(text="UPDATE", on_release=lambda x: self.update_master())
            ]
        )
        self.dialog.open()

    def update_master(self):
        new = self.master_edit_input.text.strip()
        if new:
            try:
                self.cursor.execute(f"UPDATE {self.current_master_table} SET name=? WHERE name=?", (new, self.old_master_name))
                self.conn.commit()
                self.load_master_data()
                self.dialog.dismiss()
            except: pass

    def delete_master(self):
        self.cursor.execute(f"DELETE FROM {self.current_master_table} WHERE name=?", (self.old_master_name,))
        self.conn.commit()
        self.load_master_data()
        self.dialog.dismiss()

if __name__ == "__main__":
    ExpenseApp().run()
