import customtkinter as ctk
from tkinter import messagebox
from db_config import get_db_connection



class SafetyGuideModal(ctk.CTkToplevel):
    def __init__(self, master, category, content):
        super().__init__(master)
        self.title(f"Safety Guide: {category}")
        self.geometry("400x500")
        self.resizable(False, False)

        
        self.transient(master)
        self.grab_set()

        ctk.CTkLabel(
            self, 
            text=category, 
            font=("Segoe UI", 20, "bold")
        ).pack(pady=20)

        textbox = ctk.CTkTextbox(self, width=350, height=350)
        textbox.pack(pady=10, padx=20)
        textbox.insert("0.0", content)
        textbox.configure(state="disabled") 

        ctk.CTkButton(
            self, 
            text="Close", 
            command=self.destroy,
            fg_color="#ff4d4d",
            hover_color="#cc0000"
        ).pack(pady=10)



class EmergencyDashboard(ctk.CTkFrame):

    def __init__(self, master, app_controller):
        super().__init__(master, fg_color="#181818")

        self.app = app_controller
        self.selected_id = None
        self.selected_frame = None

        self._refresh_job = None

        
        self.scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_container.pack(fill="both", expand=True, padx=25, pady=25)

        
        ctk.CTkLabel(
            self.scroll_container,
            text="Emergency & Disaster System",
            font=("Segoe UI", 28, "bold"),
            text_color="#ff4d4d"
        ).pack(anchor="w", pady=(0, 20))

        self.report_frame = ctk.CTkFrame(self.scroll_container, fg_color="#2b2b2b", corner_radius=15)
        self.report_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            self.report_frame,
            text=" Report Emergency",
            font=("Segoe UI", 18, "bold"),
            text_color="white"
        ).pack(anchor="w", padx=15, pady=10)

        self.category = ctk.CTkComboBox(
            self.report_frame,
            values=["Fire", "Medical", "Crime", "Disaster", "Other"]
        )
        self.category.set("Report")
        self.category.pack(fill="x", padx=15, pady=5)

        self.message = ctk.CTkTextbox(self.report_frame, height=80)
        self.message.pack(fill="x", padx=15, pady=5)
        self.message.insert("0.0", "Describe the emergency...")

        self.location = ctk.CTkEntry(self.report_frame, placeholder_text="Location")
        self.location.pack(fill="x", padx=15, pady=5)
        self.contact_entry = ctk.CTkEntry(self.report_frame, placeholder_text="09123456789")
        self.contact_entry.pack(fill="x", padx=15, pady=5)

        self.age_entry = ctk.CTkEntry(self.report_frame, placeholder_text="Age")
        self.age_entry.pack(fill="x", padx=15, pady=5)

        self.send_btn = ctk.CTkButton(
            self.report_frame,
            text=" SEND EMERGENCY",
            fg_color="#ff4d4d",
            hover_color="#cc0000",
            command=self.send_emergency
        )
        self.send_btn.pack(fill="x", padx=15, pady=15)

        # 
        if self.app.role == "admin":
            self.admin_frame = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
            self.admin_frame.pack(fill="x", pady=10)

            ctk.CTkButton(
                self.admin_frame,
                text="Responding",
                fg_color="#f39c12",
                hover_color="#e67e22",
                command=lambda: self.update_status("Responding")
            ).pack(side="left", padx=5)

            ctk.CTkButton(
                self.admin_frame,
                text="Resolved",
                fg_color="#28a745",
                hover_color="#218838",
                command=lambda: self.update_status("Resolved")
            ).pack(side="left", padx=5)

            ctk.CTkButton(
                self.admin_frame,
                text="Pending",
                fg_color="#6c757d",
                hover_color="#495057",
                command=lambda: self.update_status("Pending")
            ).pack(side="left", padx=5)

            ctk.CTkButton(
                self.admin_frame,
                text="Complete",
                fg_color="#3498db",
                hover_color="#2980b9",
                command=lambda: self.update_status("Completed")
            ).pack(side="left", padx=5)

        
        self.tree = ctk.CTkFrame(self.scroll_container, fg_color="#222222", corner_radius=12)
        self.tree.pack(fill="both", expand=True, pady=10)

    
        ctk.CTkLabel(
            self.tree,
            text=" List of Emergency Reports",
            font=("Segoe UI", 16, "bold"),
            text_color="white"
        ).pack(anchor="w", padx=15, pady=10)
    
        self.create_guide_menu()

        
        self.create_card(
            " Emergency Hotlines",
            ["Barangay Hotline: 0912-345-6789",
             "Emergency Desk: 888-0000",
             "National Emergency: 911",
             "Fire Department: 160",
             "Police Assistance: 117"],
            "#2b2b2b", "#f39c12"
        )

        self.create_card(
            " Evacuation Centers",
            ["Barangay Covered Court",
             "Barangay Hall",
             "Public School Gym",
             "High School Grounds"],
            "#2b2b2b", "#28a745"
        )

        self.create_card(
            " Emergency Kit Checklist",
            ["Water & canned food",
             "Flashlight",
             "First aid kit",
             "Documents",
             "Power bank",
             "Clothes",
             "Stay safe and alert"],
            "#2b2b2b", "#3498db"
        )

        
        self.load_data()
        self.auto_refresh()

    
    def load_data(self):
        conn = get_db_connection()
        if not conn:
            return

        try:
            cur = conn.cursor(dictionary=True)

            cur.execute("""
                SELECT id, username, category, message, location, status, created_at
                FROM emergency_reports
                WHERE status != 'Completed'
                ORDER BY id DESC
            """)

            rows = cur.fetchall()

            
            for w in self.tree.winfo_children():
                w.destroy()

            
            ctk.CTkLabel(
                self.tree,
                text=" List of Emergency Reports",
                font=("Segoe UI", 16, "bold"),
                text_color="white"
            ).pack(anchor="w", padx=15, pady=10)

            if not rows:
                ctk.CTkLabel(
                    self.tree,
                    text="No emergency reports yet...",
                    text_color="gray",
                    font=("Segoe UI", 14)
                ).pack(pady=30)

            for r in rows:
                frame = ctk.CTkFrame(self.tree, fg_color="#333333", corner_radius=8)
                frame.pack(fill="x", padx=10, pady=5)

   
                frame.bind(
                    "<Button-1>",
                    lambda e, rid=r["id"], f=frame: self.select_row(rid, f)
                )

                frame.configure(cursor="hand2")

            
                top_row = ctk.CTkFrame(frame, fg_color="transparent")
                top_row.pack(fill="x", padx=10, pady=5)

                status_color = self.get_status_color(r['status'])

                ctk.CTkLabel(
                    top_row,
                    text=f"● {r['status']}",
                    text_color=status_color,
                    font=("Segoe UI", 12, "bold")
                ).pack(side="right", padx=10)

            
                top_row.bind(
                    "<Button-1>",
                     lambda e, rid=r["id"], f=frame: self.select_row(rid, f)
                )

                ctk.CTkLabel(
                    top_row,
                    text=f"{r['category']}",
                    font=("Segoe UI", 14, "bold")
                ).pack(side="left")

                ctk.CTkLabel(
                    top_row,
                    text=f"👤 {r['username']}",
                    text_color="lightgray",
                    font=("Segoe UI", 12)
                ).pack(side="left", padx=10)

                ctk.CTkLabel(
                    top_row,
                    text=f"{r['location']}",
                    font=("Segoe UI", 12)
                ).pack(side="right")

                ctk.CTkLabel(
                    frame, 
                    text=r['message'], 
                    wraplength=700, 
                    justify="left"
                ).pack(anchor="w", padx=10, pady=(0,5))

                ctk.CTkLabel(
                    frame,
                    text=f"Reported: {r['created_at']}",
                    text_color="gray",
                    font=("Segoe UI", 11)
                ).pack(anchor="w", padx=10, pady=(0,5))

        finally:
            try:
                cur.close()
            except:
                pass

            try:
                conn.close()
            except:
                pass

    
    def select_row(self, rid, frame):
        for child in self.tree.winfo_children():
            if isinstance(child, ctk.CTkFrame):
                child.configure(fg_color="#333333")

        self.selected_id = rid
        self.selected_frame = frame

        if self.selected_frame.winfo_exists():
            self.selected_frame.configure(fg_color="#555555")
    
    def send_emergency(self):
       
        category = self.category.get()
        message = self.message.get("1.0", "end").strip()
        location = self.location.get().strip()
        contact = self.contact_entry.get().strip()
        age = self.age_entry.get().strip()

        
        if message == "Describe the emergency..." or not message:
            messagebox.showwarning("Incomplete", "Please describe the emergency in detail.")
            return
        
        
        if not location or len(location) < 5:
            messagebox.showwarning("Incomplete", "Please provide a specific location (at least 5 characters).")
            return
        
        if not contact.isdigit():
            messagebox.showwarning("Error", "Contact number must contain digits only.")
            return
        if len(contact) != 11:
            messagebox.showwarning("Error", "Contact number must be exactly 11 digits.")
            return
        if not age.isdigit():
            messagebox.showwarning("Error", "Age must be a valid number.")
            return
        if int(age) <= 0 or int(age) > 120:
            messagebox.showwarning("Error", "Please enter a valid age (1-120).")
            return
        
        conn = get_db_connection()
        if not conn:
            messagebox.showerror("Error", "Database connection failed.")
            return

        try:
            cur = conn.cursor()
           
            sql = """
                INSERT INTO emergency_reports (username, category, message, location, contact, age, status)
                VALUES (%s, %s, %s, %s, %s, %s, 'Pending')
                """
            cur.execute(sql, (self.app.username, category, message, location, contact, age))
            conn.commit() 
            
           
            messagebox.showinfo("Success", f"Your {category} report has been submitted.")

           
            self.message.delete("1.0", "end")
            self.message.insert("1.0", "Describe the emergency...")
            self.location.delete(0, "end")
            
            
            self.load_data()

        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to send report: {e}")
            print(f"Error: {e}")
        finally:
           
            if 'cur' in locals(): cur.close()
            if 'conn' in locals(): conn.close()

    
    def update_status(self, new_status):
        if not self.selected_id:
            messagebox.showwarning("Warning", "Select a report first")
            return

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE emergency_reports
            SET status=%s
            WHERE id=%s
        """, (new_status, self.selected_id))

        conn.commit()
        cur.close()
        conn.close()

        self.load_data()

    
    def auto_refresh(self):
        self.load_data()

        if self._refresh_job:
            self.after_cancel(self._refresh_job)

        self._refresh_job = self.after(10000, self.auto_refresh)

    
    def get_status_color(self, status):
        if status == "Pending":
            return "gray"
        elif status == "Responding":
            return "#f39c12"
        elif status == "Resolved":
            return "#707172"
        elif status == "Completed": 
            return "#15d42f"
        return "white"

    
    def create_card(self, title, items, bg, color):
        card = ctk.CTkFrame(self.scroll_container, fg_color=bg, corner_radius=15)
        card.pack(fill="x", pady=10)

        ctk.CTkLabel(
            card,
            text=title,
            font=("Segoe UI", 18, "bold"),
            text_color=color
        ).pack(anchor="w", padx=15, pady=10)

        ctk.CTkLabel(
            card,
            text="\n".join([f"• {i}" for i in items]),
            text_color="white",
            justify="left"
        ).pack(anchor="w", padx=15, pady=(0, 15))

    def create_guide_menu(self):
        guide_frame = ctk.CTkFrame(self.scroll_container, fg_color="#2b2b2b", corner_radius=15)
        guide_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            guide_frame, 
            text="Safety Guides", 
            font=("Segoe UI", 18, "bold"),
            text_color="#3498db"
        ).pack(anchor="w", padx=15, pady=10)

        
        button_frame = ctk.CTkFrame(guide_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=5, padx=15)

        guides = {
            " Fire": " WHAT TO DO:\n\n1. Stay low under smoke.\n2. Cover nose/mouth with wet cloth.\n3. Do NOT use elevators.\n4. Check doors for heat before opening.\n5. Call Fire Dept: 160 or 911.\n6. Evacuate calmly to assembly area.",
            
            " Typhoon": " WHAT TO DO:\n\n1. Secure windows and roof.\n2. Charge phones and lights.\n3. Store water and food.\n4. Listen to news updates.\n5. Stay indoors. Do not go out.\n6. Evacuate if ordered by officials.",
            
            " Flood": " WHAT TO DO:\n\n1. Move to higher ground immediately.\n2. Turn off main power switch.\n3. Do NOT walk/swim in floodwater.\n4. Avoid electric posts/wires.\n5. Bring emergency kit with you.\n6. Wait for rescue if trapped.",

            " Medical": " WHAT TO DO:\n\n1. Check if safe to approach.\n2. Do not move injured person unless danger.\n3. Call emergency: 911.\n4. Apply first aid if trained.\n5. Loosen tight clothing.\n6. Keep person calm and warm."
        }

        for cat, text in guides.items():
            ctk.CTkButton(
                button_frame, 
                text=cat, 
                width=100,
                fg_color="#3498db",
                hover_color="#2980b9",
                command=lambda c=cat, t=text: SafetyGuideModal(self, c, t)
            ).pack(side="left", padx=5, pady=5) 