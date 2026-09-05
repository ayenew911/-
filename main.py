import sqlite3
from datetime import datetime
import flet as ft

# ==========================================
# 1. DATABASE LAYER (የመረጃ ቋት አስተዳዳሪ)
# ==========================================
class DatabaseManager:
    def __init__(self, db_name="ayenew_amharic_app.db"):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. የፖርትፎሊዮ ሰንጠረዥ
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    tech_stack TEXT NOT NULL,
                    date_created TEXT NOT NULL
                )
            """)

            # 2. የወጪዎች ሰንጠረዥ
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    date_created TEXT NOT NULL
                )
            """)

            # 3. የማስታወሻዎችና ግቦች ሰንጠረዥ
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notes_goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    type TEXT NOT NULL,
                    progress REAL DEFAULT 0.0,
                    status TEXT DEFAULT 'አክቲቭ'
                )
            """)

            # 4. የአስታዋሾች ሰንጠረዥ
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_name TEXT NOT NULL,
                    due_time TEXT NOT NULL,
                    priority TEXT DEFAULT 'መካከለኛ',
                    is_completed INTEGER DEFAULT 0
                )
            """)
            conn.commit()
            self._seed_initial_data()

    def _seed_initial_data(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM projects")
            if cursor.fetchone()[0] == 0:
                projects = [
                    (
                        "የትምህርት ቤት አውቶሜሽን ሲስተም",
                        "የተማሪዎችን መረጃ፣ ውጤትና ክፍያ በዘመናዊ መልኩ የሚያስተዳድር የዴስክቶፕ ሶፍትዌር።",
                        "Python, PySide6, SQLite",
                        datetime.now().strftime("%Y-%m-%d")
                    ),
                    (
                        "የሽያጭና እቃ መቆጣጠሪያ (ልብሱ ሞባይል)",
                        "የሞባይል ጥገና እና የእቃዎች ክምችት መቆጣጠሪያ ሶፍትዌር።",
                        "Python, Flet, SQLite",
                        datetime.now().strftime("%Y-%m-%d")
                    ),
                    (
                        "ግዕዝ ክሊኒክ ማኔጅመንት",
                        "የህክምና ታካሚዎችን እና የመድኃኒት ክምችት በኢትዮጵያ ዘመን አቆጣጠር የሚያስተዳድር።",
                        "Python, CustomTkinter, SQLite",
                        datetime.now().strftime("%Y-%m-%d")
                    )
                ]
                cursor.executemany(
                    "INSERT INTO projects (title, description, tech_stack, date_created) VALUES (?, ?, ?, ?)",
                    projects
                )
                conn.commit()

    # --- ፖርትፎሊዮ CRUD ---
    def get_projects(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projects ORDER BY id DESC")
            return cursor.fetchall()

    # --- ወጪዎች CRUD ---
    def get_expenses(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM expenses ORDER BY id DESC")
            return cursor.fetchall()

    def add_expense(self, title, amount, category, date_str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO expenses (title, amount, category, date_created) VALUES (?, ?, ?, ?)",
                (title, float(amount), category, date_str)
            )
            conn.commit()

    def delete_expense(self, expense_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
            conn.commit()

    def get_expense_stats(self):
        today = datetime.now().strftime("%Y-%m-%d")
        current_month = datetime.now().strftime("%Y-%m")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(amount) FROM expenses WHERE date_created = ?", (today,))
            daily_total = cursor.fetchone()[0] or 0.0

            cursor.execute("SELECT SUM(amount) FROM expenses WHERE date_created LIKE ?", (f"{current_month}%",))
            monthly_total = cursor.fetchone()[0] or 0.0

        return daily_total, monthly_total

    # --- ማስታወሻና ግቦች CRUD ---
    def get_notes_goals(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM notes_goals ORDER BY id DESC")
            return cursor.fetchall()

    def add_note_goal(self, title, content, item_type, progress=0.0):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO notes_goals (title, content, type, progress) VALUES (?, ?, ?, ?)",
                (title, content, item_type, progress)
            )
            conn.commit()

    def delete_note_goal(self, item_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notes_goals WHERE id = ?", (item_id,))
            conn.commit()

    def update_goal_progress(self, item_id, new_progress):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE notes_goals SET progress = ? WHERE id = ?", (new_progress, item_id))
            conn.commit()

    # --- አስታዋሾች CRUD ---
    def get_reminders(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reminders ORDER BY is_completed ASC, id DESC")
            return cursor.fetchall()

    def add_reminder(self, task_name, due_time, priority):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO reminders (task_name, due_time, priority, is_completed) VALUES (?, ?, ?, 0)",
                (task_name, due_time, priority)
            )
            conn.commit()

    def toggle_reminder(self, reminder_id, status):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE reminders SET is_completed = ? WHERE id = ?", (status, reminder_id))
            conn.commit()

    def delete_reminder(self, reminder_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
            conn.commit()


# ==========================================
# 2. UI LOGIC (የተጠቃሚ ገጽታ ማስተካከያ)
# ==========================================
class AyenewPersonalOS:
    def __init__(self, page: ft.Page):
        self.page = page
        self.db = DatabaseManager()
        
        # የገጽታ ቅንብር
        self.page.title = "አየነው - የግል ስራና እንቅስቃሴ መቆጣጠሪያ"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 0
        self.page.scroll = None

        self.selected_tab = 0
        self.init_ui()

    def init_ui(self):
        # የላይኛው ባር (AppBar)
        self.page.appbar = ft.AppBar(
            title=ft.Text("አየነው - የግል OS", weight=ft.FontWeight.BOLD, size=18),
            center_title=False,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            actions=[
                ft.IconButton(
                    icon=ft.Icons.LIGHTBULB_OUTLINE,
                    tooltip="የገጽታ ቀለም ቀይር",
                    on_click=self.toggle_theme
                )
            ]
        )

        # የታችኛው መነሻ ባር (NavigationBar)
        self.page.navigation_bar = ft.NavigationBar(
            selected_index=self.selected_tab,
            on_change=self.on_tab_change,
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.PERSON_ROUNDED, label="ፖርትፎሊዮ"),
                ft.NavigationBarDestination(icon=ft.Icons.ACCOUNT_BALANCE_WALLET, label="ወጪዎች"),
                ft.NavigationBarDestination(icon=ft.Icons.TASK_ALT, label="ማስታወሻና ግቦች"),
                ft.NavigationBarDestination(icon=ft.Icons.NOTIFICATIONS_ACTIVE, label="አስታዋሾች"),
            ]
        )

        self.main_container = ft.Container(expand=True, padding=15)
        self.page.add(self.main_container)
        self.render_view()

    def toggle_theme(self, e):
        self.page.theme_mode = (
            ft.ThemeMode.LIGHT if self.page.theme_mode == ft.ThemeMode.DARK else ft.ThemeMode.DARK
        )
        e.control.icon = (
            ft.Icons.LIGHTBULB if self.page.theme_mode == ft.ThemeMode.DARK else ft.Icons.LIGHTBULB_OUTLINE
        )
        self.page.update()

    def on_tab_change(self, e):
        self.selected_tab = e.control.selected_index
        self.render_view()

    def render_view(self):
        if self.selected_tab == 0:
            self.main_container.content = self.build_portfolio_view()
        elif self.selected_tab == 1:
            self.main_container.content = self.build_expenses_view()
        elif self.selected_tab == 2:
            self.main_container.content = self.build_notes_goals_view()
        elif self.selected_tab == 3:
            self.main_container.content = self.build_reminders_view()
        self.page.update()

    # ------------------------------------------
    # ክፍል 1: ፖርትፎሊዮ (PORTFOLIO MODULE)
    # ------------------------------------------
    def build_portfolio_view(self):
        projects = self.db.get_projects()
        project_cards = []

        for proj in projects:
            p_id, title, desc, stack, date_c = proj
            chips = [
                ft.Chip(label=ft.Text(tech.strip(), size=11), bgcolor=ft.Colors.PRIMARY_CONTAINER)
                for tech in stack.split(",")
            ]
            project_cards.append(
                ft.Card(
                    content=ft.Container(
                        padding=15,
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.CODE_ROUNDED, color=ft.Colors.PRIMARY),
                                ft.Text(title, size=16, weight=ft.FontWeight.BOLD, expand=True)
                            ]),
                            ft.Text(desc, size=13, color=ft.Colors.OUTLINE),
                            ft.Row(chips, wrap=True),
                            ft.Text(f"የተሰራበት ቀን: {date_c}", size=10, color=ft.Colors.SECONDARY)
                        ], spacing=8)
                    )
                )
            )

        return ft.ListView([
            ft.Container(
                padding=15,
                border_radius=12,
                bgcolor=ft.Colors.SURFACE_CONTAINER,
                content=ft.Column([
                    ft.Row([
                        ft.CircleAvatar(content=ft.Icon(ft.Icons.PERSON, size=35), radius=30),
                        ft.Column([
                            ft.Text("አየነው ታደሰ", size=20, weight=ft.FontWeight.BOLD),
                            ft.Text("የሶፍትዌር ባለሙያ (Software Engineer)", size=13, color=ft.Colors.PRIMARY),
                        ], spacing=2)
                    ], spacing=15),
                    ft.Divider(),
                    ft.Text(
                        "የሶፍትዌር ባለሙያ በ Python, PySide6, Flet, SQLite፣ የትምህርት ቤት አውቶሜሽን እና የሽያጭና እቃ መቆጣጠሪያ ሲስተሞች።",
                        size=13
                    ),
                    ft.Row([
                        ft.ElevatedButton(
                            "ስልክ ደውል",
                            icon=ft.Icons.PHONE,
                            on_click=lambda _: self.page.launch_url("tel:+251900000000")
                        ),
                        ft.ElevatedButton(
                            "ቴሌግራም",
                            icon=ft.Icons.SEND,
                            on_click=lambda _: self.page.launch_url("https://t.me/AyenewTadesse")
                        ),
                    ], wrap=True, alignment=ft.MainAxisAlignment.START)
                ], spacing=10)
            ),
            ft.Text("የተሰሩ ሶፍትዌሮችና ፕሮጀክቶች", size=16, weight=ft.FontWeight.BOLD),
            *project_cards
        ], spacing=15)

    # ------------------------------------------
    # ክፍል 2: የወጪ መቆጣጠሪያ (EXPENSE TRACKER)
    # ------------------------------------------
    def build_expenses_view(self):
        daily_total, monthly_total = self.db.get_expense_stats()
        expenses = self.db.get_expenses()

        expense_items = []
        for exp in expenses:
            exp_id, title, amount, cat, date_c = exp
            expense_items.append(
                ft.ListTile(
                    leading=ft.Icon(
                        ft.Icons.FASTFOOD if cat == "ምግብ" else
                        ft.Icons.DIRECTIONS_BUS if cat == "ትራንስፖርት" else
                        ft.Icons.MOVIE if cat == "መዝናኛ" else
                        ft.Icons.SHOPPING_BAG if cat == "ዕቃ/ቁሳቁስ" else ft.Icons.RECEIPT
                    ),
                    title=ft.Text(title, weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(f"{cat} • {date_c}"),
                    trailing=ft.Row([
                        ft.Text(f"{amount:.2f} ብር", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.RED_400),
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE,
                            icon_color=ft.Colors.RED_300,
                            tooltip="አጥፋ",
                            on_click=lambda _, e_id=exp_id: self.delete_expense_item(e_id)
                        )
                    ], main_axis_alignment=ft.MainAxisAlignment.END, width=130)
                )
            )

        return ft.Column([
            ft.Row([
                ft.Container(
                    expand=True,
                    padding=15,
                    bgcolor=ft.Colors.SURFACE_CONTAINER,
                    border_radius=10,
                    content=ft.Column([
                        ft.Text("የዛሬ ወጪ", size=12, color=ft.Colors.OUTLINE),
                        ft.Text(f"{daily_total:.2f} ብር", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER)
                    ])
                ),
                ft.Container(
                    expand=True,
                    padding=15,
                    bgcolor=ft.Colors.SURFACE_CONTAINER,
                    border_radius=10,
                    content=ft.Column([
                        ft.Text("የዚህ ወር ወጪ", size=12, color=ft.Colors.OUTLINE),
                        ft.Text(f"{monthly_total:.2f} ብር", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_400)
                    ])
                )
            ]),
            ft.Row([
                ft.Text("የወጪዎች ዝርዝር", size=16, weight=ft.FontWeight.BOLD, expand=True),
                ft.FloatingActionButton(
                    icon=ft.Icons.ADD,
                    tooltip="አዲስ ወጪ መዝግብ",
                    mini=True,
                    on_click=self.open_add_expense_dialog
                )
            ]),
            ft.Container(
                expand=True,
                content=ft.ListView(expense_items, spacing=5) if expense_items else ft.Text("ምንም የተመዘገበ ወጪ የለም።")
            )
        ], spacing=15)

    def delete_expense_item(self, exp_id):
        self.db.delete_expense(exp_id)
        self.render_view()

    def open_add_expense_dialog(self, e):
        title_tf = ft.TextField(label="የወጪው ርዕስ")
        amount_tf = ft.TextField(label="የብር መጠን (በብር)", keyboard_type=ft.KeyboardType.NUMBER)
        category_dd = ft.Dropdown(
            label="የወጪ ምድብ",
            options=[
                ft.dropdown.Option("ምግብ"),
                ft.dropdown.Option("ትራንስፖርት"),
                ft.dropdown.Option("መዝናኛ"),
                ft.dropdown.Option("ዕቃ/ቁሳቁስ"),
                ft.dropdown.Option("ሌላ")
            ],
            value="ምግብ"
        )

        def save_expense(ev):
            if title_tf.value and amount_tf.value:
                try:
                    amt = float(amount_tf.value)
                    date_now = datetime.now().strftime("%Y-%m-%d")
                    self.db.add_expense(title_tf.value, amt, category_dd.value, date_now)
                    self.page.close(dialog)
                    self.render_view()
                except ValueError:
                    amount_tf.error_text = "እባክዎ ትክክለኛ የቁጥር መጠን ያስገቡ"
                    amount_tf.update()

        dialog = ft.AlertDialog(
            title=ft.Text("አዲስ ወጪ መመዝገቢያ"),
            content=ft.Column([title_tf, amount_tf, category_dd], tight=True, spacing=10),
            actions=[
                ft.TextButton("ሰርዝ", on_click=lambda _: self.page.close(dialog)),
                ft.ElevatedButton("አስቀምጥ", on_click=save_expense)
            ]
        )
        self.page.open(dialog)

    # ------------------------------------------
    # ክፍል 3: ማስታወሻና ግቦች (NOTES & GOALS)
    # ------------------------------------------
    def build_notes_goals_view(self):
        items = self.db.get_notes_goals()
        cards = []

        for item in items:
            i_id, title, content, i_type, progress, status = item
            if i_type == "ግብ":
                body = ft.Column([
                    ft.Text(content, size=13),
                    ft.Row([
                        ft.ProgressBar(value=progress, expand=True, color=ft.Colors.GREEN),
                        ft.Text(f"{int(progress * 100)}%", size=12, weight=ft.FontWeight.BOLD)
                    ]),
                    ft.Row([
                        ft.IconButton(
                            ft.Icons.REMOVE_CIRCLE_OUTLINE,
                            tooltip="ቀንስ",
                            on_click=lambda _, id=i_id, p=progress: self.update_goal_p(id, max(0.0, p - 0.1))
                        ),
                        ft.IconButton(
                            ft.Icons.ADD_CIRCLE_OUTLINE,
                            tooltip="ጨምር",
                            on_click=lambda _, id=i_id, p=progress: self.update_goal_p(id, min(1.0, p + 0.1))
                        ),
                    ], alignment=ft.MainAxisAlignment.END)
                ], spacing=8)
            else:
                body = ft.Text(content, size=13)

            cards.append(
                ft.Card(
                    content=ft.Container(
                        padding=12,
                        content=ft.Column([
                            ft.Row([
                                ft.Chip(
                                    label=ft.Text(i_type, size=10),
                                    bgcolor=ft.Colors.BLUE_CONTAINER if i_type == "ማስታወሻ" else ft.Colors.GREEN_CONTAINER
                                ),
                                ft.Text(title, weight=ft.FontWeight.BOLD, size=15, expand=True),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    icon_size=18,
                                    tooltip="አጥፋ",
                                    on_click=lambda _, id=i_id: self.delete_note_goal_item(id)
                                )
                            ]),
                            body
                        ], spacing=8)
                    )
                )
            )

        return ft.Column([
            ft.Row([
                ft.Text("ማስታወሻዎች እና ግቦች", size=16, weight=ft.FontWeight.BOLD, expand=True),
                ft.FloatingActionButton(
                    icon=ft.Icons.ADD,
                    tooltip="አዲስ ማስታወሻ/ግብ ጨምር",
                    mini=True,
                    on_click=self.open_add_note_goal_dialog
                )
            ]),
            ft.Container(
                expand=True,
                content=ft.ListView(cards, spacing=10) if cards else ft.Text("ምንም የተመዘገበ ማስታወሻ ወይም ግብ የለም።")
            )
        ], spacing=15)

    def update_goal_p(self, item_id, new_p):
        self.db.update_goal_progress(item_id, round(new_p, 2))
        self.render_view()

    def delete_note_goal_item(self, item_id):
        self.db.delete_note_goal(item_id)
        self.render_view()

    def open_add_note_goal_dialog(self, e):
        title_tf = ft.TextField(label="ርዕስ")
        content_tf = ft.TextField(label="ዝርዝር ሀሳብ / ይዘት", multiline=True, min_lines=2)
        type_dd = ft.Dropdown(
            label="ዓይነት",
            options=[ft.dropdown.Option("ማስታወሻ"), ft.dropdown.Option("ግብ")],
            value="ማስታወሻ"
        )

        def save_item(ev):
            if title_tf.value and content_tf.value:
                self.db.add_note_goal(title_tf.value, content_tf.value, type_dd.value)
                self.page.close(dialog)
                self.render_view()

        dialog = ft.AlertDialog(
            title=ft.Text("አዲስ ማስታወሻ ወይም ግብ"),
            content=ft.Column([title_tf, content_tf, type_dd], tight=True, spacing=10),
            actions=[
                ft.TextButton("ሰርዝ", on_click=lambda _: self.page.close(dialog)),
                ft.ElevatedButton("አስቀምጥ", on_click=save_item)
            ]
        )
        self.page.open(dialog)

    # ------------------------------------------
    # ክፍል 4: አስታዋሾች (REMINDERS)
    # ------------------------------------------
    def build_reminders_view(self):
        reminders = self.db.get_reminders()
        reminder_widgets = []

        for r in reminders:
            r_id, task, due_time, priority, is_completed = r
            
            p_color = (
                ft.Colors.RED_400 if priority == "ከፍተኛ"
                else ft.Colors.ORANGE_400 if priority == "መካከለኛ"
                else ft.Colors.BLUE_400
            )

            reminder_widgets.append(
                ft.Container(
                    padding=10,
                    border_radius=8,
                    bgcolor=ft.Colors.SURFACE_CONTAINER,
                    content=ft.Row([
                        ft.Checkbox(
                            value=bool(is_completed),
                            on_click=lambda e, id=r_id: self.toggle_reminder_status(id, e.control.value)
                        ),
                        ft.Column([
                            ft.Text(
                                task,
                                weight=ft.FontWeight.BOLD,
                                size=14,
                                style=ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH if is_completed else None)
                            ),
                            ft.Row([
                                ft.Icon(ft.Icons.SCHEDULE, size=12, color=ft.Colors.OUTLINE),
                                ft.Text(due_time, size=11, color=ft.Colors.OUTLINE),
                                ft.Container(
                                    content=ft.Text(priority, size=10, color=ft.Colors.WHITE),
                                    bgcolor=p_color,
                                    padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                    border_radius=4
                                )
                            ], spacing=5)
                        ], expand=True, spacing=3),
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE,
                            icon_size=18,
                            tooltip="አጥፋ",
                            on_click=lambda _, id=r_id: self.delete_reminder_item(id)
                        )
                    ])
                )
            )

        return ft.Column([
            ft.Row([
                ft.Text("የታቀዱ አስታዋሾች", size=16, weight=ft.FontWeight.BOLD, expand=True),
                ft.FloatingActionButton(
                    icon=ft.Icons.ADD,
                    tooltip="አዲስ አስታዋሽ መዝግብ",
                    mini=True,
                    on_click=self.open_add_reminder_dialog
                )
            ]),
            ft.Container(
                expand=True,
                content=ft.ListView(reminder_widgets, spacing=8) if reminder_widgets else ft.Text("ምንም የታቀደ አስታዋሽ የለም።")
            )
        ], spacing=15)

    def toggle_reminder_status(self, r_id, status):
        self.db.toggle_reminder(r_id, 1 if status else 0)
        self.render_view()

    def delete_reminder_item(self, r_id):
        self.db.delete_reminder(r_id)
        self.render_view()

    def open_add_reminder_dialog(self, e):
        task_tf = ft.TextField(label="የስራው መግለጫ")
        time_tf = ft.TextField(label="የሚፈጸምበት ሰዓት/ቀን (ምሳሌ፡ 11:30 ከሰዓት)")
        priority_dd = ft.Dropdown(
            label="ቅድሚያ ደረጃ",
            options=[
                ft.dropdown.Option("ከፍተኛ"),
                ft.dropdown.Option("መካከለኛ"),
                ft.dropdown.Option("ዝቅተኛ")
            ],
            value="መካከለኛ"
        )

        def save_reminder(ev):
            if task_tf.value and time_tf.value:
                self.db.add_reminder(task_tf.value, time_tf.value, priority_dd.value)
                self.page.close(dialog)
                self.render_view()

        dialog = ft.AlertDialog(
            title=ft.Text("አዲስ አስታዋሽ መጨመሪያ"),
            content=ft.Column([task_tf, time_tf, priority_dd], tight=True, spacing=10),
            actions=[
                ft.TextButton("ሰርዝ", on_click=lambda _: self.page.close(dialog)),
                ft.ElevatedButton("አስቀምጥ", on_click=save_reminder)
            ]
        )
        self.page.open(dialog)


def main(page: ft.Page):
    AyenewPersonalOS(page)

if __name__ == "__main__":
    ft.app(target=main)
