import re
from typing import List
import sys
from phi_local.sqlite_handler import SQLiteHandler
import time
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from phi_local.interrogationLocale import InterrogationLocale

sqliteh = SQLiteHandler(db_path="./test_context.sqlite")
il = InterrogationLocale(db_path=sqliteh.db_path)


def pour_LLM(utilisateur:str,question:str):
    print(f"Question de {utilisateur} : {question}")
    transaction_id = il.sqliteh.ajout_question(utilisateur, question).lastrowid
    print(f"L'id de la transaction pour la question {question} est {transaction_id}")

    try:
        reponse = il.interroge_llm(utilisateur, question);
        print(f"reponse = {reponse}")
        r = reponse['message']['content']
        #r = reponse.choices[0].message.content
        print(f"Voici la réponse: {r}")
    except BaseException as e:
        print(f"Quelque chose n'a pas fonctionné au niveau de l'interrogation de Mixtral {e}")
        il.sqliteh.remove_transaction(utilisateur,transaction_id)
        reponse = None
 
def allonzy(lignes:List[str]):
    il.construction_contexte_initial()
    stime = time.time()
    for ligne in lignes :
        l = ligne.split(' ')
        utilisateur = ligne[0]
        salon = ligne[1]
        message = ' '.join(l[2:])
        pour_LLM(utilisateur, message)
    print(f"Durée = {time.time() - stime}")

if __name__ == "__main__":
    lignes = [line.strip() for line in sys.stdin]
    allonzy(lignes)
    
