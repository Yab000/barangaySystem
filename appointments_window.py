import customtkinter as ctk
from tkinter import messagebox
from db_config import get_db_connection
from db_utils import add_history


class AppointmentsDashboard(ctk.CTkFrame):

    def __init__(self, master, app_controller):
        super().__init__(master, fg_color="#181818")
        self.pack(fill="both", expand=True)

        self.app = app_controller

        
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x")

        ctk.CTkLabel(
            header,
            text="APPOINTMENTS",
            font=("Segoe UI", 24, "bold")
        ).pack(side="left")

        ctk.CTkButton(
            header,
            text="Refresh",
            command=self.load
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            header,
            text="Delete All",
            fg_color="red",
            command=self.delete_all_appointments
        ).pack(side="right", padx=5)

        
        search = ctk.CTkFrame(self, fg_color="transparent")
        search.pack(fill="x", pady=10)

        self.search_entry = ctk.CTkEntry(search, placeholder_text="Search name")
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", lambda e: self.load())

        self.status_filter = ctk.CTkOptionMenu(search, values=["All", "Pending", "Approved", "Rejected", "Cancelled"], command=lambda e: self.load())
        self.status_filter.pack(side="left", padx=5)

        ctk.CTkButton(
            search,
            text="Clear",
            command=self.clear
        ).pack(side="left", padx=5)

        
        self.frame = ctk.CTkScrollableFrame(self, fg_color="#222")
        self.frame.pack(fill="both", expand=True)

        self.load()

    def open_review_window(self, r):

        review_win = ctk.CTkToplevel(self)
        review_win.title(f"Review: {r.get('fullname')}")
        review_win.geometry("400x600")
        review_win.attributes("-topmost", True)

        
        ctk.CTkLabel(review_win, text="APPOINTMENT DETAILS", font=("Segoe UI", 16, "bold")).pack(pady=15)
        
        
        def add_detail(label, value):
            f = ctk.CTkFrame(review_win, fg_color="transparent")
            f.pack(fill="x", padx=20, pady=2)
            ctk.CTkLabel(f, text=f"{label}:", font=("Segoe UI", 12, "bold")).pack(side="left")
            ctk.CTkLabel(f, text=str(value)).pack(side="right")

        add_detail("Name", r.get('fullname'))
        add_detail("Gender", r.get('gender', 'N/A'))
        add_detail("Type", r.get('document_type'))
        add_detail("Date", r.get('appointment_date'))
        add_detail("Status", r.get('status'))
        add_detail("Purpose", r.get('purpose', 'N/A'))

    
        btn_frame = ctk.CTkFrame(review_win, fg_color="transparent")
        btn_frame.pack(side="bottom", pady=20)

       
        u = self.safe_username(r)
    
        ctk.CTkButton(btn_frame, text="Approve", fg_color="green", width=80,
                    command=lambda: [self.update(r['id'], "Approved", r['appointment_date'], u), review_win.destroy()]).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Reject", fg_color="red", width=80,
                    command=lambda: [self.update(r['id'], "Rejected", r['appointment_date'], u), review_win.destroy()]).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Delete", fg_color="gray", width=80, 
                    command=lambda: [self.delete_appointment(r['id']), review_win.destroy()]).pack(side="left", padx=5)

   
    def get_reason(self, title):
        dialog = ctk.CTkInputDialog(text="Please enter the reason:", title=title)
        reason = dialog.get_input()
        return reason if reason and reason.strip() != "" else None

    def clear(self):
        self.search_entry.delete(0, "end")
        self.load()

    def safe_username(self, r):
        return r.get("fullname") or r.get("username") or self.app.username or "Unknown"

    
    def update(self, id, status, date, user):

        if not messagebox.askyesno("Confirm", f"Mark as {status}?"):
            return

        reason = None
        queue_id = None
        conn = None

        try:
            conn = get_db_connection()
            if not conn:
                return

            cur = conn.cursor(dictionary=True)

            cur.execute("SELECT * FROM appointments WHERE id=%s", (id,))
            r = cur.fetchone()

            if not r:
                return

        
            if status in ["Rejected", "Cancelled"]:
                reason = self.get_reason(f"{status} Reason")
                if not reason:
                    messagebox.showwarning("Input Required", "Reason is required!")
                    return

            cur.execute(
                "UPDATE appointments SET status=%s, reason=%s WHERE id=%s",
                (status, reason, id)
            )

       
            if status == "Approved":

                queue_id = f"Q-{id:04d}"

                try:
                    cur.execute("""
                        INSERT INTO queue (queue_id, appointment_id, status)
                        VALUES (%s, %s, %s)
                    """, (queue_id, id, "waiting"))
                except Exception as q_err:
                    print("QUEUE INSERT ERROR:", q_err)

                try:
                    cur.execute(
                        "UPDATE appointments SET queue_id=%s WHERE id=%s",
                        (queue_id, id)
                    )
                except Exception as e:
                    print("QUEUE ID UPDATE ERROR:", e)

            conn.commit()

       
            add_history(
                self.safe_username(r),
                r.get("document_type"),
                r.get("purpose"),
                status,
                r.get("appointment_date"),
                queue_id if queue_id else "N/A"
            )

            self.load()

        except Exception as e:
            messagebox.showerror("Error", f"Update Failed: {e}")

        finally:
            if conn:
                conn.close()

   
    def delete_appointment(self, appointment_id):

        if not messagebox.askyesno("Confirm", "Delete this appointment?"):
            return

        conn = get_db_connection()
        if not conn:
            return

        try:
            cur = conn.cursor()

            cur.execute("DELETE FROM queue WHERE appointment_id=%s", (appointment_id,))
            cur.execute("DELETE FROM appointments WHERE id=%s", (appointment_id,))

            conn.commit()
            messagebox.showinfo("Deleted", "Appointment deleted!")

            self.load()

        except Exception as e:
            messagebox.showerror("Error", str(e))

        finally:
            if conn:
                conn.close()

    
    def delete_all_appointments(self):

        if not messagebox.askyesno("WARNING", "Delete ALL appointments?"):
            return

        conn = get_db_connection()
        if not conn:
            return

        try:
            cur = conn.cursor()

            cur.execute("DELETE FROM queue")
            cur.execute("DELETE FROM appointments")

            conn.commit()
            messagebox.showinfo("Deleted", "All appointments deleted!")

            self.load()

        except Exception as e:
            messagebox.showerror("Error", str(e))

        finally:
            if conn:
                conn.close()

   
    def load(self):
        for w in self.frame.winfo_children():
            w.destroy()

        conn = get_db_connection()
        if not conn:
            return

        rows = [] 
        try:
            cur = conn.cursor(dictionary=True)
            
            query = "SELECT * FROM appointments WHERE 1=1 " 
            params = []
            if self.search_entry.get().strip():
                query += "AND fullname LIKE %s "
                params.append(f"%{self.search_entry.get().strip()}%")
            if self.status_filter.get() != "All":
                query += "AND status = %s "
                params.append(self.status_filter.get())
            query += "ORDER BY id DESC"
            cur.execute(query, tuple(params))
            rows = cur.fetchall()
        finally:
            if conn: conn.close()

        for r in rows:
           
            card = ctk.CTkFrame(self.frame, fg_color="#333", corner_radius=10)
            card.pack(fill="x", pady=5, padx=5)

            
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

            labels = [
                ctk.CTkLabel(info_frame, text=f"👤 {r.get('fullname', 'Unknown')}", font=("Segoe UI", 14, "bold")),
                ctk.CTkLabel(info_frame, text=f"📄 {r.get('document_type')}"),
                ctk.CTkLabel(info_frame, text=f"⚤ Gender: {r.get('gender', 'N/A')}"),
                ctk.CTkLabel(info_frame, text=f"📅 {r.get('appointment_date')}")
            ]
            for w in labels:
                w.pack(anchor="w")

            status_val = r.get('status', 'Pending')
            color = ("green" if status_val == "Approved" else "red" if status_val == "Rejected" else "orange")
            ctk.CTkLabel(info_frame, text=f"📌 Status: {status_val}", text_color=color).pack(anchor="w")

           
            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(side="right", padx=15)

            ctk.CTkButton(
                btn_frame, 
                text="View Details", 
                width=100,
                fg_color="#2563eb",
                command=lambda data=r: self.open_review_window(data)
            ).pack()