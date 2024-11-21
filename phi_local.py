import logging
import os
import time
from interfaces import IObserver, IObservable, IPlugin
from sqlite_handler import SQLiteHandler
from interrogationLocale import InterrogationLocale



logger = logging.getLogger(__name__)

    
class Phi(IObserver):
    def __init__(self,observable:IObservable=None):
        self.__observable = observable

        # Déterminer le répertoire du plugin
        plugin_dir = os.path.dirname(os.path.abspath(__file__))

        # Chemin du nouveau répertoire 'data'
        self.data_dir = os.path.join(plugin_dir, 'data')

        # Créer le répertoire de données s'il n'existe pas
        os.makedirs(self.data_dir, exist_ok=True)
        db_path = os.path.join(self.data_dir, 'test_context.sqlite')
        
        logger.info(f"********************** Répertoire de données du plugin : {self.data_dir}")
 
        self.sqliteh = SQLiteHandler(db_path=db_path)
        self.il = InterrogationLocale(self.sqliteh.db_path)

    def pour_llm(self,question:str,utilisateur:str,attachments):
        print(f"Question de {utilisateur} : {question}")
        transaction_id = self.il.sqliteh.ajout_question(utilisateur, question).lastrowid
        print(f"L'id de la transaction pour la question {question} est {transaction_id}")
            
        reponse = ""
        try:
            stime = time.time()
            reponse = self.il.interroge_llm(utilisateur, question);
            logger.info(f"Réponse du LLM \"{reponse}\"")
            #reponse = reponse.choices[0].message.content
            reponse = reponse['choices'][0]['message']['content']
            logger.info(f"Voici la réponse: {reponse}")
            self.il.sqliteh.modification_reponse(utilisateur, transaction_id,reponse)
        except BaseException as e:
            print(f"Quelque chose n'a pas fonctionné au niveau de l'interrogation du LLM {e}")
            self.il.sqliteh.remove_transaction(utilisateur, transaction_id)
            reponse = None
        reponset = f"{time.time()-stime} {reponse}"
        return reponset

    async def notify(self,msg:str,to:str,attachments):
        logger.info(f"***************************** L'utilisateur {to} a écrit {msg}")
        reponse = self.pour_llm(msg,to,attachments=)
        if reponse == None:
            reponse = "Une erreur s'est produite lors de l'interrogation du LLM"
        await self.__observable.notify("Coco a dit : "+reponse, to, attachments)

    def prefix(self):
        return "!coco"
    
class Plugin(IPlugin):
    def __init__(self,observable:IObservable):
        self.__observable = observable
        self.phi = Phi(self.__observable)
        # Autres initialisations
        logger.info(f"********************** Observateur créé {self.phi.prefix()}")
        
    def start(self):
        logger.info(f"********************** Inscripton de {self.phi.prefix()}")
        self.__observable.subscribe(self.phi)

    async def stop(self):
        self.__observable.unsubscribe(self.phi)