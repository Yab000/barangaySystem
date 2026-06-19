import customtkinter as ctk
import calendar
from datetime import datetime, date
import holidays
from tkinter import messagebox
from db_config import get_db_connection

class CalendarView(ctk.CTkFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color="transparent")
        self.app = app_controller
        self.pack(fill="both", expand=True, padx=25, pady=25)

        now = datetime.now()
        self.current_year = now.year
        self.current_month = now.month

        
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(0, 20))
        ctk.CTkButton(self.header_frame, text="<", width=50, fg_color="#333333", command=self.prev_month).pack(side="left")
        self.lbl_month_year = ctk.CTkLabel(self.header_frame, text="", font=("Arial", 22, "bold"))
        self.lbl_month_year.pack(side="left", expand=True)
        ctk.CTkButton(self.header_frame, text=">", width=50, fg_color="#333333", command=self.next_month).pack(side="right")

        
        self.legend_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.legend_frame.pack(fill="x", pady=(0, 10))
        self.create_legend()
        self.calendar_grid = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=15)
        self.calendar_grid.pack(fill="both", expand=True)
        for i in range(7): self.calendar_grid.columnconfigure(i, weight=1)
        self.draw_calendar()

    def create_legend(self):
        legend_items = [("Today", "#2a9d8f"), ("Booked", "#e67e22"), ("Holiday", "#c0392b")]
        for text, color in legend_items:
            frame = ctk.CTkFrame(self.legend_frame, fg_color="transparent")
            frame.pack(side="left", padx=10)
            ctk.CTkLabel(frame, text="", fg_color=color, width=15, height=15, corner_radius=3).pack(side="left", padx=5)
            ctk.CTkLabel(frame, text=text, font=("Arial", 12)).pack(side="left")

    def fetch_appointments(self):
        conn = None
        try:
            conn = get_db_connection()
            if not conn: return []
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SELECT id, appointment_date, fullname, status FROM appointments")
            return cursor.fetchall()
        except Exception as e:
            print("Fetch Error:", e)
            return []
        finally:
            if conn: conn.close()

    def draw_calendar(self):
        for w in self.calendar_grid.winfo_children(): w.destroy()
        self.lbl_month_year.configure(text=f"{calendar.month_name[self.current_month]} {self.current_year}")
        
    
        for i, day_name in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
            ctk.CTkLabel(self.calendar_grid, text=day_name, font=("Arial", 12, "bold")).grid(row=0, column=i, pady=5)

        appointments = self.fetch_appointments()
        ph_holidays = holidays.PH(years=self.current_year)
        booked_days = {}
        
        for app in appointments:
            appt_date = app.get("appointment_date")
            if not appt_date: continue
            if isinstance(appt_date, str): appt_date = datetime.strptime(appt_date, "%Y-%m-%d")
            elif isinstance(appt_date, date): appt_date = datetime.combine(appt_date, datetime.min.time())
            
            if appt_date.year == self.current_year and appt_date.month == self.current_month:
                booked_days.setdefault(appt_date.day, []).append(app)

        cal = calendar.monthcalendar(self.current_year, self.current_month)
        for r, week in enumerate(cal, start=1):
            for c, day in enumerate(week):
                if day == 0: continue
                current_date = date(self.current_year, self.current_month, day)
                bg = "#c0392b" if current_date in ph_holidays else "#2a9d8f" if current_date == date.today() else "#e67e22" if day in booked_days else "#2b2b2b"
                
                ctk.CTkButton(self.calendar_grid, text=str(day), width=80, height=80, fg_color=bg, font=("Arial", 14, "bold"),
                              command=lambda d=day: self.show_day_details(d, booked_days.get(d, []))).grid(row=r, column=c, padx=2, pady=2, sticky="nsew")

    def show_day_details(self, day, appointments):
        if not appointments:
            messagebox.showinfo("Schedule", f"No appointment sa {day}.")
            return

   
        app = appointments[0]
   
   
        window = ctk.CTkToplevel(self)
        window.title(f"Appointment: {app.get('fullname')}")
        window.geometry("400x400")
        window.attributes("-topmost", True) 

        ctk.CTkLabel(window, text=f"User: {app.get('fullname')}", font=("Arial", 16, "bold")).pack(pady=10)
        ctk.CTkLabel(window, text=f"Current Status: {app.get('status')}").pack()

    
        ctk.CTkLabel(window, text="New Appointment Date (YYYY-MM-DD):").pack(pady=(10, 0))
        date_entry = ctk.CTkEntry(window, placeholder_text="2026-06-25")
        date_entry.insert(0, f"{self.current_year}-{self.current_month:02d}-{day:02d}")
        date_entry.pack(pady=5)

        ctk.CTkLabel(window, text="Reason for Reschedule:").pack(pady=(10, 0))
        reason_entry = ctk.CTkEntry(window, width=300)
        reason_entry.pack(pady=5)

    
        def save_resched():
            new_date = date_entry.get()
            reason = reason_entry.get()
        
            if not reason:
                messagebox.showwarning("Error", "Need a reason for the reschedule.")
                return

        
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                query = "UPDATE appointments SET appointment_date = %s, reason = %s, status = 'Rescheduled' WHERE id = %s"
                cursor.execute(query, (new_date, reason, app['id']))
                conn.commit()
                conn.close()
            
                messagebox.showinfo("Success", "Successfully rescheduled!")
                window.destroy()
                self.draw_calendar() 
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ctk.CTkButton(window, text="Confirm Reschedule", fg_color="#e67e22", command=save_resched).pack(pady=20)

    def prev_month(self):
        self.current_month -= 1
        if self.current_month < 1: self.current_month, self.current_year = 12, self.current_year - 1
        self.draw_calendar()

    def next_month(self):
        self.current_month += 1
        if self.current_month > 12: self.current_month, self.current_year = 1, self.current_year + 1
        self.draw_calendar()