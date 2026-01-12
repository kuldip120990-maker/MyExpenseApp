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
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from kivy.metrics import dp
from datetime import datetime
import sqlite3
import os
import traceback

# --- KV LAYOUT ---
KV = '''
<ContentNavigationDrawer>:
    MDScrollView:
        MDList:
            OneLineIconListItem:
                text: "Dashboard"
                on_press:
                    root.nav_drawer.set_state("close")
                    root.screen_manager.current = "dashboard"
                IconLeftWidget:
                    icon: "view-dashboard"

            OneLineIconListItem:
                text: "Reports"
                on_press:
                    root.nav_drawer.set_state("close")
                    app.load_report_data()
                    root.screen_manager.current = "reports"
                IconLeftWidget:
                    icon: "file-document"

            OneLineIconListItem:
                text: "Wallet History"
                on_press:
                    root.nav_drawer.set_state("close")
                    app.load_wallet_history()
                    root.screen_manager.current = "wallet_hist"
                IconLeftWidget:
                    icon: "wallet"

            MDLabel:
                text: "Master Data"
                font_style: "Caption"
                size_hint_y: None
                height: self.texture_size[1]
                padding: dp(15), dp(10)

            OneLineIconListItem:
                text: "Manage Companies"
                # FIX: Passing screen_manager directly to avoid crash
                on_press:
                    root.nav_drawer.set_state("close")
                    app.open_master_screen("companies", root.screen_manager)
                IconLeftWidget:
                    icon: "domain"

            OneLineIconListItem:
                text: "Manage Payees"
                on_press:
                    root.nav_drawer.set_state("close")
                    app.open_master_screen("payees", root.screen_manager)
                IconLeftWidget:
                    icon: "account-cash"

            OneLineIconListItem:
                text: "Manage Categories"
                on_press:
                    root.nav_drawer.set_state("close")
                    app.open_master_screen("categories", root.screen_manager)
                IconLeftWidget:
                    icon: "shape"

<ExpenseListItem>:
    IconRightWidget:
        icon: "delete"
        theme_text_color: "Custom"
        text_color: 1, 0, 0, 1
        on_release: root.delete_item(root)

<MasterListItem>:
    IconRightWidget:
        icon: "pencil"
        on_release: root.edit_item(root)

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

                                # FIX: Added Vertical Space
                                Widget:
                                    size_hint_y: None
                                    height: dp(20)

                                # FIX: Centered Buttons with spacing
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
                        left_action_items: [["arrow-left", lambda x: app.go_back_home()]]
                    
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
                        left_action_items: [["arrow-left", lambda x: app.go_back_home()]]
                    
                    MDScrollView:
                        MDList:
                            id: wallet_list

        MDNavigationDrawer:
            id: nav_drawer
            ContentNavigationDrawer:
                nav_drawer: nav_drawer
                screen_manager: screen_manager
'''

class ContentNavigationDrawer(MDBoxLayout):
    nav_drawer = ObjectProperty()
    screen_manager = ObjectProperty()

class ExpenseListItem(TwoLineAvatarIconListItem):
    id_val = NumericProperty(0)
    
    def delete_item(self, instance):
        app = MDApp.get_running_app()
        app.delete_expense_confirm(self.id_val)

class MasterListItem(OneLineIconListItem):
    def edit_item(self, instance):
        app = MDApp.get_running_app()
        app.show_edit_master_dialog(self.text)

class ExpenseApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        
        try:
            # Database setup
            self.db_name = os.path.join(self.user_data_dir, 'expenses_mobile_v6.db')
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            self.create_tables()
            
            self.current_master_table = "" 
            self.sm = None # Placeholder for ScreenManager

            return Builder.load_string(KV)
        except Exception as e:
            error_msg = traceback.format_exc()
            return MDLabel(text=f"CRASH ERROR:\n{error_msg}", halign="center")

    def on_start(self):
        try:
            # FIX: Securely finding screen_manager
            if self.root:
                self.sm = self.root.ids.screen_manager
                
            # Default Data
            if not self.get_master_list('categories'):
                for n in ['Travel', 'Food', 'Office', 'Salary']:
                    self.cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (n,))
                self.conn.commit()
                
            self.update_balance_display()
            today = datetime.now()
            if self.sm:
                screen = self.sm.get_screen("dashboard")
                screen.ids.date_field.text = today.strftime("%Y-%m-%d")
        except Exception:
            pass 

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS companies (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS payees (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS categories (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL)''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                date TEXT, month TEXT, year INTEGER,
                company TEXT, payee TEXT, category TEXT, amount REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS wallet_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                type TEXT NOT NULL, amount REAL NOT NULL, remark TEXT,
                expense_id INTEGER, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def get_master_list(self, table):
        try:
            self.cursor.execute(f"SELECT name FROM {table}")
            return [row[0] for row in self.cursor.fetchall()]
        except: return []

    def go_back_home(self):
        if self.sm:
            self.sm.current = "dashboard"

    # --- WALLET LOGIC ---
    def update_balance_display(self):
        try:
            self.cursor.execute("SELECT SUM(CASE WHEN type = 'add' THEN amount ELSE -amount END) FROM wallet_transactions")
            res = self.cursor.fetchone()[0]
            bal = res if res else 0.0
            
            # FIX: Use stored self.sm to avoid crash
            if self.sm:
                screen = self.sm.get_screen("dashboard")
                screen.ids.wallet_bal_label.text = f"₹{bal:,.2f}"
        except: pass

    def show_wallet_dialog(self, trans_type):
        self.trans_type_temp = trans_type
        title = "Add Funds" if trans_type == 'add' else "Withdraw Funds"
        
        content = MDBoxLayout(orientation="vertical", spacing="12dp", size_hint_y=None, height="100dp")
        self.w_amount = MDTextField(hint_text="Amount", input_filter="float")
        self.w_remark = MDTextField(hint_text="Remark (Optional)")
        content.add_widget(self.w_amount)
        content.add_widget(self.w_remark)
        
        self.dialog = MDDialog(
            title=title,
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="CONFIRM", on_release=self.process_wallet_trans)
            ],
        )
        self.dialog.open()

    def process_wallet_trans(self, instance):
        try:
            amt_text = self.w_amount.text
            if not amt_text:
                raise ValueError
                
            amt = float(amt_text)
            if amt <= 0: raise ValueError
            
            remark_text = self.w_remark.text if self.w_remark.text else ""
            
            self.cursor.execute('INSERT INTO wallet_transactions (type, amount, remark) VALUES (?, ?, ?)', 
                               (self.trans_type_temp, amt, remark_text))
            self.conn.commit()
            
            self.dialog.dismiss()
            self.update_balance_display()
            Snackbar(text="Transaction Successful").open()
        except ValueError:
            Snackbar(text="Invalid Amount").open()
        except Exception as e:
            # Catch other errors to prevent crash
            Snackbar(text="Error occurred").open()

    # --- DATA ENTRY ---
    def show_date_picker(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_date_save)
        date_dialog.open()

    def on_date_save(self, instance, value, date_range):
        if self.sm:
            screen = self.sm.get_screen("dashboard")
            screen.ids.date_field.text = str(value)

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
        if not self.sm: return
        screen = self.sm.get_screen("dashboard")
        
        date = screen.ids.date_field.text
        company = screen.ids.company_field.text
        payee = screen.ids.payee_field.text
        category = screen.ids.category_field.text
        amount_str = screen.ids.amount_field.text

        if not amount_str or not company or not payee:
            Snackbar(text="Please fill all fields").open()
            return

        try:
            amount = float(amount_str)
            dt_obj = datetime.strptime(date, "%Y-%m-%d")
            month_name = dt_obj.strftime("%B")
            year_num = dt_obj.year
            
            # Insert Expense
            self.cursor.execute(
                "INSERT INTO expenses (date, month, year, company, payee, category, amount) VALUES (?,?,?,?,?,?,?)",
                (date, month_name, year_num, company, payee, category, amount)
            )
            eid = self.cursor.lastrowid
            
            # Insert Wallet Transaction
            self.cursor.execute(
                "INSERT INTO wallet_transactions (type, amount, remark, expense_id) VALUES (?,?,?,?)",
                ('expense', amount, f"Exp: {category}", eid)
            )
            self.conn.commit()
            
            self.update_balance_display()
            Snackbar(text="Saved Successfully").open()
            
            # Clear fields
            screen.ids.amount_field.text = ""
            screen.ids.payee_field.text = ""
            
        except ValueError:
            Snackbar(text="Invalid Data format").open()

    # --- REPORTS ---
    def load_report_data(self):
        if not self.sm: return
        screen = self.sm.get_screen("reports")
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

    def delete_expense_confirm(self, eid):
        self.del_eid = eid
        self.dialog = MDDialog(
            title="Delete Expense?",
            text="This will also refund the amount to wallet.",
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="DELETE", md_bg_color=(1,0,0,1), on_release=self.perform_delete)
            ]
        )
        self.dialog.open()

    def perform_delete(self, instance):
        self.cursor.execute("DELETE FROM expenses WHERE id=?", (self.del_eid,))
        self.cursor.execute("DELETE FROM wallet_transactions WHERE expense_id=?", (self.del_eid,))
        self.conn.commit()
        self.dialog.dismiss()
        self.load_report_data()
        self.update_balance_display()
        Snackbar(text="Deleted").open()

    # --- MASTER DATA MANAGEMENT ---
    # FIX: Accepting manager argument to avoid crash
    def open_master_screen(self, table_name, manager=None):
        self.current_master_table = table_name
        
        # Use passed manager, or fallback to self.sm
        target_sm = manager if manager else self.sm
        
        if target_sm:
            screen = target_sm.get_screen("master_data")
            screen.ids.master_toolbar.title = f"Manage {table_name.capitalize()}"
            self.load_master_data(target_sm)
            target_sm.current = "master_data"

    def load_master_data(self, manager=None):
        target_sm = manager if manager else self.sm
        if not target_sm: return
        
        items = self.get_master_list(self.current_master_table)
        screen = target_sm.get_screen("master_data")
        screen.ids.master_list.data = [{"text": i} for i in items]

    def show_add_master_dialog(self):
        content = MDBoxLayout(orientation="vertical", size_hint_y=None, height="50dp")
        self.master_input = MDTextField(hint_text="Enter Name")
        content.add_widget(self.master_input)
        
        self.dialog = MDDialog(
            title=f"Add to {self.current_master_table}",
            type="custom",
            content_cls=content,
            buttons=[
                MDRaisedButton(text="SAVE", on_release=self.save_master_data)
            ]
        )
        self.dialog.open()

    def save_master_data(self, instance):
        name = self.master_input.text.strip()
        if name:
            try:
                self.cursor.execute(f"INSERT INTO {self.current_master_table} (name) VALUES (?)", (name,))
                self.conn.commit()
                self.load_master_data()
                self.dialog.dismiss()
            except:
                Snackbar(text="Already Exists").open()

    def show_edit_master_dialog(self, old_name):
        self.old_master_name = old_name
        content = MDBoxLayout(orientation="vertical", size_hint_y=None, height="100dp", spacing="10dp")
        self.master_edit_input = MDTextField(text=old_name)
        content.add_widget(self.master_edit_input)
        
        self.dialog = MDDialog(
            title=f"Edit/Delete {old_name}",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="DELETE", text_color=(1,0,0,1), on_release=self.delete_master_data),
                MDRaisedButton(text="UPDATE", on_release=self.update_master_data)
            ]
        )
        self.dialog.open()

    def update_master_data(self, instance):
        new_name = self.master_edit_input.text.strip()
        if new_name:
            try:
                self.cursor.execute(f"UPDATE {self.current_master_table} SET name=? WHERE name=?", (new_name, self.old_master_name))
                self.conn.commit()
                self.load_master_data()
                self.dialog.dismiss()
            except:
                Snackbar(text="Error or Exists").open()

    def delete_master_data(self, instance):
        self.cursor.execute(f"DELETE FROM {self.current_master_table} WHERE name=?", (self.old_master_name,))
        self.conn.commit()
        self.load_master_data()
        self.dialog.dismiss()

    # --- WALLET HISTORY LIST ---
    def load_wallet_history(self):
        if not self.sm: return
        screen = self.sm.get_screen("wallet_hist")
        screen.ids.wallet_list.clear_widgets()
        
        self.cursor.execute("SELECT type, amount, remark, created_at FROM wallet_transactions ORDER BY id DESC LIMIT 50")
        rows = self.cursor.fetchall()
        
        for r in rows:
            icon = "arrow-down-bold" if r[0] == 'expense' or r[0] == 'remove' else "arrow-up-bold"
            color = (1, 0, 0, 1) if r[0] == 'expense' or r[0] == 'remove' else (0, 0.7, 0, 1)
            
            item = TwoLineAvatarIconListItem(
                text=f"₹{r[1]:,.2f} ({r[0].upper()})",
                secondary_text=f"{r[2]} | {r[3]}"
            )
            
            from kivymd.uix.list import IconLeftWidget
            ic = IconLeftWidget(icon=icon)
            ic.theme_text_color = "Custom"
            ic.text_color = color
            item.add_widget(ic)
            
            screen.ids.wallet_list.add_widget(item)

if __name__ == "__main__":
    ExpenseApp().run()
