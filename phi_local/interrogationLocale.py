import logging
import requests
import json
from datetime import datetime
from sqlite_handler import SQLiteHandler
import os
import sys

class InterrogationLocale:
    def __init__(self,
                 db_path: str = 'interrogation_phi.sqlite',
                 profondeur_historique: int = 6,
                 url: str = "http://sanroque:11434",  # Nouvelle URL
                 model_name="phi3.5",
                 instructions_initiales={"role": "system", "content": "Vous êtes un assistant efficace. Vos réponses sont aussi brèves que possible."},
                 ):
        self.db_path = db_path
        self.sqliteh = SQLiteHandler(self.db_path)
        self.profondeur_historique = profondeur_historique
        self.url = url
        self.model_name = model_name
        self.instructions_initiales = instructions_initiales
        self.contexte = []

    def load_env_variables(self,file_path):
        with open(file_path, 'r') as file:
            for line in file:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

    def construction_contexte_initial(self,utilisateur:str="kiki") :
        self.sqliteh.remove_all_transactions()
        transaction_id = self.sqliteh.ajout_question(utilisateur, "Qui était Louis XIV de France").lastrowid
        #print(f"L'id de la transaction pour la question Qui était Louis XIV de France est {transaction_id}")
        self.sqliteh.modification_reponse(utilisateur, transaction_id,"Un roi de France")
        
        transaction_id = self.sqliteh.ajout_question(utilisateur, "Qui était Charles Baudelaire").lastrowid
        #print(f"L'id de la transaction pour la question Qui était Charles Baudelaire est {transaction_id}")
        self.sqliteh.modification_reponse(utilisateur, transaction_id,"Un poète Français")
        #for transaction in self.sqliteh.historique(utilisateur, self.profondeur_historique):
        #    print(f"*************transaction {transaction}")

    def historique_et_question_formatés(self, utilisateur: str = "kiki"):
        contexte = [self.instructions_initiales]

        logging.info(f"°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°° profondeur {self.profondeur_historique}")
        h = self.sqliteh.historique(utilisateur,  self.profondeur_historique)
        logging.info(f"°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°° res h {h}")
        for transaction in h:
            contexte.append({"role": "user", "content": transaction['question']})
            if transaction['reponse'] is not None:
                contexte.append({"role": "assistant", "content": transaction['reponse']})
        return contexte

    def interroge_llm(self, utilisateur, question):
        print(f"Interroge {self.model_name} {question}")
        logging.info(f"L'utilisateur {utilisateur} pose à {self.model_name} la question {question}")
        try:
            qf = self.historique_et_question_formatés(utilisateur)
        except BaseException as e:
            print(f"Échec construction question {e}")
            logging.info(f"Échec construction question {e}")
            return None
        
        # Préparation des headers pour la requête POST
        headers = {
            "Content-Type": "application/json",
#            "Authorization": f"Bearer {self.api_key}"  # Utilisation de la clé API si nécessaire
        }
        
        logging.info(f"°°°°°°°°°°°°°°°°°°°°°°°°°°°°°° qf = {qf}")

        # Préparation des données pour l'appel à la nouvelle API
        data = {
            "model": self.model_name,
            "messages": qf,
            "options": {"num_gpu": 32}, #, "ctx-size": 1024},
            "stream": False
        }

        try:
            # Appel à la nouvelle URL avec requests.post
            response = requests.post(f"{self.url}/api/chat", headers=headers, data=json.dumps(data))

            # Vérification de la réponse
            if response.status_code == 200:
                return response.json()  # Retourne la réponse formatée JSON
            else:
                print(f"Échec interrogation locale : {response.status_code}, {response.text}")
                logging.info(f"Échec interrogation locale : {response.status_code}, {response.text}")
                return None
        except BaseException as e:
            logging.error(f"Échec interrogation locale {e}")
            return None

