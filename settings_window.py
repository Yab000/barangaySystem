import customtkinter as ctk
from tkinter import messagebox
from db_config import get_db_connection
import hashlib
import re
import datetime

class SettingsDashboard(ctk.CTkFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color="transparent")
        self.app = app_controller
        self.build_ui()
        self.load_profile()

    def build_ui(self):
        self.pack(fill="both", expand=True, padx=30, pady=30)

        ctk.CTkLabel(
            self,
            text="USER SETTINGS",
            font=("Arial", 24, "bold")
        ).pack(pady=(0, 20), anchor="w")

        
        profile_frame = ctk.CTkFrame(self, fg_color="#2b2b2b", corner_radius=10)
        profile_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            profile_frame,
            text="Profile Information",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=20, pady=10)

        self.fullname = self.create_input(profile_frame, "Full Name")
        self.email = self.create_input(profile_frame, "Email")
        self.contact = self.create_input(profile_frame, "Contact")
        self.address = self.create_input(profile_frame, "Address")

        ctk.CTkButton(
            profile_frame,
            text="Save Profile",
            fg_color="#2563eb",
            command=self.save_profile
        ).pack(anchor="e", padx=20, pady=10)

        
        pass_frame = ctk.CTkFrame(self, fg_color="#2b2b2b", corner_radius=10)
        pass_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            pass_frame,
            text="Change Password",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=20, pady=10)

        self.old_pass = self.create_password_field(pass_frame, "Old Password")
        self.new_pass = self.create_password_field(pass_frame, "New Password")
        self.confirm_pass = self.create_password_field(pass_frame, "Confirm Password")

        ctk.CTkButton(
            pass_frame,
            text="Update Password",
            command=self.change_password
        ).pack(anchor="e", padx=20, pady=10)

        
        self.activity_label = ctk.CTkLabel(self, text="Last login: Loading...", text_color="gray")
        self.activity_label.pack(pady=5)

        ctk.CTkButton(
            self,
            text="Delete Account",
            fg_color="#dc3545",
            command=self.delete_account
        ).pack(pady=10)
        
        ctk.CTkButton(
            self,
            text="Back to Dashboard",
            fg_color="#6c757d",
            command=self.go_back
        ).pack(pady=10)

   
    def create_input(self, parent, placeholder):
        entry = ctk.CTkEntry(parent, placeholder_text=placeholder)
        entry.pack(fill="x", padx=20, pady=5)
        return entry

    def create_password_field(self, parent, placeholder):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=5)
        entry = ctk.CTkEntry(frame, placeholder_text=placeholder, show="*")
        entry.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(frame, text="👁", width=30, command=lambda: self.toggle_pass(entry)).pack(side="right", padx=5)
        return entry

    def toggle_pass(self, entry):
        entry.configure(show="" if entry.cget("show") == "*" else "*")

    
    def go_back(self):
        self.destroy()
    
        
        self.app.show_dashboard(self.app.username, self.app.role)
 
    def logout(self):
        self.app.logout()

    def load_profile(self):
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute("""
                SELECT full_name, email, contact, address, last_login
                FROM users
                WHERE username=%s
            """, (self.app.username,))

            data = cur.fetchone()

            if data:
                self.fullname.insert(0, data.get("full_name") or "")
                self.email.insert(0, data.get("email") or "")
                self.contact.insert(0, data.get("contact") or "")
                self.address.insert(0, data.get("address") or "")

                last_login = data.get("last_login")

                if last_login:
                    self.activity_label.configure(text=f"Last login: {last_login}")
                else:
                    self.activity_label.configure(text="Last login: First time login")

        finally:
            cur.close()
            conn.close()

    
    def save_profile(self):
      
        email = self.email.get()
        if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messagebox.showerror("Error", "Invalid Email Format")
            return

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE users
                SET full_name=%s, email=%s, contact=%s, address=%s
                WHERE username=%s
            """, (self.fullname.get(), email, self.contact.get(), 
                  self.address.get(), self.app.username))
            conn.commit()
            messagebox.showinfo("Success", "Profile updated!")
        finally:
            cur.close()
            conn.close()

   
    def change_password(self):
        old = self.old_pass.get().strip()
        new = self.new_pass.get().strip()
        confirm = self.confirm_pass.get().strip()

        if not old or not new or not confirm:
            messagebox.showwarning("Missing", "Fill all fields")
            return
        if new != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return
        if len(new) < 8:
            messagebox.showerror("Error", "Password must be at least 8 characters")
            return

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute("SELECT password FROM users WHERE username=%s", (self.app.username,))
            user = cur.fetchone()
            
            old_hash = hashlib.sha256(old.encode()).hexdigest()
            if user["password"] != old_hash:
                messagebox.showerror("Error", "Old password incorrect")
                return

            new_hash = hashlib.sha256(new.encode()).hexdigest()
            cur.execute("UPDATE users SET password=%s WHERE username=%s", 
                        (new_hash, self.app.username))
            conn.commit()
            messagebox.showinfo("Success", "Password updated!")
            
            
            for entry in [self.old_pass, self.new_pass, self.confirm_pass]:
                entry.delete(0, 'end')
        finally:
            cur.close()
            conn.close()

   
    def delete_account(self):
        if messagebox.askyesno("Confirm", "Are you sure? This action cannot be undone."):
            conn = get_db_connection()
            cur = conn.cursor()
            try:
                cur.execute("DELETE FROM users WHERE username=%s", (self.app.username,))
                conn.commit()
                messagebox.showinfo("Goodbye", "Account deleted successfully.")
                self.app.logout()
            finally:
                cur.close()
                conn.close()