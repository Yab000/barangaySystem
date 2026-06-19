import customtkinter as ctk
from tkinter import messagebox
import hashlib
import json
import os
from db_config import get_db_connection
import mysql.connector
import datetime


class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color="#1e1e1e", corner_radius=20)
        self.app = app_controller
        self.password_visible = False
        self.pack(pady=50, padx=50, fill="both", expand=True)

        
        ctk.CTkLabel(self, text="WELCOME BACK", font=("Segoe UI", 28, "bold")).pack(pady=(40, 10))
        ctk.CTkLabel(self, text="Barangay Appointment System", text_color="gray").pack(pady=(0, 20))

        self.username_entry = ctk.CTkEntry(self, placeholder_text="Username", width=350, height=45)
        self.username_entry.pack(pady=8)

        pass_frame = ctk.CTkFrame(self, fg_color="transparent")
        pass_frame.pack(pady=8)
        self.password_entry = ctk.CTkEntry(pass_frame, placeholder_text="Password", show="*", width=300, height=45)
        self.password_entry.pack(side="left")
        self.eye_btn = ctk.CTkButton(pass_frame, text="👁", width=45, height=45,
                                     fg_color="#2a2a2a", hover_color="#444",
                                     command=self.toggle_password)
        self.eye_btn.pack(side="left", padx=5)

        self.role_select = ctk.CTkComboBox(self, values=["admin", "resident"], width=350, height=45)
        self.role_select.set("resident")
        self.role_select.pack(pady=8)

        self.remember_var = ctk.BooleanVar()
        ctk.CTkCheckBox(self, text="Remember Me", variable=self.remember_var).pack(pady=5)

        ctk.CTkButton(self, text="LOGIN", width=350, height=45,
                      fg_color="#0d6efd", command=self.check_login).pack(pady=(15, 5))

        ctk.CTkButton(self, text="Forgot Password?", fg_color="transparent",
                      text_color="#ffcc00", command=self.forgot_password).pack(pady=(0, 5))

        ctk.CTkButton(self, text="Create Account", fg_color="transparent",
                      text_color="#00bfff", command=self.app.show_register).pack(pady=(0, 10))

        self.load_saved_user()
        self.password_entry.bind("<Return>", lambda e: self.check_login())

    
    def save_user(self, username, role):
        if self.remember_var.get():
            try:
                with open("session.json", "w") as f:
                    json.dump({
                        "username": username,
                        "role": role
                    }, f)
            except Exception as e:
                print("Session Save Error:", e)

    
    def load_saved_user(self):
        if os.path.exists("session.json"):
            try:
                with open("session.json", "r") as f:
                    data = json.load(f)

                self.username_entry.insert(0, data.get("username", ""))
                self.role_select.set(data.get("role", "resident"))
            except:
                pass

    def toggle_password(self):
        self.password_visible = not self.password_visible
        self.password_entry.configure(show="" if self.password_visible else "*")
        self.eye_btn.configure(text="🙈" if self.password_visible else "👁")

    def forgot_password(self):
        win = ctk.CTkToplevel(self)
        win.title("Forgot Password")
        win.geometry("400x400")
        win.attributes("-topmost", True)

        ctk.CTkLabel(win, text="Reset Password", font=("Segoe UI", 20, "bold")).pack(pady=20)

        user_entry = ctk.CTkEntry(win, placeholder_text="Username", width=300)
        user_entry.pack(pady=5)

        email_entry = ctk.CTkEntry(win, placeholder_text="Email", width=300)
        email_entry.pack(pady=5)

        new_p_entry = ctk.CTkEntry(win, placeholder_text="New Password", show="*", width=300)
        new_p_entry.pack(pady=5)

        conf_p_entry = ctk.CTkEntry(win, placeholder_text="Confirm Password", show="*", width=300)
        conf_p_entry.pack(pady=5)

        def execute_reset():
            user = user_entry.get().strip()
            email = email_entry.get().strip()
            new_p = new_p_entry.get()
            conf_p = conf_p_entry.get()

            if not all([user, email, new_p, conf_p]):
                messagebox.showerror("Error", "All fields are required!")
                return

            if new_p != conf_p:
                messagebox.showerror("Error", "Passwords do not match!")
                return

            conn = get_db_connection()
            if not conn:
                return

            try:
                cursor = conn.cursor(dictionary=True)

                
                cursor.execute(
                    "SELECT * FROM users WHERE username=%s AND email=%s",
                    (user, email)
                )
                result = cursor.fetchone()

                if not result:
                    messagebox.showerror("Error", "User not found or email mismatch!")
                    return

                hashed = hashlib.sha256(new_p.encode()).hexdigest()

                cursor.execute(
                    "UPDATE users SET password=%s WHERE username=%s",
                    (hashed, user)
                )

                conn.commit()

                messagebox.showinfo("Success", "Password updated successfully!")
                win.destroy()

            except Exception as e:
                messagebox.showerror("Database Error", str(e))

            finally:
                if conn:
                    conn.close()

        ctk.CTkButton(win, text="Update Password", fg_color="#28a745",
                    command=execute_reset).pack(pady=20)

    
    def check_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        role_input = self.role_select.get().strip().lower()

        if not username or not password:
            messagebox.showerror("Error", "Please fill all fields")
            return

        conn = get_db_connection()

        if conn is None:
            messagebox.showerror("Error", "Database connection failed")
            return

        cursor = None

        try:
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT username, password, role
                FROM users
                WHERE username=%s
            """, (username,))

            user = cursor.fetchone()

            if not user:
                messagebox.showerror("Login Failed", "Invalid credentials")
                return

            hashed_input = hashlib.sha256(password.encode()).hexdigest()

            if user["password"] != hashed_input:
                messagebox.showerror("Login Failed", "Invalid credentials")
                return
                

            if user["role"].strip().lower() != role_input:
                messagebox.showerror("Role Error", "Wrong role selected")
                return
            try:
    
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                update_cursor = conn.cursor()
                update_cursor.execute("UPDATE users SET last_login = %s WHERE username = %s", (now, username))
                conn.commit() 
                update_cursor.close()
            except Exception as e:
                print("Error updating last_login:", e)

            self.save_user(username, user["role"])
            self.add_history(username, "LOGIN")

            self.after(
                200,
                lambda: self.app.show_dashboard(user["role"], username)
            )

        except Exception as e:
            messagebox.showerror("Error", str(e))

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


    def add_history(self, username, action):
        try:
            conn = get_db_connection()
            if conn is None:
                return

            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO activity_logs (username, action, timestamp)
                VALUES (%s, %s, NOW())
            """, (username, action))

            conn.commit()

            cursor.close()
            conn.close()

        except Exception as e:
            print("History error:", e)