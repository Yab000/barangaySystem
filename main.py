import customtkinter as ctk

from user_login import LoginFrame
from admin_window import AdminDashboard
from resident_window import ResidentDashboard
from monitor_window import MonitorDashboard
from history_window import HistoryDashboard  
from appointments_window import AppointmentsDashboard
from settings_window import SettingsDashboard
from admin_settings_window import AdminSettingsDashboard
from registration_window import RegistrationWindow
from calendar_window import CalendarView
from request_form import RequestFormWindow     
from emergency_window import EmergencyDashboard
from welcome_window import WelcomeDashboard



ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class BarangayApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Barangay Appointment and Queue Management System")
        self.geometry("1200x700")

        self.sidebar_visible = True

        self.username = None
        self.role = None

        self.nav_buttons = {}
        self.active_page = None

        
        self.container = ctk.CTkFrame(self, fg_color="#0f0f0f")
        self.container.pack(fill="both", expand=True)

        self.display_area = None
        self.sidebar = None

        self.show_login()

    def create_sidebar(self):
        
       if self.sidebar:
        btn_appts = ctk.CTkButton(
            self.sidebar, 
            text="Appointments", 
            fg_color="transparent", 
            anchor="w"
        )
        btn_appts.pack(fill="x", pady=5)
        self.nav_buttons["Appointments"] = btn_appts

    def set_notification(self, button_key, has_notification):
        
        btn = self.nav_buttons.get(button_key)
        if not btn: return


        for widget in btn.winfo_children():
            if getattr(widget, "is_badge", False):
                widget.destroy()

        if has_notification:
            badge = ctk.CTkLabel(
                btn,
                text=" ",
                width=12,
                height=12,
                corner_radius=6, 
                fg_color="#FF0000",
            )
            badge.is_badge = True

            badge.place(relx=0.85, rely=0.15)
    
    def show_login(self):
        self.clear_container()
        frame = ctk.CTkFrame(self.container, fg_color="transparent")
        frame.pack(fill="both", expand=True)
        LoginFrame(frame, self)

    def show_register(self):
        RegistrationWindow(self)

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()
    
    def toggle_sidebar(self):
        if self.sidebar_visible:
            self.sidebar.grid_remove()
            self.sidebar_visible = False
            
        else:
            self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
            self.sidebar_visible = True

    def set_notification(self, page_name, has_notification):
        if page_name in self.nav_buttons:
            btn = self.nav_buttons[page_name]
            current_text = btn.cget("text")
            clean_text = current_text.replace(" ●", "")
            if has_notification:
                btn.configure(text=f"{clean_text} ●", text_color="#ef4444")
            else:
                btn.configure(text=clean_text, text_color="white")

    def show_dashboard(self, role, username):
        self.clear_container()
        self.username = username
        self.role = role.lower()

       
        self.container.grid_columnconfigure(0, weight=0)
        self.container.grid_columnconfigure(1, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

      
        self.sidebar = ctk.CTkFrame(self.container, width=280, fg_color="#0b0f14")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        ctk.CTkLabel(self.sidebar, text="👤", font=("Segoe UI Emoji", 40)).pack(pady=(20, 0))
        
        title = " ADMIN PANEL" if self.role == "admin" else " USER PANEL"
        ctk.CTkLabel(self.sidebar, text=title, font=("Segoe UI", 20, "bold"), 
                     text_color="#facc15" if self.role == "admin" else "white").pack(pady=(20, 5))
        
        ctk.CTkLabel(self.sidebar, text=self.username, text_color="gray").pack()
        ctk.CTkFrame(self.sidebar, height=2, fg_color="#1f2937").pack(fill="x", padx=15, pady=10)

        
        self.nav_buttons.clear()
        for text, page in self.get_buttons(self.role):
            btn = ctk.CTkButton(
                self.sidebar, text=text, fg_color="transparent",
                hover_color="#1f2937", anchor="w", height=45,
                font=("Segoe UI", 15),
                command=lambda p=page: self.load_content(p)
            )
            btn.pack(fill="x", padx=15, pady=5)
            self.nav_buttons[page] = btn


        
        ctk.CTkButton(self.sidebar, text="🚪 Logout", fg_color="#dc2626", hover_color="#991b1b",
                      command=self.logout).pack(side="bottom", fill="x", padx=15, pady=20)

        
        self.main_display = ctk.CTkFrame(self.container, fg_color="#141414")
        self.main_display.grid(row=0, column=1, sticky="nsew")

        
        self.hamburger_btn = ctk.CTkButton(
            self.main_display, text="☰", width=40, height=40,
            fg_color="transparent", command=self.toggle_sidebar
        )
        self.hamburger_btn.pack(anchor="nw", padx=10, pady=10)

       
        self.display_area = ctk.CTkFrame(self.main_display, fg_color="transparent")
        self.display_area.pack(fill="both", expand=True, padx=10, pady=10)

        
        initial_page = "Admin" if self.role == "admin" else "Welcome"
        self.load_content(initial_page)
   
    def get_buttons(self, role):
        if role == "admin":
            return [
                 ("Admin", "Admin"),
                (" Emergency", "Emergency"),
                ("Appointments", "Appointments"),
                (" Queue", "Queue"),
                (" History", "History"),
                (" Calendar", "Calendar"),
                (" Settings", "AdminSettings")
            ]
        else:
            return [
                (" Dashboard", "Welcome"),
                (" Create Appointment", "Request"),
                (" Emergency", "Emergency"),
                (" Calendar", "Calendar"),
                (" History", "History"),
                (" Settings", "Settings")
            ]

    
    def load_content(self, page):
        if not self.display_area:
            return

       
        for widget in self.display_area.winfo_children():
            widget.destroy()

        pages = {
            "Admin": AdminDashboard,
            "Resident": ResidentDashboard,
            "Welcome": WelcomeDashboard,
            "Appointments": AppointmentsDashboard,
            "Queue": MonitorDashboard,
            "History": HistoryDashboard,
            "Calendar": CalendarView,
            "Settings": SettingsDashboard,
            "AdminSettings": AdminSettingsDashboard,
            "Emergency": EmergencyDashboard,
            "Request": RequestFormWindow,
        }

        page_class = pages.get(page)


        if not page_class:
            print("Unknown page:", page)
            return

        try:
            
            if page == "Request":
                frame = page_class(
                    self.display_area,
                    self,
                    self.username,
                    self.role,
                    None
                )
            elif page == "Admin":
                frame = page_class(self.display_area, self)
            else:    

                frame = page_class(self.display_area, self)

            frame.pack(fill="both", expand=True)
            self.update_nav_highlight(page)
            self.active_page = page

        except Exception as e:
            print(f"Error loading {page}: {e}")
            ctk.CTkLabel(
                self.display_area,
                text=f"Error loading {page}",
                text_color="red"
            ).pack()

    def update_nav_highlight(self, active_page):
        for page, btn in self.nav_buttons.items():
            if page == active_page:
                btn.configure(fg_color="#2563eb", text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color="white")


    def logout(self):
        self.username = None
        self.role = None
        self.show_login()

if __name__ == "__main__":
    app = BarangayApp()
    app.mainloop()