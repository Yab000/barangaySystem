import customtkinter as ctk
from tkinter import messagebox
from db_config import get_db_connection
import mysql.connector
import hashlib



class SearchableDropdown(ctk.CTkFrame):
    def __init__(self, master, values, placeholder="Select", command=None):
        super().__init__(master)

        self.values = values
        self.command = command

        self.var = ctk.StringVar()

        self.entry = ctk.CTkEntry(self, textvariable=self.var, placeholder_text=placeholder)
        self.entry.pack(fill="x", ipady=6)

        self.listbox_frame = ctk.CTkFrame(self, fg_color="#1e1e1e")
        self.listbox_frame.pack(fill="x", pady=(2, 0))
        self.listbox_frame.pack_forget()

        self.items = []

        self.entry.bind("<KeyRelease>", self.filter_list)
        self.entry.bind("<FocusOut>", lambda e: self.listbox_frame.pack_forget())

    def filter_list(self, event=None):
        text = self.var.get().lower()

        for widget in self.items:
            widget.destroy()
        self.items.clear()

        if not text:
            self.listbox_frame.pack_forget()
            return

        filtered = [v for v in self.values if text in v.lower()]

        if not filtered:
            self.listbox_frame.pack_forget()
            return

        self.listbox_frame.pack(fill="x")

        for value in filtered:
            btn = ctk.CTkButton(
                self.listbox_frame,
                text=value,
                fg_color="transparent",
                anchor="w",
                command=lambda v=value: self.select(v)
            )
            btn.pack(fill="x")
            self.items.append(btn)

    def select(self, value):
        self.var.set(value)
        self.listbox_frame.pack_forget()

        if self.command:
            self.command(value)

    def get(self):
        return self.var.get()

    def set(self, value):
        self.var.set(value)



