import customtkinter as ctk
from tkinter import messagebox
from db_config import get_db_connection

class WelcomeDashboard(ctk.CTkFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color="#141414")
        self.app = app_controller

        
        self.pending_count = ctk.StringVar(value="0")
        self.approved_count = ctk.StringVar(value="0")
        self.rejected_count = ctk.StringVar(value="0")
        self.cancelled_count = ctk.StringVar(value="0")


        self.header_card = ctk.CTkFrame(self, fg_color="#1f2937", corner_radius=18)
        self.header_card.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            self.header_card,
            text=f"Welcome, {self.app.username or 'Resident'}!",
            font=("Segoe UI", 28, "bold"),
            text_color="white"
        ).pack(anchor="w", padx=20, pady=18)

        
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=20, pady=10)

        self.content.grid_columnconfigure(0, weight=3) 
        self.content.grid_columnconfigure(1, weight=2) 
        self.content.grid_rowconfigure(0, weight=1)

    
        self.left_panel = ctk.CTkScrollableFrame(
            self.content,
            fg_color="#1e1e1e",
            corner_radius=20
        )
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
        


        self.stats_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        self.stats_frame.pack(fill="x", padx=20, pady=10)

        self.create_stat("Pending", self.pending_count, "#374151")
        self.create_stat("Approved", self.approved_count, "#14532d")
        self.create_stat("Rejected", self.rejected_count, "#7f1d1d")
        self.create_stat("Cancelled", self.cancelled_count, "#1f2937")

        
        self.status_box = ctk.CTkFrame(self.left_panel, fg_color="#2a2a2a", corner_radius=15)
        self.status_box.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(self.status_box, text="Latest Status", font=("Segoe UI", 16, "bold")).pack(pady=10)

        self.lbl_latest = ctk.CTkLabel(self.status_box, text="Loading...")
        self.lbl_latest.pack()

        self.lbl_queue = ctk.CTkLabel(self.status_box, text="Queue: --")
        self.lbl_queue.pack()

        self.lbl_position = ctk.CTkLabel(self.status_box, text="Position: --")
        self.lbl_position.pack()

        self.lbl_now = ctk.CTkLabel(
            self.status_box,
            text="Now Serving: --",
            font=("Segoe UI", 14, "bold"),
            text_color="red"
        )
        self.lbl_now.pack(pady=10)


        self.mv_frame = ctk.CTkFrame(self.left_panel, fg_color="#1f2937", corner_radius=15)
        self.mv_frame.pack(fill="x", padx=20, pady=(10, 20))

        ctk.CTkLabel(
            self.mv_frame,
            text="MISSION",
            font=("Segoe UI", 16, "bold"),
            text_color="#facc15"
        ).pack(anchor="w", padx=15, pady=(10, 0))

        ctk.CTkLabel(
            self.mv_frame,
            text="To provide an efficient, reliable, and user-friendly Barangay Appointment and Queue Management System that streamlines appointment scheduling, reduces waiting time, improves service delivery, and ensures transparent monitoring of transactions for all residents.",
            wraplength=420,
            justify="left"
        ).pack(anchor="w", padx=15, pady=(0, 10))

        ctk.CTkLabel(
            self.mv_frame,
            text="VISION",
            font=("Segoe UI", 16, "bold"),
            text_color="#60a5fa"
        ).pack(anchor="w", padx=15, pady=(10, 0))

        ctk.CTkLabel(
            self.mv_frame,
            text="To become a modern and digitally empowered barangay that delivers accessible, organized, and efficient public services through technology, enhancing resident satisfaction and promoting a responsive and well-managed community.",
            wraplength=420,
            justify="left"
        ).pack(anchor="w", padx=15, pady=(0, 15))

        
        self.right_panel = ctk.CTkFrame(
            self.content,
            fg_color="#1e1e1e",
            corner_radius=20,
            width=420
        )
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=10)

        self.right_scroll = ctk.CTkScrollableFrame(
            self.right_panel,
            fg_color="transparent"
        )
        self.right_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        
        ctk.CTkLabel(
            self.right_scroll,
            text="Announcements",
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", padx=15, pady=10)

        self.announcement_container = ctk.CTkFrame(self.right_scroll, fg_color="transparent")
        self.announcement_container.pack(fill="both", expand=True, padx=10, pady=10)

        
        self.default_announcements = [
            " General Barangay Assembly\n\n"
            " Barangay Hall\n"
            " June 15, 2026\n"
            " 8:00 AM - 12:00 NN\n\n"
            "Local assemblies are conducted periodically by the Punong Barangay to discuss budget transparency, community projects, municipal ordinances, and resident concerns. Residents are encouraged to attend and participate in discussions regarding barangay programs and services.",

            " Community Clean-Up Drive\n\n"
            " June 20, 2026\n"
            " 7:00 AM - 11:00 AM\n\n"
            "Barangay residents are invited to participate in the community sanitation and drainage declogging drive. This activity helps prevent flooding and promotes proper waste management. Please bring personal cleaning materials if available.",

            " Power Interruption Advisory\n\n"
            " June 25, 2026\n"
            " 9:00 AM - 5:00 PM\n\n"
            "A scheduled power interruption will take place due to electrical maintenance and facility upgrades. Residents are advised to charge devices beforehand and monitor official advisories for updates.",

            " Curfew Advisory\n\n"
            " 10:00 PM - 4:00 AM\n\n"
            "The barangay strictly implements the curfew ordinance for minors aged 17 years old and below. Minors found outside during curfew hours without proper supervision may be escorted home or referred to appropriate authorities.",

            " Relief Distribution Program\n\n"
            " Senior Citizens & PWDs\n\n"
            "Relief assistance will be distributed to qualified Senior Citizens and Persons with Disabilities. Please bring your original Senior Citizen ID or PWD ID together with a photocopy for verification purposes."
        ]


        self.contact_card = ctk.CTkFrame(
            self.right_scroll,
            fg_color="#1f2937",
            corner_radius=15
        )
        self.contact_card.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(
            self.contact_card,
            text="If You Have Any Other Concerns",
            font=("Segoe UI", 16, "bold"),
            text_color="#34d399"
        ).pack(anchor="w", padx=15, pady=(15, 5))

        contact_text = (
            "If you have any other concerns, you can visit our social media\n\n"
            "Email: barangaygroup7@gmail.com\n"
            "Facebook: barangaygroup7\n\n"
            "Contact Number: 01234567891\n"
            "Hotline: 1-877-777-2680\n\n"
            "Office: V.V. Soliven Ave. II, Bgy. San Isidro, Cainta\n"
            "Office Hours: 8:00 AM to 7:00 PM Monday to Sunday\n\n"
            "Thank you, User/Resident!"
        )

        ctk.CTkLabel(
            self.contact_card,
            text=contact_text,
            justify="left",
            wraplength=350,
            width=300,  
            text_color="white"
        ).pack(anchor="w", padx=15, pady=(0, 15))

        self._show_announcements()
        self._build_reminders()
        self._build_services()

    
        self.check_appointment_status()
        self.check_queue_status()
        self.auto_refresh()
    def update_stats_from_db(self):
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT status, COUNT(*) as count FROM appointments WHERE username=%s GROUP BY status"
            cursor.execute(query, (self.app.username,))
            results = cursor.fetchall()
            
            counts = {"Pending": "0", "Approved": "0", "Rejected": "0", "Cancelled": "0"}
            
            for row in results:
                counts[row['status']] = str(row['count'])
            
            self.pending_count.set(counts["Pending"])
            self.approved_count.set(counts["Approved"])
            self.rejected_count.set(counts["Rejected"])
            self.cancelled_count.set(counts["Cancelled"])
            
        except Exception as e:
            print("ERROR sa update_stats_from_db:", e)
        finally:
            if conn: conn.close()
    
    def create_stat(self, title, var, color):
        card = ctk.CTkFrame(self.stats_frame, fg_color=color, corner_radius=12)
        card.pack(fill="x", pady=5)
        ctk.CTkLabel(card, text=title, font=("Segoe UI", 14, "bold"), text_color="white").pack(anchor="w", padx=10, pady=(5, 0))
        ctk.CTkLabel(card, textvariable=var, font=("Segoe UI", 16, "bold"), text_color="white").pack(anchor="w", padx=10, pady=(0, 5))


    def _show_announcements(self):
        for w in self.announcement_container.winfo_children():
            w.destroy()

        for ann in self.default_announcements:
            card = ctk.CTkButton(
                self.announcement_container,
                text=ann.split("\n")[0],
                anchor="w",
                fg_color="#374151",
                hover_color="#4b5563",
                corner_radius=12,
                height=60,
                command=lambda a=ann: self.show_announcement_popup(a)
            )
            card.pack(fill="x", pady=6)


    def show_announcement_popup(self, text):
        popup = ctk.CTkToplevel(self)
        popup.title("Announcement")
        popup.geometry("450x350")
        popup.resizable(False, False)
        popup.configure(fg_color="#111827")
        popup.grab_set()

        ctk.CTkLabel(
            popup,
            text="ANNOUNCEMENT DETAILS",
            font=("Segoe UI", 18, "bold"),
            text_color="#facc15"
        ).pack(pady=(15, 10))

        card = ctk.CTkFrame(
            popup,
            fg_color="#1f2937",
            corner_radius=15
        )
        card.pack(fill="both", expand=True, padx=15, pady=10)

        box = ctk.CTkTextbox(card, width=380, height=200, fg_color="transparent")
        box.pack(pady=10, padx=10)
        box.insert("0.0", text)
        box.configure(state="disabled")

        ctk.CTkButton(
            popup,
            text="Close",
            fg_color="#dc2626",
            hover_color="#991b1b",
            command=popup.destroy
        ).pack(pady=(0, 15))

    def _build_reminders(self):
        card = ctk.CTkFrame(
            self.right_scroll,
            fg_color="#111827",
            corner_radius=15
        )
        card.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            card,
            text=" Quick Reminders",
            font=("Segoe UI", 14, "bold")
        ).pack(pady=8)

        reminders = [
            "Bring valid ID",
            "Check appointment status",
            "Arrive 15 minutes early",
            "Keep queue number safe"
        ]

        for item in reminders:
            ctk.CTkLabel(
                card,
                text=f"• {item}",
                text_color="#9ca3af"
            ).pack(anchor="w", padx=12, pady=2)

    def _build_services(self):
        card = ctk.CTkFrame(
            self.right_scroll,
            fg_color="#111827",
            corner_radius=15
        )
        card.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            card,
            text=" Available Services",
            font=("Segoe UI", 14, "bold")
        ).pack(pady=8)

        services = [
            "Barangay Clearance",
            "PWD ID",
            "Senior Citizen ID",
            "Certificate of Residency",
            "Business Permit",
            "Indigency Certificate",
            "Barangay Construction Clearance",
            "Barangay Calamity Certification",
            "First-Time Jobseeker Certificate",
            "Barangay ID"
        ]

        for item in services:
            ctk.CTkLabel(
                card,
                text=f"• {item}",
                text_color="#9ca3af"
            ).pack(anchor="w", padx=12, pady=2)

    def check_appointment_status(self):
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT id, status FROM appointments 
                WHERE username=%s AND status='Pending' 
                ORDER BY id DESC LIMIT 1
            """, (self.app.username,))
            
            pending_row = cursor.fetchone()
            

            if pending_row:
                self.active_pending_id = pending_row['id']
                self.show_cancel_button()
            else:
                self.active_pending_id = None
                self.hide_cancel_button()

        except Exception as e:
            print("ERROR sa check_appointment_status:", e)
        finally:
            if conn: conn.close()

    def show_cancel_button(self):
        
        if not hasattr(self, 'cancel_btn'):
            self.cancel_btn = ctk.CTkButton(
                self.status_box, 
                text="View Details & Cancel", 
                fg_color="#f59e0b", 
                hover_color="#d97706",
                command=self.open_details_modal 
            )
            self.cancel_btn.pack(pady=10)

    def hide_cancel_button(self):
        if hasattr(self, 'cancel_btn'):
            self.cancel_btn.destroy()
            del self.cancel_btn

    def open_details_modal(self):
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM appointments WHERE id=%s", (self.active_pending_id,))
        data = cur.fetchone()
        cur.close()
        conn.close()

        if not data:
            return
        
        modal = ctk.CTkToplevel(self)
        modal.title("Appointment Details")
        modal.geometry("400x400")
        modal.grab_set()

        ctk.CTkLabel(
            modal,
            text="APPOINTMENT DETAILS",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=20)
        
        details_text = (
            f"Service: {data['document_type']}\n\n"
            f"Date: {data['appointment_date']}\n\n"
            f"Time: {data['appointment_time']}\n\n"
            f"Status: {data['status']}"
        )
        ctk.CTkLabel(
            modal,
            text=details_text,
            justify="left",
            font=("Segoe UI", 14)
        ).pack(pady=10)

        def do_cancel():
            reason_modal = ctk.CTkToplevel(self)
            reason_modal.title("Cancel Appointment")
            reason_modal.geometry("350x250")
            reason_modal.grab_set()

            ctk.CTkLabel(
                reason_modal,
                text="Why are you cancelling?",
                font=("Segoe UI", 16, "bold")
            ).pack(pady=15)

            reason_var = ctk.StringVar(value="Select reason")

            dropdown = ctk.CTkComboBox(
                reason_modal,
                values=[
                    "Schedule conflict",
                    "Not available on date",
                    "Found alternative",
                    "Emergency",
                    "Other"
                ],
                variable=reason_var
            
            )
            dropdown.pack(pady=10, fill="x", padx=20)

            def confirm():
                reason = reason_var.get()

                if reason == "Select reason":
                    messagebox.showwarning("Required", "Select reason")
                    return

                self.execute_cancel(self.active_pending_id, reason)


                reason_modal.destroy()
                modal.destroy()

            ctk.CTkButton(
                reason_modal,
                text="Confirm",
                command=confirm
            ).pack()

        ctk.CTkButton(
            modal,
            text="Cancel Appointment",
            fg_color="red",
            command=do_cancel
        ).pack(pady=20)
    
   
    def execute_cancel(self, appt_id, reason):
        if not appt_id:
            messagebox.showerror("Error", "No appointments selected.")
            return

        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()

      
            cur.execute("""
                UPDATE appointments
                SET status='Cancelled by Resident',
                    reason=%s
                WHERE id=%s
            """, (reason, appt_id))

        
            cur.execute("SELECT queue_id FROM appointments WHERE id=%s", (appt_id,))
            row = cur.fetchone()

            if row:
                queue_id = row[0]

                cur.execute("""
                    UPDATE queue_status 
                    SET status='Cancelled'
                    WHERE queue_no=%s
                """, (queue_id,))

            conn.commit()

            messagebox.showinfo("Success", "Appointment cancelled successfully.")

        # refresh UI
            self.check_appointment_status()
            self.check_queue_status()
            self.update_stats_from_db()

        except Exception as e:
            print("CANCEL ERROR:", e)
            messagebox.showerror("Error", str(e))

        finally:
            if conn:
                conn.close()

   
    def fetch_latest_queue_status(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT queue_no, position, now_serving, status
                FROM queue_status
                ORDER BY id DESC
                LIMIT 1
            """)

            data = cursor.fetchone()

            cursor.close()
            conn.close()

            return data
        except Exception as e:
            print("QUEUE FETCH ERROR:", e)
            return None

    def check_queue_status(self):
        try:
            data = self.fetch_latest_queue_status()

            if not data:
                self.update_latest_status("No data", "--", "--", "--")
                return
            
            if data.get("status") == "Cancelled":
                self.update_latest_status("Cancelled", "--", "--", "--")
            else:
                self.update_latest_status(
                    data.get("status", "--"),
                    data.get("queue_no", "--"),
                    data.get("position", "--"),
                    data.get("now_serving", "--")
                )

        except Exception as e:
            print("QUEUE CHECK ERROR:", e)

    def update_latest_status(self, latest, queue, position, now_serving):
        self.lbl_latest.configure(text=latest)
        self.lbl_queue.configure(text=f"Queue: {queue}")
        self.lbl_position.configure(text=f"Position: {position}")
        self.lbl_now.configure(text=f"Now Serving: {now_serving}")

    
    def auto_refresh(self):
        if self.winfo_exists():
            self.check_appointment_status()
            self.check_queue_status()
            self.update_stats_from_db()
            self.after(8000, self.auto_refresh)
