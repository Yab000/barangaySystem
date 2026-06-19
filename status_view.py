import customtkinter as ctk
from db_config import get_db_connection


class StatusDashboard(ctk.CTkFrame):

    def __init__(self, master, app_controller):

        super().__init__(master, fg_color="transparent")

        self.running = True
        self.app = app_controller

        self.pack(fill="both", expand=True, padx=30, pady=30)

        
        ctk.CTkLabel(
            self,
            text=" Barangay Analytics & System Status",
            font=("Segoe UI", 28, "bold")
        ).pack(anchor="w", pady=(0, 30))

    
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.pack(fill="x", pady=10)

        self.pending_card = self._create_stat_card("PENDING REQUESTS", "#1f538d")
        self.queue_card = self._create_stat_card("ACTIVE QUEUE", "#28a745")

        self.pending_card.pack(side="left", fill="both", expand=True, padx=10)
        self.queue_card.pack(side="left", fill="both", expand=True, padx=10)

        self.update_stats()


    def _create_stat_card(self, title, color):

        card = ctk.CTkFrame(
            self.stats_frame,
            fg_color="#2b2b2b",
            corner_radius=15,
            height=150
        )

        ctk.CTkLabel(
            card,
            text=title,
            font=("Segoe UI", 14, "bold"),
            text_color="gray"
        ).pack(pady=(25, 5))

        label = ctk.CTkLabel(
            card,
            text="0",
            font=("Segoe UI", 48, "bold"),
            text_color=color
        )
        label.pack(pady=(0, 25))

        card.value_label = label
        return card

    
    def update_stats(self):

        if not self.winfo_exists() or not self.running:
            return

        conn = None
        cursor = None

        try:
            conn = get_db_connection()
            if not conn:
                return

            cursor = conn.cursor()

    
            cursor.execute("""
                SELECT COUNT(*)
                FROM appointments
                WHERE LOWER(status) = 'pending'
            """)
            pending = cursor.fetchone()[0]

    
            cursor.execute("""
                SELECT COUNT(*)
                FROM appointments
                WHERE LOWER(status) IN ('approved', 'processing')
            """)
            queue = cursor.fetchone()[0]
            
            self.pending_card.value_label.configure(text=str(pending))
            self.queue_card.value_label.configure(text=str(queue))

        except Exception as e:
            print(f"Error updating status: {e}")

        finally:
            try:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
            except:
                pass

        self.after(5000, self.update_stats)


    def stop(self):
        self.running = False