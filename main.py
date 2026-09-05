import flet as ft
import sqlite3
from datetime import datetime
import json

# ==========================================
# 1. DATABASE INITIALIZATION & SEEDING
# ==========================================
DB_NAME = "life_os.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Daily Tasks Table (የእለት እንቅስቃሴ)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            steps TEXT,
            priority TEXT DEFAULT 'መካከለኛ',
            is_completed INTEGER DEFAULT 0,
            created_at TEXT
        )
    ''')
    
    # 2. Financial Transactions Table (የገንዘብ እንቅስቃሴ)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            trans_type TEXT NOT NULL, -- 'ገቢ' or 'ወጪ'
            category TEXT NOT NULL,
            trans_date TEXT
        )
    ''')
    
    # 3. Contacts Table (የግንኙነት መዝገብ)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT,
            phone TEXT,
            notes TEXT,
            last_contact TEXT
        )
    ''')
    
    # 4. Projects Table (የፕሮጀክት ማኔጀር)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'በመሰራት ላይ',
            progress INTEGER DEFAULT 0
        )
    ''')
    
    # 5. Portfolio Table (የሶፍትዌር ኤግዚቢሽን)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            tech_stack TEXT NOT NULL,
            price_estimate TEXT
        )
    ''')
    
    # Seed default portfolio items if empty
    cursor.execute("SELECT COUNT(*) FROM portfolio")
    if cursor.fetchone()[0] == 0:
        default_portfolio = [
            (
                "EthioDoc - የሰነዶች ማኔጅመንት",
                "ዴስክቶፕ ሲስተም (PySide6)",
                "የተለያዩ ፋይሎችን እና ኦፊሴላዊ ሰነዶችን በOCR ቴክኖሎጂ ታግዞ በደመና እና በኮምፒውተር ላይ የሚያደራጅ ሶፍትዌር።",
                "Python, PySide6, SQLite, Tesseract OCR",
                "25,000 ብር"
            ),
            (
                "ልብሱ ሞባይል ጥገና - የዕቃ መቆጣጠሪያ",
                "የንግድ ሲስተም (CustomTkinter)",
                "የሞባይል ጥገና ሱቆች ዕቃዎችን፣ የጥገና ቀጠሮዎችን እና የገንዘብ ሂሳብን በቀላሉ የሚያስተዳድሩበት።",
                "Python, CustomTkinter, SQLite",
                "18,000 ብር"
            ),
            (
                "ግዕዝ ክሊኒክ - የሕክምና ማኔጅመንት",
                "የጤና ሲስተም (CustomTkinter)",
                "የታካሚዎች መዝገብ፣ የመድኃኒት መደብር እና የኢትዮጵያ ዘመን አቆጣጠርን ያካተተ የክሊኒክ ሶፍትዌር።",
                "Python, CustomTkinter, SQLite",
                "35,000 ብር"
            ),
            (
                "NetGuard - የኔትወርክ ሴኩሪቲ ቱል",
                "የደህንነት መሳሪያ (Python CLI/GUI)",
                "በአካባቢ ኔትወርክ ላይ ያሉ ያልተፈቀዱ መሳሪያዎችን የሚቆጣጠር እና የትራፊክ ደህንነት የሚያረጋግጥ።",
                "Python, Scapy, Socket Programming",
                "20,000 ብር"
            )
        ]
        cursor.executemany('''
            INSERT INTO portfolio (title, category, description, tech_stack, price_estimate)
            VALUES (?, ?, ?, ?, ?)
        ''', default_portfolio)
        
    conn.commit()
    conn.close()

init_db()

# ==========================================
# 2. MAIN APPLICATION LOGIC
# ==========================================
def main(page: ft.Page):
    page.title = "Personal LifeOS & Portfolio"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 10
    page.scroll = ft.ScrollMode.ADAPTIVE

    # Database Helpers
    def run_query(query, params=(), fetchall=False, fetchone=False):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, params)
        data = None
        if fetchall:
            data = cursor.fetchall()
        elif fetchone:
            data = cursor.fetchone()
        conn.commit()
        conn.close()
        return data

    # Notification SnackBar
    def show_msg(text):
        page.snack_bar = ft.SnackBar(ft.Text(text, font_family="Ethics"))
        page.snack_bar.open = True
        page.update()

    # ------------------------------------------
    # TAB 1: 📅 የእለት እንቅስቃሴ (Daily Life OS)
    # ------------------------------------------
    def build_daily_view():
        tasks_list = ft.Column(spacing=10)

        def load_tasks():
            tasks_list.controls.clear()
            rows = run_query("SELECT id, title, steps, priority, is_completed FROM tasks ORDER BY id DESC", fetchall=True)
            for r in rows:
                task_id, title, steps, priority, is_completed = r
                
                def toggle_complete(e, tid=task_id, val=is_completed):
                    new_val = 0 if val == 1 else 1
                    run_query("UPDATE tasks SET is_completed = ? WHERE id = ?", (new_val, tid))
                    load_tasks()

                p_color = ft.Colors.RED_400 if priority == "ከፍተኛ" else (ft.Colors.ORANGE_400 if priority == "መካከለኛ" else ft.Colors.GREEN_400)
                
                tasks_list.controls.append(
                    ft.Card(
                        content=ft.Container(
                            padding=12,
                            content=ft.Column([
                                ft.Row([
                                    ft.Checkbox(value=bool(is_completed), on_change=toggle_complete),
                                    ft.Text(title, size=16, weight=ft.FontWeight.BOLD, 
                                            style=ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH if is_completed else None)),
                                    ft.Container(
                                        content=ft.Text(priority, size=12, color=ft.Colors.WHITE),
                                        bgcolor=p_color,
                                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                        border_radius=5
                                    )
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ft.Text(f"የአፈጻጸም መመሪያ፡ {steps}", size=13, color=ft.Colors.GREY_400) if steps else ft.Container()
                            ])
                        )
                    )
                )
            page.update()

        title_input = ft.TextField(label="የተግባሩ ስም", border_radius=8)
        steps_input = ft.TextField(label="ደረጃ በደረጃ የመፈጸሚያ መመሪያ", multiline=True, border_radius=8)
        priority_dropdown = ft.Dropdown(
            label="አስፈላጊነት",
            value="መካከለኛ",
            options=[
                ft.dropdown.Option("ከፍተኛ"),
                ft.dropdown.Option("መካከለኛ"),
                ft.dropdown.Option("ዝቅተኛ")
            ],
            border_radius=8
        )

        def add_task(e):
            if not title_input.value:
                show_msg("እባክዎን የተግባሩን ስም ያስገቡ!")
                return
            run_query("INSERT INTO tasks (title, steps, priority, created_at) VALUES (?, ?, ?, ?)",
                      (title_input.value, steps_input.value, priority_dropdown.value, datetime.now().strftime("%Y-%m-%d")))
            title_input.value = ""
            steps_input.value = ""
            add_dialog.open = False
            show_msg("ተግባሩ በትክክል ተመዝግቧል!")
            load_tasks()

        add_dialog = ft.AlertDialog(
            title=ft.Text("አዲስ የእለት ተግባር ጨምር"),
            content=ft.Column([title_input, steps_input, priority_dropdown], height=240, spacing=10),
            actions=[
                ft.TextButton("ሰርዝ", on_click=lambda e: setattr(add_dialog, "open", False) or page.update()),
                ft.ElevatedButton("መዝግብ", on_click=add_task, bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE)
            ]
        )

        def open_add_dialog(e):
            page.dialog = add_dialog
            add_dialog.open = True
            page.update()

        load_tasks()

        return ft.Container(
            padding=10,
            content=ft.Column([
                ft.Row([
                    ft.Text("📅 የእለት እንቅስቃሴ መሪ", size=20, weight=ft.FontWeight.BOLD),
                    ft.IconButton(ft.Icons.ADD_CIRCLE, icon_color=ft.Colors.BLUE_400, icon_size=32, on_click=open_add_dialog)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(),
                tasks_list
            ])
        )

    # ------------------------------------------
    # TAB 2: 💰 የገንዘብ እንቅስቃሴ (Expense Tracker)
    # ------------------------------------------
    def build_expense_view():
        trans_list = ft.Column(spacing=8)
        total_income_text = ft.Text("0.00 ብር", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)
        total_expense_text = ft.Text("0.00 ብር", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_400)
        balance_text = ft.Text("0.00 ብር", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_300)

        def load_expenses():
            trans_list.controls.clear()
            rows = run_query("SELECT id, title, amount, trans_type, category, trans_date FROM transactions ORDER BY id DESC", fetchall=True)
            
            inc = 0.0
            exp = 0.0
            for r in rows:
                tid, title, amount, t_type, cat, t_date = r
                if t_type == "ገቢ":
                    inc += amount
                else:
                    exp += amount
                    
                is_inc = t_type == "ገቢ"
                trans_list.controls.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.ARROW_DOWNWARD if is_inc else ft.Icons.ARROW_UPWARD, 
                                        color=ft.Colors.GREEN_400 if is_inc else ft.Colors.RED_400),
                        title=ft.Text(title, weight=ft.FontWeight.BOLD),
                        subtitle=ft.Text(f"{cat} | {t_date}"),
                        trailing=ft.Text(f"{'+' if is_inc else '-'}{amount:,.2f} ብር", 
                                         color=ft.Colors.GREEN_400 if is_inc else ft.Colors.RED_400, weight=ft.FontWeight.BOLD)
                    )
                )
            
            total_income_text.value = f"{inc:,.2f} ብር"
            total_expense_text.value = f"{exp:,.2f} ብር"
            balance_text.value = f"{(inc - exp):,.2f} ብር"
            page.update()

        t_title = ft.TextField(label="የገንዘብ እንቅስቃሴው መግለጫ", border_radius=8)
        t_amount = ft.TextField(label="የገንዘብ መጠን (በብር)", keyboard_type=ft.KeyboardType.NUMBER, border_radius=8)
        t_type = ft.Dropdown(
            label="አይነት",
            value="ወጪ",
            options=[ft.dropdown.Option("ገቢ"), ft.dropdown.Option("ወጪ")],
            border_radius=8
        )
        t_cat = ft.Dropdown(
            label="መድብ",
            value="የግል ወጪ",
            options=[
                ft.dropdown.Option("የግል ወጪ"),
                ft.dropdown.Option("የሶፍትዌር መሳሪያዎች"),
                ft.dropdown.Option("የፕሮጀክት ገቢ"),
                ft.dropdown.Option("ሌላ")
            ],
            border_radius=8
        )

        def save_transaction(e):
            if not t_title.value or not t_amount.value:
                show_msg("እባክዎን ሁሉንም መስኮች በትክክል ይሙሉ!")
                return
            try:
                amt = float(t_amount.value)
            except ValueError:
                show_msg("እባክዎን ትክክለኛ የገንዘብ ቁጥር ያስገቡ!")
                return

            run_query("INSERT INTO transactions (title, amount, trans_type, category, trans_date) VALUES (?, ?, ?, ?, ?)",
                      (t_title.value, amt, t_type.value, t_cat.value, datetime.now().strftime("%Y-%m-%d")))
            t_title.value = ""
            t_amount.value = ""
            add_trans_dialog.open = False
            show_msg("የገንዘብ እንቅስቃሴው ተመዝግቧል!")
            load_expenses()

        add_trans_dialog = ft.AlertDialog(
            title=ft.Text("አዲስ የገንዘብ መዝገብ"),
            content=ft.Column([t_title, t_amount, t_type, t_cat], height=260, spacing=10),
            actions=[
                ft.TextButton("ሰርዝ", on_click=lambda e: setattr(add_trans_dialog, "open", False) or page.update()),
                ft.ElevatedButton("መዝግብ", on_click=save_transaction, bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE)
            ]
        )

        load_expenses()

        return ft.Container(
            padding=10,
            content=ft.Column([
                ft.Row([
                    ft.Text("💰 የገንዘብ እንቅስቃሴ", size=20, weight=ft.FontWeight.BOLD),
                    ft.IconButton(ft.Icons.ADD_CARD, icon_color=ft.Colors.GREEN_400, icon_size=32, 
                                  on_click=lambda e: setattr(page, "dialog", add_trans_dialog) or setattr(add_trans_dialog, "open", True) or page.update())
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Card(
                    content=ft.Container(
                        padding=15,
                        content=ft.Column([
                            ft.Row([ft.Text("ጠቅላላ ገቢ፡"), total_income_text], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Row([ft.Text("ጠቅላላ ወጪ፡"), total_expense_text], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Divider(),
                            ft.Row([ft.Text("ቀሪ ሂሳብ፡", weight=ft.FontWeight.BOLD), balance_text], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                        ])
                    )
                ),
                ft.Text("የቅርብ ጊዜ እንቅስቃሴዎች", size=16, weight=ft.FontWeight.BOLD),
                trans_list
            ])
        )

    # ------------------------------------------
    # TAB 3: 👥 የግንኙነት መዝገብ (Relationship CRM)
    # ------------------------------------------
    def build_contacts_view():
        contacts_list = ft.Column(spacing=10)

        def load_contacts():
            contacts_list.controls.clear()
            rows = run_query("SELECT id, name, role, phone, notes, last_contact FROM contacts ORDER BY id DESC", fetchall=True)
            for r in rows:
                cid, name, role, phone, notes, last_contact = r
                contacts_list.controls.append(
                    ft.Card(
                        content=ft.ListTile(
                            leading=ft.Icon(ft.Icons.PERSON, color=ft.Colors.BLUE_300),
                            title=ft.Text(name, weight=ft.FontWeight.BOLD),
                            subtitle=ft.Text(f"ድርሻ፡ {role} | ስልክ፡ {phone}\nማስታወሻ፡ {notes}"),
                            trailing=ft.Text(last_contact, size=11, color=ft.Colors.GREY_400)
                        )
                    )
                )
            page.update()

        c_name = ft.TextField(label="ሙሉ ስም", border_radius=8)
        c_role = ft.Dropdown(
            label="የግንኙነት አይነት",
            value="ደንበኛ",
            options=[
                ft.dropdown.Option("ደንበኛ"),
                ft.dropdown.Option("የስራ ባልደረባ"),
                ft.dropdown.Option("የግል ወዳጅ"),
                ft.dropdown.Option("አማካሪ")
            ],
            border_radius=8
        )
        c_phone = ft.TextField(label="ስልክ ቁጥር", keyboard_type=ft.KeyboardType.PHONE, border_radius=8)
        c_notes = ft.TextField(label="ተጨማሪ ማስታወሻ/ውይይት", multiline=True, border_radius=8)

        def save_contact(e):
            if not c_name.value:
                show_msg("እባክዎን ስም ያስገቡ!")
                return
            run_query("INSERT INTO contacts (name, role, phone, notes, last_contact) VALUES (?, ?, ?, ?, ?)",
                      (c_name.value, c_role.value, c_phone.value, c_notes.value, datetime.now().strftime("%Y-%m-%d")))
            c_name.value = ""
            c_phone.value = ""
            c_notes.value = ""
            add_contact_dialog.open = False
            show_msg("የግንኙነት መረጃው ተመዝግቧል!")
            load_contacts()

        add_contact_dialog = ft.AlertDialog(
            title=ft.Text("አዲስ ሰው መዝግብ"),
            content=ft.Column([c_name, c_role, c_phone, c_notes], height=270, spacing=10),
            actions=[
                ft.TextButton("ሰርዝ", on_click=lambda e: setattr(add_contact_dialog, "open", False) or page.update()),
                ft.ElevatedButton("መዝግብ", on_click=save_contact, bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE)
            ]
        )

        load_contacts()

        return ft.Container(
            padding=10,
            content=ft.Column([
                ft.Row([
                    ft.Text("👥 የግንኙነት መዝገብ", size=20, weight=ft.FontWeight.BOLD),
                    ft.IconButton(ft.Icons.PERSON_ADD, icon_color=ft.Colors.BLUE_400, icon_size=32,
                                  on_click=lambda e: setattr(page, "dialog", add_contact_dialog) or setattr(add_contact_dialog, "open", True) or page.update())
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(),
                contacts_list
            ])
        )

    # ------------------------------------------
    # TAB 4: 💻 የፕሮጀክት ማኔጀር (Work & Dev Hub)
    # ------------------------------------------
    def build_projects_view():
        projects_list = ft.Column(spacing=10)

        def load_projects():
            projects_list.controls.clear()
            rows = run_query("SELECT id, title, description, status, progress FROM projects ORDER BY id DESC", fetchall=True)
            for r in rows:
                pid, title, desc, status, progress = r
                
                def update_status(e, project_id=pid):
                    run_query("UPDATE projects SET status = ? WHERE id = ?", (e.control.value, project_id))
                    show_msg("የፕሮጀክት ደረጃ ተቀይሯል!")

                projects_list.controls.append(
                    ft.Card(
                        content=ft.Container(
                            padding=12,
                            content=ft.Column([
                                ft.Text(title, size=16, weight=ft.FontWeight.BOLD),
                                ft.Text(desc, size=13, color=ft.Colors.GREY_300),
                                ft.Row([
                                    ft.Text("ደረጃ፡", size=12),
                                    ft.Dropdown(
                                        value=status,
                                        options=[
                                            ft.dropdown.Option("በእቅድ ላይ"),
                                            ft.dropdown.Option("በመሰራት ላይ"),
                                            ft.dropdown.Option("ተጠናቋል")
                                        ],
                                        on_change=update_status,
                                        width=150
                                    )
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                            ])
                        )
                    )
                )
            page.update()

        p_title = ft.TextField(label="የፕሮጀክቱ ስም", border_radius=8)
        p_desc = ft.TextField(label="የስራው ዝርዝር መግለጫ", multiline=True, border_radius=8)

        def save_project(e):
            if not p_title.value:
                show_msg("እባክዎን የፕሮጀክት ስም ያስገቡ!")
                return
            run_query("INSERT INTO projects (title, description) VALUES (?, ?)", (p_title.value, p_desc.value))
            p_title.value = ""
            p_desc.value = ""
            add_proj_dialog.open = False
            show_msg("ፕሮጀክቱ ተመዝግቧል!")
            load_projects()

        add_proj_dialog = ft.AlertDialog(
            title=ft.Text("አዲስ ፕሮጀክት መዝግብ"),
            content=ft.Column([p_title, p_desc], height=180, spacing=10),
            actions=[
                ft.TextButton("ሰርዝ", on_click=lambda e: setattr(add_proj_dialog, "open", False) or page.update()),
                ft.ElevatedButton("መዝግብ", on_click=save_project, bgcolor=ft.Colors.PURPLE_600, color=ft.Colors.WHITE)
            ]
        )

        load_projects()

        return ft.Container(
            padding=10,
            content=ft.Column([
                ft.Row([
                    ft.Text("💻 የፕሮጀክት ማኔጀር", size=20, weight=ft.FontWeight.BOLD),
                    ft.IconButton(ft.Icons.ADD_TASK, icon_color=ft.Colors.PURPLE_400, icon_size=32,
                                  on_click=lambda e: setattr(page, "dialog", add_proj_dialog) or setattr(add_proj_dialog, "open", True) or page.update())
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(),
                projects_list
            ])
        )

    # ------------------------------------------
    # TAB 5: 🚀 የሶፍትዌር ኤግዚቢሽን (Portfolio Showcase)
    # ------------------------------------------
    def build_portfolio_view():
        portfolio_list = ft.Column(spacing=12)

        def send_inquiry(item_title):
            inquiry_dialog = ft.AlertDialog(
                title=ft.Text(f"የግዢ/የስራ ጥያቄ፡ {item_title}"),
                content=ft.Column([
                    ft.Text("የእርስዎን ስም እና ስልክ ያስገቡ፤ በቅርቡ እንገናኛለን።"),
                    ft.TextField(label="ስምዎ", border_radius=8),
                    ft.TextField(label="ስልክ ቁጥር", keyboard_type=ft.KeyboardType.PHONE, border_radius=8)
                ], height=180, spacing=10),
                actions=[
                    ft.ElevatedButton("ላክ", on_click=lambda e: (setattr(inquiry_dialog, "open", False), show_msg("ጥያቄዎ ተልኳል! እናመሰግናለን።"), page.update()), bgcolor=ft.Colors.ORANGE_600, color=ft.Colors.WHITE)
                ]
            )
            page.dialog = inquiry_dialog
            inquiry_dialog.open = True
            page.update()

        def load_portfolio():
            portfolio_list.controls.clear()
            rows = run_query("SELECT id, title, category, description, tech_stack, price_estimate FROM portfolio", fetchall=True)
            for r in rows:
                pid, title, category, description, tech_stack, price_estimate = r
                portfolio_list.controls.append(
                    ft.Card(
                        content=ft.Container(
                            padding=15,
                            content=ft.Column([
                                ft.Row([
                                    ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_300),
                                    ft.Container(
                                        content=ft.Text(price_estimate, size=12, color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD),
                                        bgcolor=ft.Colors.AMBER_400,
                                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                        border_radius=5
                                    )
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ft.Text(f"ዘርፍ፡ {category}", size=12, color=ft.Colors.GREY_400),
                                ft.Text(description, size=13),
                                ft.Text(f"ቴክኖሎጂ፡ {tech_stack}", size=12, color=ft.Colors.BLUE_200, weight=ft.FontWeight.W_500),
                                ft.ElevatedButton(
                                    "የሶፍትዌር ግዢ / የስራ ጥያቄ ላክ",
                                    icon=ft.Icons.SHOPPING_BAG,
                                    bgcolor=ft.Colors.ORANGE_700,
                                    color=ft.Colors.WHITE,
                                    on_click=lambda e, t=title: send_inquiry(t)
                                )
                            ], spacing=8)
                        )
                    )
                )
            page.update()

        load_portfolio()

        return ft.Container(
            padding=10,
            content=ft.Column([
                ft.Text("🚀 የሶፍትዌር ኤግዚቢሽን & ፖርትፎሊዮ", size=20, weight=ft.FontWeight.BOLD),
                ft.Text("የተሰሩ የሶፍትዌር ምርቶች እና አገልግሎቶች ማሳያ", size=13, color=ft.Colors.GREY_400),
                ft.Divider(),
                portfolio_list
            ])
        )

    # ==========================================
    # 3. NAVIGATION & VIEW SWITCHER
    # ==========================================
    views = [
        build_daily_view(),
        build_expense_view(),
        build_contacts_view(),
        build_projects_view(),
        build_portfolio_view()
    ]

    body_container = ft.Container(content=views[0], expand=True)

    def on_nav_change(e):
        idx = e.control.selected_index
        body_container.content = views[idx]
        page.update()

    page.navigation_bar = ft.NavigationBar(
        selected_index=0,
        on_change=on_nav_change,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.TODAY, label="እንቅስቃሴ"),
            ft.NavigationBarDestination(icon=ft.Icons.ACCOUNT_BALANCE_WALLET, label="ገንዘብ"),
            ft.NavigationBarDestination(icon=ft.Icons.CONTACTS, label="ግንኙነት"),
            ft.NavigationBarDestination(icon=ft.Icons.WORK, label="ፕሮጀክት"),
            ft.NavigationBarDestination(icon=ft.Icons.STAR, label="ኤግዚቢሽን"),
        ]
    )

    page.add(body_container)

# Run the Application
ft.app(target=main)
