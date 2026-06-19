import customtkinter as ctk
from db_config import get_db_connection


class AdminDashboard(ctk.CTkFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color="transparent")
        self.tkraise()
        self.app = app_controller
        self.running = True
        self.is_loading = False
        self.pack(fill="both", expand=True, padx=10, pady=5)

        ctk.CTkLabel(
            self, 
            text="Admin Dashboard", 
            font=("Segoe UI", 28, "bold"), 
            text_color="white"
        ).pack(anchor="w", padx=20, pady=(10, 5))

        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.pack(fill="x")

        
        self.label = ctk.CTkLabel(
            self,
            text="Admin Dashboard Content",
            font=("Segoe UI", 20)
        )
        self.label.pack(pady=5)

        

        self.pending_lbl = self.create_card("Pending", "#f39c12")
        self.approved_lbl = self.create_card("Approved", "#27ae60")
        self.cancelled_lbl = self.create_card("Cancelled", "#e74c3c")
        self.rejected_lbl = self.create_card("Rejected", "#e67e22")
        self.residents_lbl = self.create_card("Residents", "#3498db")

        for lbl in [
            self.pending_lbl,
            self.approved_lbl,
            self.cancelled_lbl,
            self.rejected_lbl,
            self.residents_lbl
        ]:
            lbl.pack(side="left", expand=True, fill="x", padx=8)

        
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, pady=15)

       
        self.activity_frame = ctk.CTkFrame(self.content, fg_color="#222", corner_radius=15)
        self.activity_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self.activity_frame.pack_propagate(False)

        
        ctk.CTkLabel(self.activity_frame, text="Dashboard Overview", font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=15, pady=10)

        
        self.overview_frame = ctk.CTkFrame(self.activity_frame, fg_color="transparent", height=120)
        self.overview_frame.pack(fill="x", padx=10, pady=5)

        
        self.activity_list = ctk.CTkScrollableFrame(self.activity_frame, fg_color="transparent")
        self.activity_list.pack(fill="both", expand=True, padx=10, pady=10)   

       
        self.right_panel = ctk.CTkFrame(self.content, fg_color="#222", corner_radius=15)
        self.right_panel.pack(side="right", fill="both", expand=True)

        ctk.CTkLabel(
            self.right_panel,
            text="Today's Appointments",
            font=("Segoe UI", 18, "bold"),
            text_color="white"
        ).pack(pady=10)

        self.today_list = ctk.CTkScrollableFrame(self.right_panel, fg_color="#1a1a1a")
        self.today_list.pack(fill="both", expand=True, padx=10, pady=5)

      
        
        self.btn_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.btn_frame.pack(fill="x", padx=10, pady=5)

        self.btn_frame.grid_columnconfigure(0, weight=1)
        self.btn_frame.grid_columnconfigure(1, weight=1)

        
        def create_btn(text, cmd, color, row, col, colspan=1):
            ctk.CTkButton(self.btn_frame, text=text, command=cmd, fg_color=color, height=35).grid(
                row=row, column=col, columnspan=colspan, padx=5, pady=5, sticky="ew"
            )

        create_btn("NEXT NOW SERVING", self.next_now_serving, "#16a34a", 0, 0, 2)
        create_btn("View Pending", self.view_pending, "#707823", 1, 0)
        create_btn("Approve All Pending", self.approve_pending, "#27ae60", 1, 1)
        create_btn("View Residents", self.view_residents, "#3498db", 2, 0)
        create_btn("View All Appointments", self.view_appointments, "#6c757d", 2, 1)
        create_btn("Skip Current", self.skip_current, "#f59e0b", 3, 0)
        create_btn("Mark Done", self.mark_done, "#2563eb", 3, 1)
        create_btn("Reset Queue", self.reset_queue, "#dc2626", 4, 0, 2)

        self.load_all()
        self.auto_refresh()

    def create_card(self, title, color):
        frame = ctk.CTkFrame(self.cards_frame, fg_color=color, corner_radius=15, height=100)
        frame.pack_propagate(False)

        ctk.CTkLabel(frame, text=title,
                     font=("Segoe UI", 14, "bold"),
                     text_color="white").pack(pady=(15, 0))

        label = ctk.CTkLabel(frame, text="0",
                             font=("Segoe UI", 24, "bold"),
                             text_color="white")
        label.pack()

        frame.label = label
        return frame

    
    def load_all(self):
        print("Loading all data...")
        if self.is_loading:
            return
        self.is_loading = True
        try:
            self.load_stats()
            self.load_activity()
            self.load_today()
            self.load_overview()
        except Exception as e:
            print(f"CRITICAL UI ERROR: {e}")
        finally:
            self.is_loading = False
      

    def refresh_all(self):
        if self.is_loading:
            return
        self.load_all()

    def load_stats(self):
        conn = get_db_connection()
        if not conn:
            return

        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM appointments WHERE LOWER(status)='pending'")
            self.pending_lbl.label.configure(text=cursor.fetchone()[0])

            cursor.execute("SELECT COUNT(*) FROM appointments WHERE LOWER(status)='approved'")
            self.approved_lbl.label.configure(text=cursor.fetchone()[0])

            cursor.execute("SELECT COUNT(*) FROM appointments WHERE LOWER(status)='cancelled'")
            self.cancelled_lbl.label.configure(text=cursor.fetchone()[0])

            cursor.execute("SELECT COUNT(*) FROM appointments WHERE LOWER(status)='rejected'")
            self.rejected_lbl.label.configure(text=cursor.fetchone()[0])

            cursor.execute("SELECT COUNT(*) FROM users")
            self.residents_lbl.label.configure(text=cursor.fetchone()[0])

        finally:
            cursor.close()
            conn.close()

    def load_activity(self):
        # 1. Burahin ang dating laman
        for w in self.activity_list.winfo_children():
            w.destroy()

        conn = get_db_connection()
        if not conn:
            return

        cursor = conn.cursor(dictionary=True)
        try:
            
            query = """
                SELECT 
                    al.action, 
                    al.timestamp, 
                    COALESCE(u.full_name, 'Unknown') AS fullname, 
                    COALESCE(a.document_type, 'N/A') AS document_type
                FROM activity_logs al
                LEFT JOIN users u ON al.username = u.username
                LEFT JOIN appointments a ON al.details = a.id
                ORDER BY al.timestamp DESC 
                LIMIT 10
            """
            cursor.execute(query)

            for r in cursor.fetchall():
                box = ctk.CTkFrame(self.activity_list, fg_color="#1E293B", corner_radius=10)
                box.pack(fill="x", pady=5, padx=10)

                
                log_text = f"{r['fullname']} - {r['action']} ({r['document_type']})"
                
                ctk.CTkLabel(
                    box, text=log_text, font=("Segoe UI", 12, "bold"), text_color="#F8FAFC"
                ).pack(anchor="w", padx=10, pady=(8, 0))

                
                time_val = r['timestamp']
                time_str = time_val.strftime("%I:%M %p") if time_val else "N/A"
                
                ctk.CTkLabel(
                    box, text=f"({time_str})", font=("Segoe UI", 10), text_color="#94A3B8"
                ).pack(anchor="w", padx=10, pady=(0, 8))

        except Exception as e:
            print(f"Error sa load_activity: {e}")
        finally:
            cursor.close()
            conn.close()
    

    def load_today(self):
        for w in self.today_list.winfo_children():
            w.destroy()

        conn = get_db_connection()
        if not conn:
            return

        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT * FROM appointments
                WHERE DATE(appointment_date) = CURDATE()
            """)

            rows = cursor.fetchall()


            for r in rows:
                data = dict(r)

                frame = ctk.CTkFrame(self.today_list, fg_color="#2a2a2a", corner_radius=10)
                frame.pack(fill="x", pady=5, padx=5)

        
                ctk.CTkLabel(
                    frame,
                    text=data["fullname"],
                    font=("Segoe UI", 13, "bold")
                ).pack(anchor="w", padx=10, pady=(5, 0))

                ctk.CTkLabel(
                    frame,
                    text=data["document_type"],
                    font=("Segoe UI", 11),
                    text_color="gray"
                ).pack(anchor="w", padx=10)

           
                def bind_click(widget, row=data):
                    widget.bind("<Button-1>", lambda e: self.show_appointment_details(row))

                bind_click(frame)

                for child in frame.winfo_children():
                    bind_click(child)

        finally:
            cursor.close()
            conn.close()
    def show_appointment_details(self, data):
       
        details_win = ctk.CTkToplevel(self)
        details_win.title("Appointment Details")
        details_win.geometry("400x450")
        details_win.attributes("-topmost", True) 

        ctk.CTkLabel(details_win, text="Appointment Information", font=("Segoe UI", 20, "bold")).pack(pady=20)

        fields = [("Full Name", "fullname"), ("Type", "document_type"), 
                  ("Date", "appointment_date"), ("Status", "status")]

        for label_text, key in fields:
            frame = ctk.CTkFrame(details_win, fg_color="transparent")
            frame.pack(fill="x", padx=20, pady=5)
            ctk.CTkLabel(frame, text=f"{label_text}:", font=("Segoe UI", 12, "bold")).pack(side="left")
            ctk.CTkLabel(frame, text=str(data.get(key, "N/A")), font=("Segoe UI", 12)).pack(side="right")

        ctk.CTkButton(details_win, text="Close", command=details_win.destroy, fg_color="#e74c3c").pack(pady=30)

    def open_review_window(self, data):
        review_win = ctk.CTkToplevel(self)
        review_win.title("Review Appointment")
        review_win.geometry("350x400")
        review_win.attributes("-topmost", True)

        ctk.CTkLabel(review_win, text="Review Details", font=("Segoe UI", 16, "bold")).pack(pady=15)

       
        fields = [("Name", "fullname"), ("Type", "document_type"), ("Purpose", "purpose"), ("Date", "appointment_date")]
        for label, key in fields:
            f = ctk.CTkFrame(review_win, fg_color="transparent")
            f.pack(fill="x", padx=20, pady=2)
            ctk.CTkLabel(f, text=f"{label}:", font=("Segoe UI", 11, "bold")).pack(side="left")
            ctk.CTkLabel(f, text=str(data.get(key, "N/A"))).pack(side="right")

      
        ctk.CTkButton(
            review_win, text="Approve Appointment", fg_color="#27ae60",
            command=lambda: [self.approve_single_appointment(data['id']), review_win.destroy()]
        ).pack(pady=20) 

    def get_pending_count_from_db(self):
        
        conn = get_db_connection()
        if not conn:
            return 0
        
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM appointments WHERE LOWER(status)='pending'")
            result = cursor.fetchone()
            return result[0] if result else 0
        
        
        except Exception as e:
            print(f"Error getting pending count: {e}")
            return 0
        finally:
            cursor.close()
            conn.close()

    def get_emergency_count_from_db(self):
        conn = get_db_connection()
        if not conn:
            return 0

        cursor = conn.cursor()
        try:
            cursor.execute("SELECT status FROM emergency_reports")
            statuses = cursor.fetchall()
            print(f"DEBUG: Lahat ng status sa DB: {statuses}")

            cursor.execute("SELECT COUNT(*) FROM emergency_reports WHERE status='Pending'")
            result = cursor.fetchone()
            
            # Siguraduhing may balik na resulta
            return result[0] if result else 0
            
        except Exception as e:
            print(f"Error getting emergency count: {e}")
            return 0
        finally:
            cursor.close()
            conn.close()
            
    def auto_refresh(self):
        print("DEBUG: Auto-refresh heartbeat...")
        if not self.winfo_exists() or not self.running:
            return

        try:
       
            p_count = self.get_pending_count_from_db()
            self.app.set_notification("Appointments", p_count > 0)
            
            e_count = self.get_emergency_count_from_db()
            print(f"DEBUG: Emergency Count found: {e_count}")
            self.app.set_notification("Emergency", e_count > 0)

        except Exception as e:
            print(f"Error sa notifications: {e}")
        try:
            self.load_activity()
            self.load_overview()

            if hasattr(self, 'today_list') and self.today_list.winfo_exists():
                is_in_custom_view = any(
                    isinstance(w, ctk.CTkButton) and w.cget("text") == "← Back to Today's"
                    for w in self.today_list.winfo_children()
                )
                if not is_in_custom_view:
                    self.load_today()
        except Exception as e:
            print(f"Error sa UI rendering: {e}")

        self.after(15000, self.auto_refresh)


    def stop(self):
        self.running = False
        conn = get_db_connection()

        if not conn:
            return
        
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO activity_logs(username, action)
                VALUES(%s,%s)
            """, ("admin", "Skipped Current Queue"))
            
            cursor.execute("UPDATE queue_status SET status='Skipped' WHERE status='Serving'")

            conn.commit()
            

        finally:
            cursor.close()
            conn.close()

    def mark_done(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO activity_logs(username, action)
                VALUES(%s,%s)
            """, ("admin", "Marked Current Queue Done"))
            
            cursor.execute("UPDATE queue_status SET status='Done' WHERE status='Serving'")

            cursor.execute("SELECT * FROM queue_status WHERE status='Pending' ORDER BY id ASC LIMIT 1")
            next_q = cursor.fetchone()
            conn.commit()
            self.load_all()
        finally:
            cursor.close()
            conn.close()

    def skip_current(self):
        conn = get_db_connection()
        if not conn: return
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE queue_status SET status='Skipped' WHERE status='Serving'")
            cursor.execute("INSERT INTO activity_logs(username, action) VALUES(%s, %s)", ("admin", "Skipped Current Appointment"))
            self.load_all()
            self.load_today() 
        except Exception as e:
            print(f"Error sa skip_current: {e}")
        finally:
            cursor.close()
            conn.close()

    def reset_queue(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO activity_logs(username, action)
                VALUES(%s,%s)
            """, ("admin", "Reset Queue"))
            
            cursor.execute("DELETE FROM queue_status")
            conn.commit()
            self.load_all()
        finally:
            cursor.close()
            conn.close()

    def next_now_serving(self):
        conn = get_db_connection()
        if not conn:
            return

        cursor = conn.cursor(dictionary=True)

        try:
        
            cursor.execute("""
                UPDATE queue_status
                SET status='Done'
                WHERE status='Serving'
            """)

        
            cursor.execute("""
                SELECT * FROM queue_status
                WHERE status='Pending'
                ORDER BY id ASC
                LIMIT 1
            """)

            next_q = cursor.fetchone()

            if not next_q:
                conn.commit()
                print("Wala nang pending sa queue.")
                return

        
            cursor.execute("""
                UPDATE queue_status 
                SET status='Serving', now_serving=%s 
                WHERE id=%s
            """, (next_q["queue_no"], next_q["id"]))

        
            cursor.execute("""
                INSERT INTO activity_logs(username, action, details) 
                VALUES(%s, %s, %s)
            """, ("admin", "Next Serving", str(next_q["id"])))

            self.load_all()
            self.load_today()
        except Exception as e:
            print(f"Error sa next_now_serving: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

    def approve_pending(self):
        conn = get_db_connection()
        if not conn:
            return

        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE appointments
                SET status='approved'
                WHERE LOWER(status)='pending'
            """)

            cursor.execute("""
            INSERT INTO activity_logs(username, action)
            VALUES(%s,%s)
            """, ("admin", "Approved All Pending Appointments"))
            
            conn.commit()
            self.load_all()
        finally:
            cursor.close()
            conn.close()

    def view_residents(self):
        
        for w in self.today_list.winfo_children():
            w.destroy()

        ctk.CTkButton(
            self.today_list, 
            text="← Back to Today's", 
            fg_color="#555", 
            height=25,
            command=self.load_today
        ).pack(fill="x", pady=(0, 10))

       
        conn = get_db_connection()
        if not conn:
            return

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT username, full_name, city, barangay
                FROM users
                WHERE role='resident'
            """)

         
            for r in cursor.fetchall():
                box = ctk.CTkFrame(self.today_list, fg_color="#333", corner_radius=10)
                box.pack(fill="x", padx=10, pady=5)
                
             
                ctk.CTkLabel(box, text=r["full_name"], font=("Segoe UI", 13, "bold"), text_color="white").pack(anchor="w", padx=10, pady=(10, 0))
                ctk.CTkLabel(box, text=f"{r['city']} - {r['barangay']}", text_color="gray").pack(anchor="w", padx=10, pady=(0, 10))

        finally:
            cursor.close()
            conn.close()

    def view_appointments(self):
        for w in self.today_list.winfo_children():
            w.destroy()

        ctk.CTkButton(
            self.today_list, 
            text="← Back to Today's", 
            fg_color="#555", 
            height=25,
            command=self.load_today
        ).pack(fill="x", pady=(0, 10))

        conn = get_db_connection()
        if not conn:
            return

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT fullname, document_type, status, appointment_date FROM appointments")
            
            for r in cursor.fetchall():
                
                box = ctk.CTkFrame(self.today_list, fg_color="#333", corner_radius=10)
                box.pack(fill="x", padx=10, pady=5)

               
                ctk.CTkLabel(box, text=r["fullname"], font=("Segoe UI", 13, "bold"), text_color="white").pack(anchor="w", padx=10, pady=(5, 0))
                ctk.CTkLabel(box, text=f"{r['document_type']} | {r['appointment_date']}", text_color="gray").pack(anchor="w", padx=10)
                ctk.CTkLabel(box, text=f"Status: {r['status']}", text_color="#3498db").pack(anchor="w", padx=10, pady=(0, 5))

        finally:
            cursor.close()
            conn.close()
            
    def approve_single_appointment(self, app_id):
        conn = get_db_connection()
        if not conn:
            return

        cursor = conn.cursor()

        try:
       
            cursor.execute(
                "UPDATE appointments SET status='approved' WHERE id=%s",
                (app_id,)
            )

            cursor.execute("""
                INSERT INTO activity_logs(username, action)
                VALUES(%s,%s)
            """, ("admin", f"Approved Appointment ID {app_id}"))

            conn.commit()

        
            self.load_stats()
            self.load_activity()
            self.load_today()

        finally:
            cursor.close()
            conn.close()

    def view_pending(self):
        for w in self.today_list.winfo_children():
             w.destroy()

        ctk.CTkButton(
            self.today_list, 
            text="← Back to Today's", 
            fg_color="#555", 
            height=25,
            command=self.load_today
        ).pack(fill="x", pady=(0, 10))

        conn = get_db_connection()
        if not conn:
            return

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT id, fullname, document_type, appointment_date 
                FROM appointments 
                WHERE LOWER(status)='pending'
            """)
            
           
            ctk.CTkLabel(self.today_list, text="Pending Appointments", 
                         font=("Segoe UI", 14, "bold")).pack(pady=5)

            for r in cursor.fetchall():
                
             
                box = ctk.CTkFrame(self.today_list, fg_color="#333", corner_radius=10)
                box.pack(fill="x", padx=10, pady=5)

               
                info_frame = ctk.CTkFrame(box, fg_color="transparent")
                info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

                ctk.CTkLabel(info_frame, text=r["fullname"], font=("Segoe UI", 13, "bold"), text_color="white").pack(anchor="w")
                ctk.CTkLabel(info_frame, text=f"Doc: {r['document_type']} | Date: {r['appointment_date']}", text_color="gray").pack(anchor="w")

                ctk.CTkButton(
                    box, 
                    text="Approve", 
                    width=70, 
                    height=30, 
                    fg_color="#27ae60", 
                    command=lambda app_id=r['id']: self.approve_single_appointment(app_id)
                ).pack(side="right", padx=10)

        finally:
            cursor.close()
            conn.close()

    def load_overview(self):
        for w in self.overview_frame.winfo_children():
            w.destroy()

        conn = get_db_connection()
        if not conn: return
        cursor = conn.cursor(dictionary=True)

        try:
       
            cursor.execute("SELECT gender, COUNT(*) as count FROM users WHERE role='resident' GROUP BY gender")
            gender_data = cursor.fetchall()
        
            cursor.execute("SELECT COUNT(*) as total FROM users WHERE role='resident'")
            total_residents = cursor.fetchone()['total'] or 0
        
            cursor.execute("SELECT fullname, document_type FROM appointments WHERE status='approved' ORDER BY id DESC LIMIT 1")
            latest = cursor.fetchone()
        
        
            cursor.execute("SELECT COUNT(*) as total FROM appointments WHERE status='pending'")
            pending_data = cursor.fetchone()
            pending_count = pending_data['total'] if pending_data else 0

       
            self.overview_frame.grid_columnconfigure((0, 1), weight=1)
            self.overview_frame.grid_rowconfigure((0, 1), weight=1)

       
            def create_card(row, col, title, value, subtext, color):
                frame = ctk.CTkFrame(self.overview_frame, fg_color="#1E293B", corner_radius=10)
                frame.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
                ctk.CTkLabel(frame, text=title, font=("Segoe UI", 10, "bold"), text_color="gray").pack(pady=(5, 0))
                ctk.CTkLabel(frame, text=value, font=("Segoe UI", 16, "bold"), text_color=color).pack()
                ctk.CTkLabel(frame, text=subtext, font=("Segoe UI", 9)).pack(pady=(0, 5))
                return frame

        
            card1 = create_card(0, 0, "TOTAL RESIDENTS", str(total_residents), "Active Members", "white")
       

        
            latest_val = latest["fullname"] if latest and "fullname" in latest else "N/A"
            latest_sub = latest["document_type"] if latest and "document_type" in latest else "None"
            create_card(0, 1, "LATEST APPROVED", latest_val, latest_sub, "#27ae60")

        
            create_card(1, 0, "PENDING REQUESTS", str(pending_count), "Need Action", "#f39c12")

            create_card(1, 1, "SYSTEM STATUS", "Online", "Synced", "#3498db")

        except Exception as e:
            print(f"Error sa load_overview: {e}")
        finally:
            cursor.close()
            conn.close()