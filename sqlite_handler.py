import sqlite3
import json
from datetime import datetime

class SQLiteHandler:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.creation_historique()
        self.creation_contexte()

    def creation_historique(self):
        with self.conn:
            self.conn.execute('''CREATE TABLE IF NOT EXISTS transactions (
                                 utilisateur TEXT,
                                 transaction_id INTEGER PRIMARY KEY,
                                 date_question TEXT,
                                 question TEXT,
                                 date_reponse TEXT,
                                 reponse TEXT)''')

    def suppression_historique(self):
        with self.conn:
            self.conn.execute('DROP TABLE IF EXISTS transactions')
            self.creation_historique()

    def creation_contexte(self):
        with self.conn:
            self.conn.execute('''CREATE TABLE IF NOT EXISTS contexte (
                                 utilisateur TEXT PRIMARY KEY,
                                 contexte TEXT)''')


    def effacement_contexte(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('DROP TABLE IF EXISTS contexte')

    def ajout_transaction(self, utilisateur, date_question, question, date_reponse, reponse):
        with self.conn:
            date_question = datetime.now().isoformat()
            self.conn.execute('INSERT INTO transactions (utilisateur, date_question, question, date_reponse, reponse) VALUES (?, ?, ?, ?, ?, ?)',
                              (utilisateur, date_question, question, date_reponse, reponse, )) 
            

    def ajout_question(self, utilisateur, question):
        with self.conn:
            date_question = datetime.now().isoformat()
            ret = self.conn.execute('INSERT INTO transactions (utilisateur, date_question, question) VALUES (?, ?, ?)',
                              (utilisateur, date_question, question))
            return ret

    def modification_reponse(self, utilisateur, transaction_id, reponse):
        with self.conn:
            date_reponse = datetime.now().isoformat()
            if reponse == None:
                reponse = "" 
            ret = self.conn.execute('UPDATE transactions SET date_reponse = ?, reponse = ? WHERE utilisateur = ? AND transaction_id = ?',
                              (date_reponse, reponse, utilisateur, transaction_id,))
            return ret

    def remove_transaction(self, utilisateur, transaction_id):
        with self.conn:
            ret = self.conn.execute('DELETE FROM transactions WHERE utilisateur = ? AND transaction_id = ?',
                              (utilisateur, transaction_id,))
            return ret
        
    # def remove_transaction(self, utilisateur):
    #     with self.conn:
    #         ret = self.conn.execute('DELETE FROM transactions WHERE utilisateur = ?,
    #                           (utilisateur, ))
    #         return ret

    
    def remove_all_transactions(self):
        with self.conn:
            ret = self.conn.execute('DELETE FROM transactions')
            return ret


    def modification_contexte(self, utilisateur, contexte):
        with self.conn:
            contexte_json = json.dumps(contexte)
            ret = self.conn.execute('INSERT OR REPLACE INTO contexte (utilisateur, contexte) VALUES (?, ?)',
                              (utilisateur, contexte_json))
            self.conn.commit()
            return ret
            
    def historique(self, utilisateur, n):
        with self.conn:
            cursor = self.conn.execute('''SELECT * FROM transactions WHERE utilisateur = ?  ORDER BY transaction_id  DESC LIMIT ?''', (utilisateur, n,))
            transactions = cursor.fetchall()
            
            # Convertir les transactions en une liste de dictionnaires pour une meilleure lisibilité
            colonnes = [description[0] for description in cursor.description]
            transactions_liste = []
            for transaction in transactions:
                transactions_liste.append(dict(zip(colonnes, transaction)))
            
            return transactions_liste[::-1]

    def __del__(self):
        self.conn.close()