class RegistrationWindow(ctk.CTkToplevel):
    def __init__(self, app_controller):
        super().__init__()
        self.app = app_controller
        self.title("Resident Registration")

        
        self.resizable(False, False)
        self.state("zoomed")
        self.configure(fg_color="#0b0f14")

        self.bind("<Escape>", lambda e: self.destroy())

        ctk.CTkButton(
            self,
            text="← Back to Login",
            fg_color="transparent",
            text_color="#4da6ff",
            hover_color="#1f2937",
            command=self.destroy
        ).pack(anchor="w", padx=20, pady=(10, 0))

        ctk.CTkLabel(
            self,
            text="Create your account",
            font=("Segoe UI", 20, "bold")
        ).pack(pady=10)

        
        self.location_data = {
            "Cavite - Bacoor": ["Alima", "Aniban I", "Aniban II"],
            "Cavite - Carmona": ["Maduya", "Lantic"],
            "Cavite - Cavite City": ["San Roque", "San Francisco"],
            "Cavite - Dasmariñas": ["Salitran I", "Salitran II", "Paliparan"],
            "Cavite - General Trias": ["Bacao", "San Francisco"],
            "Cavite - Imus": ["Alapan I", "Anabu I"],
            "Cavite - Tagaytay": ["Sungay South", "Silang Junction"],
            "Cavite - Trece Martires": ["San Agustin", "San Miguel"],

            "Laguna - Calamba": ["Bagong Kalsada", "Banlic", "Canlubang"],
            "Laguna - San Pedro City": ["Landayan", "Sto. Niño"],
            "Laguna - Biñan City": ["Sto. Domingo", "San Antonio"],
            "Laguna - Santa Rosa City": ["Balibago", "Don Jose"],
            "Laguna - Cabuyao City": ["Banlic", "Marinig"],
            "Laguna - San Pablo City": ["San Vicente", "San Gabriel"],

            "Batangas - Lipa City": ["Adya", "Balintawak"],
            "Batangas City": ["Alangilan", "Bolbok"],
            "Tanauan": ["Altura", "Bañadero"],
            "Santo Tomas": ["San Vicente", "San Miguel"],
            "Calaca": ["Dacanlao", "Quisumbing"],

            "Rizal - Antipolo City": ["Cupang", "De la Paz", "Mambugan"],
            "Angono": ["Poblacion Ibaba", "San Roque"],
            "Baras": ["San Salvador", "Concepcion"],
            "Binangonan": ["Batingan", "Darangan"],
            "Cainta": ["San Andres", "Santo Domingo"],
            "Cardona": ["Del Remedio", "Calahan"],
            "Jalajala": ["Bayugo", "Punta"],
            "Morong": ["San Pedro", "San Juan"],
            "Pililla": ["Malaya", "Bagumbayan"],
            "Montalban (Rodriguez)": ["Balite", "San Isidro"],
            "San Mateo": ["Guitnang Bayan", "Ampid"],
            "Tanay": ["Cayabu", "Sampaloc"],
            "Taytay": ["Dolores", "San Juan"],
            "Teresa": ["May-Iba", "Bagumbayan"],

            "Quezon - Lucena": ["Gulang-Gulang", "Dalahican"],
            "Tayabas City": ["Wakas", "Gibanga"]
        }

       
        main_container = ctk.CTkFrame(self, fg_color="#0b0f14")
        main_container.pack(fill="both", expand=True)

        self.form_frame = ctk.CTkScrollableFrame(main_container, fg_color="#111827")
        self.form_frame.pack(fill="both", expand=True, padx=50, pady=20)

        
        self.fullname = self.create_input("Full Name")
        self.age = self.create_input("Age")
        self.email = self.create_input("Email Address")
        self.address = self.create_input("Complete Address")
        self.contact = self.create_input("Contact Number")
        self.valid_id_entry = self.create_input("Valid ID Number")
        self.username = self.create_input("Username")

        self.password = self.create_password_input("Password")
        self.confirm_password = self.create_password_input("Confirm Password")

        self.gender = self.create_dropdown(["Male", "Female", "Other"], "Gender")
        self.civil_status = self.create_dropdown(
            ["Single", "Married", "Widowed", "Separated"],
            "Civil Status"
        )

       
        self.city = ctk.CTkComboBox(
            self.form_frame,
            values=list(self.location_data.keys()),
            height=38,
            command=self.update_barangay_list
        )
        self.city.pack(pady=6, fill="x")
        self.city.set("Select City")

        self.barangay = ctk.CTkComboBox(
            self.form_frame,
            values=[],
            height=38
        )
        self.barangay.pack(pady=6, fill="x")
        self.barangay.set("Select City First")
        self.barangay.configure(state="disabled")

        
        self.register_btn = ctk.CTkButton(
            self.form_frame,
            text="REGISTER ACCOUNT",
            fg_color="#28a745",
            height=40,
            command=self.register_user
        )
        self.register_btn.pack(fill="x", pady=15)

   
    def create_input(self, placeholder):
        entry = ctk.CTkEntry(self.form_frame, placeholder_text=placeholder, height=38)
        entry.pack(pady=5, fill="x")
        return entry

    def create_dropdown(self, values, placeholder):
        combo = ctk.CTkComboBox(self.form_frame, values=values, height=38)
        combo.pack(pady=5, fill="x")
        combo.set(placeholder)
        return combo

    def create_password_input(self, placeholder):
        frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        frame.pack(pady=5, fill="x")

        entry = ctk.CTkEntry(frame, placeholder_text=placeholder, show="*", height=38)
        entry.pack(side="left", fill="x", expand=True)

        def toggle():
            if entry.cget("show") == "*":
                entry.configure(show="")
                btn.configure(text="🙈")
            else:
                entry.configure(show="*")
                btn.configure(text="👁")

        btn = ctk.CTkButton(frame, text="👁", width=40, command=toggle)
        btn.pack(side="right", padx=5)

        return entry

    
    def update_barangay_list(self, city):
        barangays = self.location_data.get(city, [])

        self.barangay.configure(values=barangays, state="normal")
        self.barangay.set("Select Barangay")

    
    def register_user(self):
        city = self.city.get()
        barangay = self.barangay.get()

        full_name = self.fullname.get().strip()
        username = self.username.get().strip()
        password = self.password.get().strip()
        confirm = self.confirm_password.get().strip()

        email = self.email.get().strip()
        contact = self.contact.get().strip()

        if not all([full_name, username, password, email, contact]):
            messagebox.showwarning("Incomplete", "Fill up required fields")
            return

        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return

        if city in ["Select City", "", None] or barangay in ["Select Barangay", "", None]:
            messagebox.showwarning("Incomplete", "Please select City and Barangay")
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            hashed = hashlib.sha256(password.encode()).hexdigest()

            cursor.execute("""
                INSERT INTO users
                (username, password, full_name, email, contact, address,
                gender, civil_status, valid_id_number, city, barangay, role)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'resident')
            """, (
                username,
                hashed,
                full_name,
                email,
                contact,
                self.address.get(),
                self.gender.get(),
                self.civil_status.get(),
                self.valid_id_entry.get(),
                city,
                barangay
            ))

            conn.commit()
            messagebox.showinfo("Success", "Account created successfully!")
            self.destroy()

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))

        finally:
            if conn:
                conn.close()