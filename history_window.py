import customtkinter as ctk
from tkinter import ttk, messagebox
from db_config import get_db_connection


class HistoryDashboard(ctk.CTkFrame):

    def __init__(self, master, app_controller):
        super().__init__(master, fg_color="#0b0f14")

        self.app = app_controller
        self.pack(fill="both", expand=True)

       
        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "Treeview",
            background="#121212",
            foreground="white",
            fieldbackground="#121212",
            rowheight=28
        )

        style.configure(
            "Treeview.Heading",
            background="#1f2937",
            foreground="white"
        )

       
        ctk.CTkLabel(
            self,
            text="Transaction History",
            font=("Segoe UI", 26, "bold"),
            text_color="white"
        ).pack(pady=15)

        #
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(pady=5)

        self.search_entry = ctk.CTkEntry(
            search_frame,
            width=300,
            placeholder_text="Search username..."
        )
        self.search_entry.pack(side="left", padx=5)

        ctk.CTkButton(search_frame, text="Search", command=self.search_data).pack(side="left", padx=5)
        ctk.CTkButton(search_frame, text="Refresh", command=self.load_data).pack(side="left", padx=5)

        ctk.CTkButton(search_frame, text="Daily Report", fg_color="#2a9d8f", command=self.generate_daily_report).pack(side="left", padx=5)

        ctk.CTkButton(search_frame, text="Delete Selected", fg_color="red", command=self.delete_selected).pack(side="left", padx=5)
        ctk.CTkButton(search_frame, text="Delete All", fg_color="darkred", command=self.delete_all).pack(side="left", padx=5)

        
        table_frame = ctk.CTkFrame(self, fg_color="#0b0f14")
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("ID", "Queue", "Username", "Service", "Details", "Date/Time")

        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140)

        self.tree.pack(fill="both", expand=True)

        self.load_data()

    
    def delete_selected(self):

        selected = self.tree.focus()

        if not selected:
            messagebox.showwarning("Warning", "Pumili muna ng record!")
            return

        values = self.tree.item(selected, "values")
        record_id = values[0]

        if not messagebox.askyesno("Confirm", "Delete selected record?"):
            return

        conn = get_db_connection()
        if not conn:
            return

        try:
            cur = conn.cursor()
            cur.execute(
                "DELETE FROM transaction_history WHERE id=%s",
                (record_id,)
            )
            conn.commit()

            messagebox.showinfo("Success", "Deleted successfully!")
            self.load_data()

        finally:
            if conn:
                conn.close()

   
    def delete_all(self):

        if not messagebox.askyesno("Confirm", "Delete ALL history? This cannot be undone!"):
            return

        conn = get_db_connection()
        if not conn:
            return

        try:
            cur = conn.cursor()

            if self.app.role == "admin":
                cur.execute("DELETE FROM transaction_history")
            else:
                cur.execute(
                    "DELETE FROM transaction_history WHERE username=%s",
                    (self.app.username,)
                )

            conn.commit()

            messagebox.showinfo("Success", "All history deleted!")
            self.load_data()

        finally:
            if conn:
                conn.close()

    
    def load_data(self):

        self.tree.delete(*self.tree.get_children())

        conn = get_db_connection()
        if not conn:
            return

        try:
            cur = conn.cursor(dictionary=True)

           
            if self.app.role != "admin":
                query = """
                    SELECT id, queue_id, username, action, details, timestamp
                    FROM transaction_history
                    WHERE username=%s
                    ORDER BY timestamp DESC
                """
                params = (self.app.username,)
            else:
                query = """
                    SELECT id, queue_id, username, action, details, timestamp
                    FROM transaction_history
                    ORDER BY timestamp DESC
                """
                params = ()

            cur.execute(query, params)

            for r in cur.fetchall():
                self.tree.insert("", "end", values=(
                    r["id"],
                    r.get("queue_id", "N/A"),
                    r["username"],
                    r["action"],
                    r["details"],
                    r["timestamp"]
                ))

        finally:
            if conn:
                conn.close()

   
    def search_data(self):

        keyword = self.search_entry.get().strip()

        self.tree.delete(*self.tree.get_children())

        conn = get_db_connection()
        if not conn:
            return

        try:
            cur = conn.cursor(dictionary=True)

           
            if self.app.role != "admin":
                query = """
                    SELECT id, queue_id, username, action, details, timestamp
                    FROM transaction_history
                    WHERE username LIKE %s
                    AND username=%s
                    ORDER BY timestamp DESC
                """
                params = (f"%{keyword}%", self.app.username)
            else:
                query = """
                    SELECT id, queue_id, username, action, details, timestamp
                    FROM transaction_history
                    WHERE username LIKE %s
                    ORDER BY timestamp DESC
                """
                params = (f"%{keyword}%",)

            cur.execute(query, params)

            for r in cur.fetchall():
                self.tree.insert("", "end", values=(
                    r["id"],
                    r.get("queue_id", "N/A"),
                    r["username"],
                    r["action"],
                    r["details"],
                    r["timestamp"]
                ))

        finally:
            if conn:
                conn.close()

    def generate_daily_report(self):
        from datetime import date
        today = date.today().strftime("%Y-%m-%d")
        
        self.tree.delete(*self.tree.get_children())
        
        conn = get_db_connection()
        if not conn: return
        
        try:
            cur = conn.cursor(dictionary=True)
            query = "SELECT * FROM transaction_history WHERE DATE(timestamp) = %s"
            cur.execute(query, (today,))
            
            records = cur.fetchall()
            for r in records:
                self.tree.insert("", "end", values=(
                    r["id"], r.get("queue_id", "N/A"), r["username"], 
                    r["action"], r["details"], r["timestamp"]
                ))
            
            if not records:
                messagebox.showinfo("Report", "No transactions for today.")
        finally:
            conn.close()

    
    def auto_refresh(self):
        if self.winfo_exists():
            self.load_data()
            self.after(8000, self.auto_refresh)