import customtkinter as ctk
import os
from datetime import datetime
from tkinter import messagebox
from db_config import get_db_connection


class AdminSettingsDashboard(ctk.CTkFrame):

    def __init__(self, master, app_controller):
        super().__init__(master, fg_color="#181818")

        self.app = app_controller
        self.pack(fill="both", expand=True)

        self.show_pass_old = False
        self.show_pass_new = False
        self.show_pass_confirm = False

        
        ctk.CTkLabel(
            self,
            text="ADMIN SYSTEM SETTINGS",
            font=("Segoe UI", 24, "bold"),
            text_color="white"
        ).pack(pady=15)

        
        main = ctk.CTkFrame(self, fg_color="#222")
        main.pack(fill="both", expand=True, padx=20, pady=10)

       
        left = ctk.CTkFrame(main, fg_color="#1a1a1a", width=300)
        left.pack(side="left", fill="y", padx=10, pady=10)
        left.pack_propagate(False)

        ctk.CTkLabel(left, text="ADMIN PANEL", font=("Segoe UI", 18, "bold")).pack(pady=10)

        ctk.CTkLabel(left, text="Admin Information", text_color="gray").pack(anchor="w", padx=10, pady=5)

        ctk.CTkLabel(left, text=f"Username: {self.app.username}", text_color="white").pack(anchor="w", padx=10)
        ctk.CTkLabel(left, text=f"Role: {self.app.role}", text_color="white").pack(anchor="w", padx=10)

       
        right = ctk.CTkFrame(main, fg_color="transparent")
        right.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        
        ctk.CTkLabel(right, text="Change Admin Password", font=("Segoe UI", 16, "bold")).pack(anchor="w")

        self.old_pass = ctk.CTkEntry(right, placeholder_text="Old Password", show="*")
        self.old_pass.pack(fill="x", pady=5)

        self.old_eye = ctk.CTkButton(right, text="👁", width=40, command=self.toggle_old)
        self.old_eye.pack(anchor="e")

        self.new_pass = ctk.CTkEntry(right, placeholder_text="New Password", show="*")
        self.new_pass.pack(fill="x", pady=5)

        self.new_eye = ctk.CTkButton(right, text="👁", width=40, command=self.toggle_new)
        self.new_eye.pack(anchor="e")

        self.confirm_pass = ctk.CTkEntry(right, placeholder_text="Confirm Password", show="*")
        self.confirm_pass.pack(fill="x", pady=5)

        self.confirm_eye = ctk.CTkButton(right, text="👁", width=40, command=self.toggle_confirm)
        self.confirm_eye.pack(anchor="e")

        ctk.CTkButton(
            right,
            text="Update Password",
            fg_color="#2563eb",
            command=self.update_password
        ).pack(pady=10, fill="x")

        ctk.CTkLabel(right, text="Barangay Information", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(20, 5))

        self.barangay_entry = ctk.CTkEntry(right, placeholder_text="Barangay Name")
        self.barangay_entry.pack(fill="x", pady=5)

        self.captain_entry = ctk.CTkEntry(right, placeholder_text="Captain / Chairman")
        self.captain_entry.pack(fill="x", pady=5)

        ctk.CTkLabel(
            right,
            text="Maximum Daily Appointments",
            font=("Segoe UI", 16, "bold")
        ).pack(anchor="w", pady=(20, 5))

        self.max_appointments = ctk.CTkEntry(
            right,
            placeholder_text="e.g. 50"
        )
        self.max_appointments.pack(fill="x", pady=5)

        ctk.CTkButton(
            right,
            text="Save System Changes",
            fg_color="#16a34a",
            command=self.save_settings
        ).pack(pady=10, fill="x")

        ctk.CTkButton(
            right,
            text="Backup Database",
            fg_color="#f59e0b",
            command=self.backup_database
        ).pack(fill="x", pady=10)

        self.load_settings()

    
    def toggle_old(self):
        self.show_pass_old = not self.show_pass_old
        self.old_pass.configure(show="" if self.show_pass_old else "*")

    def toggle_new(self):
        self.show_pass_new = not self.show_pass_new
        self.new_pass.configure(show="" if self.show_pass_new else "*")

    def toggle_confirm(self):
        self.show_pass_confirm = not self.show_pass_confirm
        self.confirm_pass.configure(show="" if self.show_pass_confirm else "*")

    
    def load_settings(self):
        conn = get_db_connection()
        if not conn:
            return

        try:
            cur = conn.cursor()
            cur.execute("SELECT setting_key, setting_value FROM system_settings")
            data = dict(cur.fetchall())

            self.barangay_entry.insert(0, data.get("barangay_name", ""))
            self.captain_entry.insert(0, data.get("captain_name", ""))
            self.max_appointments.insert(
                0,
                data.get("max_daily_appointments", "50")
            )

            
        finally:
            cur.close()
            conn.close()

    #
    def save_settings(self):
        barangay = self.barangay_entry.get()
        captain = self.captain_entry.get()
        max_daily = self.max_appointments.get()

        conn = get_db_connection()
        if not conn:
            return

        try:
            cur = conn.cursor()

            cur.execute("""
                UPDATE system_settings
                SET setting_value=%s
                WHERE setting_key='barangay_name'
            """, (barangay,))

            cur.execute("""
                UPDATE system_settings
                SET setting_value=%s
                WHERE setting_key='captain_name'
            """, (captain,))

            cur.execute("""
                UPDATE system_settings
                SET setting_value=%s
                WHERE setting_key='max_daily_appointments'
            """, (max_daily,))

            conn.commit()
            messagebox.showinfo("Success", "System updated!")

        finally:
            cur.close()
            conn.close()

    
    def update_password(self):
        old = self.old_pass.get()
        new = self.new_pass.get()
        confirm = self.confirm_pass.get()

        if new != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return

        conn = get_db_connection()
        if not conn:
            return

        try:
            cur = conn.cursor()

            cur.execute("SELECT password FROM users WHERE username=%s", (self.app.username,))
            data = cur.fetchone()

            if not data or data[0] != old:
                messagebox.showerror("Error", "Wrong old password")
                return

            cur.execute("""
                UPDATE users
                SET password=%s
                WHERE username=%s
            """, (new, self.app.username))

            conn.commit()
            messagebox.showinfo("Success", "Password updated!")

        finally:
            cur.close()
            conn.close()
    def backup_database(self):
        try:
            filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"

            command = (
                f"mysqldump -u root barangay_db > {filename}"
            )

            os.system(command)

            messagebox.showinfo(
                "Success",
                f"Backup created:\n{filename}"
            )

        except Exception as e:
            messagebox.showerror(
                "Error",
                str(e)
            )