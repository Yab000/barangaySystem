import customtkinter as ctk
from tkinter import messagebox
from db_config import get_db_connection
from datetime import datetime
from tkinter import filedialog
from tkcalendar import DateEntry
import threading


class RequestFormWindow(ctk.CTkFrame):

    def __init__(self, master, app, username, role, extra):
        super().__init__(master)
        self.app = app
        self.username = username
        self.pack(fill="both", expand=True)

       
        self.scroll = ctk.CTkScrollableFrame(self)
        self.scroll.pack(fill="both", expand=True, padx=40, pady=20)

       
        ctk.CTkLabel(
            self.scroll,
            text="CREATE APPOINTMENT",
            font=("Segoe UI", 28, "bold")
        ).pack(pady=20)

      
        self.name_entry = ctk.CTkEntry(self.scroll, placeholder_text="Full Name", height=45)
        self.name_entry.pack(fill="x", pady=8)

        self.gender_entry = ctk.CTkComboBox(self.scroll, values=["Male", "Female"])
        self.gender_entry.set("Select Gender")
        self.gender_entry.pack(fill="x", pady=8)

        self.load_user_info()

        
        self.file_path = ctk.StringVar()

        ctk.CTkButton(
            self.scroll,
            text="Upload Requirement",
            command=self.upload_file
        ).pack(fill="x", pady=8)

        self.file_label = ctk.CTkLabel(
            self.scroll,
            text="No file selected"
        )
        self.file_label.pack(anchor="w")


    def load_user_info(self):

        conn = get_db_connection()
        if not conn:
            return

        cur = conn.cursor(dictionary=True)

        cur.execute("""
            SELECT full_name
            FROM users
            WHERE username=%s
        """, (self.username,))

        row = cur.fetchone()

        if row:
            self.name_entry.insert(0, row["full_name"])

        cur.close()
        conn.close()

       
        self.service = ctk.CTkComboBox(
            self.scroll,
            values=[
                "Barangay Clearance", "Certificate of Residency",
                "Barangay Business Clearance", "Barangay Indigency",
                "Barangay Construction Clearance", "Barangay Calamity Certification",
                "First-Time Jobseeker Certificate", "Barangay ID", "PWD ID", "Senior Citizen ID",
            ],
            height=45
        )
        self.service.set("Select Service")
        self.service.pack(fill="x", pady=8)

        self.service.configure(command=self.show_requirements)

        self.contact_entry = ctk.CTkEntry(self.scroll, placeholder_text="Contact Number", height=45)
        self.contact_entry.pack(fill="x", pady=8)

        self.address_entry = ctk.CTkEntry(self.scroll, placeholder_text="Full Address", height=45)
        self.address_entry.pack(fill="x", pady=8)

        self.date_entry = DateEntry(self.scroll, width=12, height=45, background='#28a745', 
                            foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.date_entry.pack(fill="x", pady=8)   

        self.email_entry = ctk.CTkEntry(self.scroll, placeholder_text="Email Address", height=45)
        self.email_entry.pack(fill="x", pady=8) 

        self.agree_check = ctk.CTkCheckBox(self.scroll, text="I certify that all information provided is true.")
        self.agree_check.pack(anchor="w", pady=10)

        self.time_entry = ctk.CTkComboBox(
            self.scroll,
            values=[
                "08:00 AM", "09:00 AM", "10:00 AM",
                "11:00 AM", "01:00 PM", "02:00 PM", "03:00 PM", "4:00 PM"
            ]
        )
        self.time_entry.set("08:00 AM")
        self.time_entry.pack(fill="x", pady=8)

        self.purpose = ctk.CTkTextbox(self.scroll, height=80)
        self.purpose.pack(fill="x", pady=10)
        self.purpose.insert("0.0", "Type your purpose here...")

        self.requirements_label = ctk.CTkLabel(
            self.scroll,
            text="Requirements will appear here",
            justify="left"
        )
        self.requirements_label.pack(anchor="w", pady=5)

        
        self.submit_btn = ctk.CTkButton(
            self,
            text="SUBMIT APPOINTMENT",
            fg_color="#28a745",
            command=self.submit_appointment
        )
        self.submit_btn.pack(side="bottom", fill="x", padx=40, pady=15)

    def clear_form(self):
        self.name_entry.delete(0, 'end')
        self.contact_entry.delete(0, 'end')
        self.address_entry.delete(0, 'end')
        self.email_entry.delete(0, 'end')
        self.date_entry.delete(0, 'end')
        self.purpose.delete("1.0", "end")
        self.service.set("Select Service")
        self.time_entry.set("08:00 AM")
        self.file_path.set("")
        self.file_label.configure(text="No file selected")
        self.agree_check.deselect()

    def cancel_appointment(self, appointment_id):
        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
        
            cur.execute("UPDATE appointments SET status='Cancelled by Resident' WHERE id=%s", (appointment_id,))
        
            conn.commit()
            cur.close()
        
            messagebox.showinfo("Success", "Appointment cancelled successfully.")
        
            self.load_appointments() 
        
        except Exception as e:
            messagebox.showerror("Error", f"Hindi ma-cancel: {e}")
        finally:
            if conn:
                conn.close()

    
    def show_requirements(self, service):

        reqs = {
            "Barangay Clearance": "• Valid ID\n• Cedula",
            "Certificate of Residency": "• Valid ID\n• Proof of Address",
            "Barangay Business Clearance": "• DTI Permit\n• Valid ID",
            "Barangay Indigency": "• Valid ID\n• Request Letter",
            "First-Time Jobseeker Certificate": "• Valid ID\n• Birth Certificate"
        }

        self.requirements_label.configure(
            text=reqs.get(service, "No requirements listed.")
        )

    
    def upload_file(self):
        file = filedialog.askopenfilename()

        if file:
            self.file_path.set(file)
            self.file_label.configure(text=file.split("/")[-1])

  
    def validate_date(self, date_text):
        try:
            datetime.strptime(date_text, "%Y-%m-%d")
            return True
        except:
            return False

    
    def submit_appointment(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        service = self.service.get().strip()
        contact = self.contact_entry.get().strip()
        date = self.date_entry.get().strip()
        time_val = self.time_entry.get().strip()
        purpose = self.purpose.get("1.0", "end").strip()
        address = self.address_entry.get().strip()

        current_file_path = self.file_path.get()


        if not all([name, service, contact, date, time_val, purpose, address]):
            messagebox.showwarning("Missing", "Fill all fields")
            return
        if self.agree_check.get() == 0:
            messagebox.showwarning("Agreement", "You must agree to the terms.")
            return
        if "@" not in email or "." not in email:
            messagebox.showerror("Error", "Invalid email address")
            return

        if not contact.isdigit() or len(contact) != 11:
            messagebox.showerror("Error", "Invalid contact number")
            return

        if not self.validate_date(date):
            messagebox.showerror("Error", "Invalid date format")
            return

        confirm = messagebox.askyesno(
            "Confirm Appointment",
            f"""
Name: {name}
Service: {service}
Date: {date}
Time: {time_val}

Submit?
"""
        )

        if not confirm:
            return

        self.submit_btn.configure(state="disabled", text="Submitting...")

        threading.Thread(
            target=self.process_db_submission,
            
            args=(name, service, contact, date, time_val, purpose, current_file_path, self.gender_entry.get(), address, email),
            daemon=True
        ).start()

    
    def process_db_submission(self, name, service, contact, date, time_val, purpose, current_file_path, gender, address, email):

        conn = None
        cur = None

        try:
            conn = get_db_connection()
            cur = conn.cursor()

           
            cur.execute("""
                SELECT COUNT(*)
                FROM appointments
                WHERE appointment_date=%s
                AND appointment_time=%s
            """, (date, time_val))

            count = cur.fetchone()[0]
            MAX_SLOT = 5

            if count >= MAX_SLOT:
                self.after(0, lambda: messagebox.showwarning(
                    "Full Slot",
                    "Selected time slot is already full."
                ))
                return
            
           
            cur.execute("""
                SELECT setting_value
                FROM system_settings
                WHERE setting_key='max_daily_appointments'
            """)

            result = cur.fetchone()

            max_limit = int(result[0]) if result else 50

            cur.execute("""
                SELECT COUNT(*)
                FROM appointments
                WHERE appointment_date=%s
            """, (date,))

            daily_count = cur.fetchone()[0]

            if daily_count >= max_limit:
                self.after(0, lambda: messagebox.showwarning(
                    "Limit Reached",
                    f"Maximum of {max_limit} appointments allowed for this day."
                ))
                return

            queue_id = f"Q-{datetime.now().strftime('%H%M%S')}"

            file_path = self.file_path.get()

            cur.execute("""
                INSERT INTO appointments
                (queue_id, fullname, contact, document_type, purpose,
                appointment_date, appointment_time, status, username, file_path, gender, address, email)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                queue_id,
                name,
                contact,
                service,
                purpose,
                date,
                time_val,
                "Pending",
                self.username,
                current_file_path,
                gender,
                address,
                email
            ))

            cur.execute("""
                SELECT COUNT(*)
                FROM appointments
                WHERE status='Pending'
            """)
            position = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO queue_status
                (queue_no, position, now_serving, status)
                VALUES (%s, %s, %s, %s)
            """, (
                queue_id,
                position,
                "---",
                "Pending"
            ))


            cur.execute("""
                INSERT INTO transaction_history
                (username, action, details, queue_id)
                VALUES (%s,%s,%s,%s)
            """, (
                self.username,
                "Appointment Created",
                service,
                queue_id
            ))

            conn.commit()

            self.after(0, self.show_success, queue_id, name, service, date, time_val, address)
            self.after(0, self.clear_form)

        except Exception as e:
           
            self.after(0, lambda err=e: messagebox.showerror("Error", str(err)))

        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

            self.after(0, lambda: self.submit_btn.configure(
                state="normal",
                text="SUBMIT APPOINTMENT"
            ))

    
    def show_success(self, queue_id, name, service, date, time_val, address):
        messagebox.showinfo(
            "Appointment Receipt",
            f"""
SUCCESS!

Queue ID: {queue_id}
Name: {name}
Service: {service}
Date: {date}
Time: {time_val}
Address: {address}
         
Please save this for your reference.
"""
    )