import customtkinter as ctk
from db_config import get_db_connection

class ResidentDashboard(ctk.CTkFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color="#0f0f0f")
        self.app = app_controller
        self.pack(fill="both", expand=True, padx=20, pady=20)

       
        ctk.CTkLabel(self, text=f"Welcome, {self.app.username}!", font=("Segoe UI", 32, "bold"), text_color="#ffffff").pack(anchor="w", pady=(0, 20))

       
        queue_frame = ctk.CTkFrame(self, fg_color="#1f2937", corner_radius=15)
        queue_frame.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(queue_frame, text="📺 NOW SERVING", font=("Segoe UI", 16, "bold"), text_color="#9ca3af").pack(pady=(10, 0))
        self.now_serving_label = ctk.CTkLabel(queue_frame, text="Loading...", font=("Segoe UI", 48, "bold"), text_color="#60a5fa")
        self.now_serving_label.pack(pady=(0, 15))

       
        status_frame = ctk.CTkFrame(self, fg_color="transparent")
        status_frame.pack(fill="x", pady=(0, 20))
        
        self.status_labels = {}
        statuses = [("Pending", "#fbbf24"), ("Approved", "#22c55e"), ("Rejected", "#ef4444"), ("Cancelled", "#6b7280")]
        
        for i, (s, color) in enumerate(statuses):
            card = ctk.CTkFrame(status_frame, fg_color="#18181b", corner_radius=10, width=150)
            card.grid(row=0, column=i, padx=10, pady=5, sticky="ew")
            status_frame.grid_columnconfigure(i, weight=1)
            
            ctk.CTkLabel(card, text=s, font=("Segoe UI", 14), text_color=color).pack(pady=(10, 0))
            lbl = ctk.CTkLabel(card, text="0", font=("Segoe UI", 28, "bold"))
            lbl.pack(pady=(0, 10))
            self.status_labels[s] = lbl

        
        grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True)
        for i in range(3): grid_frame.grid_columnconfigure(i, weight=1)

        self.create_info_card(grid_frame, 0, "Mission", "To provide efficient and accessible public service through innovative digital solutions.", "#1f1f1f")
        self.create_info_card(grid_frame, 1, "Vision", "A modernized Barangay where services are accessible at your fingertips.", "#1f1f1f")
        
        announcement_text = (
            "• Libreng Tuli: 9am-5pm\n"
            "• Anti-Rabies: 9am-5pm\n"
            "• Bakuna: 8am-5pm\n"
            "• Medical Mission: 7am-6pm"
        )
        self.create_info_card(grid_frame, 2, "Announcements", announcement_text, "#1f1f1f")

        self.load_data()

    def create_info_card(self, master, col, title, content, color):
        card = ctk.CTkFrame(master, fg_color=color, corner_radius=15)
        card.grid(row=0, column=col, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(card, text=title.upper(), font=("Segoe UI", 16, "bold"), text_color="#3b82f6").pack(pady=15)
        ctk.CTkLabel(card, text=content, font=("Segoe UI", 15), wraplength=250, justify="center").pack(padx=15, pady=(0, 20))

    def load_data(self):
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT status, COUNT(*) as total FROM appointments WHERE username=%s GROUP BY status", (self.app.username,))
                for row in cursor.fetchall():
                    if row['status'] in self.status_labels:
                        self.status_labels[row['status']].configure(text=str(row['total']))
                
                cursor.execute("SELECT queue_id FROM queue WHERE status='Serving' LIMIT 1")
                q = cursor.fetchone()
                self.now_serving_label.configure(text=f"Queue #{q['queue_id']}" if q else "No one serving")
            finally:
                conn.close()