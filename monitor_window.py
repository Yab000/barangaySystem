import customtkinter as ctk
from tkinter import messagebox
from db_config import get_db_connection



class DetailsView(ctk.CTkToplevel):

    def __init__(self, master, data):
        super().__init__(master)
        self.title("Appointment Details")
        self.geometry("400x450")
        self.grab_set()

        ctk.CTkLabel(self, text="Queue Details", font=("Segoe UI", 20, "bold")).pack(pady=15)
        fields = ["Fullname", "Document_type", "Contact", "Age", "Status"]
        for field in fields:
            val = data.get(field.lower(), "N/A")
            frame = ctk.CTkFrame(self, fg_color="transparent")
            frame.pack(fill="x", padx=20, pady=5)
            ctk.CTkLabel(frame, text=f"{field}:", font=("Segoe UI", 12, "bold")).pack(side="left")
            ctk.CTkLabel(frame, text=str(val), font=("Segoe UI", 12)).pack(side="right")
        
        ctk.CTkButton(self, text="Close", command=self.destroy).pack(pady=20)

class MonitorDashboard(ctk.CTkFrame):

    def __init__(self, master, app_controller):
        super().__init__(master, fg_color="#0f0f0f")

        self.app = app_controller
        self.running = True
        self.last_data_count = -1
        self.seen_appointments = {}

        self.pack(fill="both", expand=True, padx=20, pady=20)

        
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            header,
            text="Live Queue Monitor",
            font=("Segoe UI", 28, "bold"),
            text_color="white"
        ).pack(side="left")

        self.search_entry = ctk.CTkEntry(header, placeholder_text="Search name...", width=200)
        self.search_entry.pack(side="right", padx=10)
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_queue())

       
        self.scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="#121212",
            corner_radius=12
        )
        self.scroll.pack(fill="both", expand=True)

        self.load_queue()
        self.auto_refresh()

   
    def delete_appointment(self, appointment_id):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this queue item?"):
            conn = None
            try:
                conn = get_db_connection()
                if conn:
                    cur = conn.cursor()
                    cur.execute("DELETE FROM appointments WHERE id = %s", (appointment_id,))
                    conn.commit()
                    cur.close()

                self.last_data_count = -1
                self.load_queue()

            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete: {e}")

            finally:
                if conn:
                    conn.close()
    def open_details(self, appointment_id):
        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM appointments WHERE id = %s", (appointment_id,))
            data = cur.fetchone()
            cur.close()
            
            if data:
                DetailsView(self, data)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load details: {e}")
        finally:
            if conn: conn.close()

   
    def load_queue(self):

        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return

            cur = conn.cursor(dictionary=True)

            search_query = self.search_entry.get().strip()

            if search_query:
                sql = """
                    SELECT * FROM appointments
                    WHERE fullname LIKE %s
                    AND status IN ('Pending', 'Approved')
                    ORDER BY FIELD(status,'Pending','Approved'), id DESC
                """
                cur.execute(sql, (f"%{search_query}%",))
            else:
                sql = """
                    SELECT * FROM appointments
                    WHERE status IN ('Pending', 'Approved')
                    ORDER BY FIELD(status,'Pending','Approved'), id DESC
                """
                cur.execute(sql)

            rows = cur.fetchall()
            cur.close()

            if len(rows) == self.last_data_count and not search_query:
                return

            self.last_data_count = len(rows)

            for w in self.scroll.winfo_children():
                w.destroy()

            if not rows:
                empty_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
                empty_frame.pack(pady=50)

                ctk.CTkLabel(empty_frame, text="📭", font=("Segoe UI", 60)).pack()
                ctk.CTkLabel(empty_frame, text="No pending appointments", font=("Segoe UI", 18, "bold"), text_color="gray").pack(pady=10)
                ctk.CTkLabel(empty_frame, text="All systems are clear.", font=("Segoe UI", 13), text_color="#555555").pack()
                return

            for i, row in enumerate(rows, 1):

                status = (row.get("status") or "Pending").upper()
                color = "#f39c12" if status == "PENDING" else "#27ae60"

                card = ctk.CTkFrame(self.scroll, fg_color="#1e1e1e", corner_radius=15, height=90)
                card.pack(fill="x", pady=8, padx=8)
                card.pack_propagate(False)

                top = ctk.CTkFrame(card, fg_color="transparent")
                top.pack(fill="x", padx=15, pady=(10, 0))

                ctk.CTkLabel(
                    top,
                    text=f"#{i} {row.get('fullname', 'Unknown')}",
                    font=("Segoe UI", 16, "bold"),
                    text_color="white"
                ).pack(side="left")

                ctk.CTkButton(
                    top,
                    text="Delete",
                    fg_color="transparent",
                    text_color="red",
                    width=50,
                    command=lambda id=row['id']: self.delete_appointment(id)
                ).pack(side="right", padx=5)

                ctk.CTkButton(
                    top,
                    text="View",
                    fg_color="#3498db",
                    text_color="white",
                    width=50,
                    command=lambda id=row['id']: self.open_details(id)
                ).pack(side="right", padx=5)

                bottom = ctk.CTkFrame(card, fg_color="transparent")
                bottom.pack(fill="x", padx=15)

                ctk.CTkLabel(
                    bottom,
                    text=row.get("document_type", "N/A"),
                    font=("Segoe UI", 13),
                    text_color="#a1a1a1"
                ).pack(side="left")

                ctk.CTkLabel(
                    card,
                    text=status,
                    fg_color=color,
                    text_color="white",
                    corner_radius=10,
                    font=("Segoe UI", 12, "bold"),
                    width=110,
                    height=28
                ).pack(side="right", padx=15, pady=15)
              
                app_id = row.get('id')
                current_status = status 


                if app_id not in self.seen_appointments or self.seen_appointments[app_id] != current_status:
                    self.seen_appointments[app_id] = current_status
                    if self.last_data_count != -1:
                        try:
                            self.app.push_notification(f"Queue Update: {row.get('fullname')} is now {current_status}", "info")
                        except:
                            pass

                

        except Exception as e:
            print("Queue Load Error:", e)

        finally:
            if conn:
                conn.close()

   
    def auto_refresh(self):
        if self.running and self.winfo_exists():
            self.load_queue()
            self.after(3000, self.auto_refresh)