# model.py
import sqlite3
from datetime import datetime

class Model:
    def __init__(self, db_name="parc.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_tables()
        self.init_attractions()

    def create_tables(self):
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS attractions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prix REAL NOT NULL
        )
        """)
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            attraction_id INTEGER NOT NULL,
            attraction_nom TEXT NOT NULL,
            prix REAL NOT NULL,
            date_heure TEXT NOT NULL,
            FOREIGN KEY (attraction_id) REFERENCES attractions(id)
        )
        """)
        self.conn.commit()

    def init_attractions(self):
        existant = self.conn.execute("SELECT COUNT(*) FROM attractions").fetchone()[0]
        if existant == 0:
            self.conn.execute("INSERT INTO attractions (nom, prix) VALUES (?, ?)", ("Bateau Pirate", 100.0))
            self.conn.execute("INSERT INTO attractions (nom, prix) VALUES (?, ?)", ("Balançoire Électrique", 100.0))
            self.conn.commit()

    def liste_attractions(self):
        return self.conn.execute("SELECT * FROM attractions").fetchall()

    def vendre_ticket(self, attraction_id, quantite=1):
        """Crée 'quantite' tickets pour une attraction donnée et les retourne tous"""
        attraction = self.conn.execute(
            "SELECT * FROM attractions WHERE id=?", (attraction_id,)
        ).fetchone()
        if not attraction:
            return None

        tickets_crees = []
        for _ in range(quantite):
            date_heure = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.conn.execute(
                "INSERT INTO tickets (attraction_id, attraction_nom, prix, date_heure) VALUES (?, ?, ?, ?)",
                (attraction[0], attraction[1], attraction[2], date_heure)
            )
            self.conn.commit()
            ticket = self.conn.execute(
                "SELECT * FROM tickets ORDER BY id DESC LIMIT 1"
            ).fetchone()
            tickets_crees.append(ticket)

        return tickets_crees

    def tickets_du_jour(self):
        aujourdhui = datetime.now().strftime("%Y-%m-%d")
        return self.conn.execute(
            "SELECT * FROM tickets WHERE date_heure LIKE ? ORDER BY id DESC",
            (f"{aujourdhui}%",)
        ).fetchall()

    def total_du_jour(self):
        aujourdhui = datetime.now().strftime("%Y-%m-%d")
        result = self.conn.execute(
            "SELECT COUNT(*), COALESCE(SUM(prix), 0) FROM tickets WHERE date_heure LIKE ?",
            (f"{aujourdhui}%",)
        ).fetchone()
        return {"nombre_tickets": result[0], "total_argent": result[1]}

    def total_par_attraction_jour(self):
        aujourdhui = datetime.now().strftime("%Y-%m-%d")
        return self.conn.execute(
            """SELECT attraction_nom, COUNT(*), SUM(prix)
               FROM tickets WHERE date_heure LIKE ?
               GROUP BY attraction_nom""",
            (f"{aujourdhui}%",)
        ).fetchall()

    def liste_jours(self):
        """Retourne tous les jours distincts où il y a eu des ventes, du plus récent au plus ancien"""
        return self.conn.execute(
            """SELECT DATE(date_heure) as jour, COUNT(*), SUM(prix)
               FROM tickets
               GROUP BY jour
               ORDER BY jour DESC"""
        ).fetchall()

    def tickets_par_jour(self, jour):
        """Détail des tickets pour un jour précis (format YYYY-MM-DD)"""
        return self.conn.execute(
            "SELECT * FROM tickets WHERE date_heure LIKE ? ORDER BY id",
            (f"{jour}%",)
        ).fetchall()

    def total_par_attraction_pour_jour(self, jour):
        return self.conn.execute(
            """SELECT attraction_nom, COUNT(*), SUM(prix)
               FROM tickets WHERE date_heure LIKE ?
               GROUP BY attraction_nom""",
            (f"{jour}%",)
        ).fetchall()