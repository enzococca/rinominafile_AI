import sys
import os
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog,
                             QTextEdit, QMessageBox, QProgressBar, QRadioButton, QButtonGroup, QHBoxLayout,
                             QInputDialog, QDialog, QListWidget, QTextBrowser, QListWidgetItem)
from openai import OpenAI
import re
import json


class APIKeyManager:
    def __init__(self, api_key_file='openai_api_key.txt'):
        self.api_key_file = api_key_file
        self.api_key = None
        self.client = None

    def load_api_key(self):
        if os.path.exists(self.api_key_file):
            with open(self.api_key_file, 'r') as file:
                self.api_key = file.read().strip()
            return True
        return False

    def save_api_key(self, api_key):
        with open(self.api_key_file, 'w') as file:
            file.write(api_key)
        self.api_key = api_key

    def get_api_key(self):
        if not self.api_key:
            if not self.load_api_key():
                self.request_api_key()
        return self.api_key

    def request_api_key(self):
        from PyQt5.QtWidgets import QInputDialog, QLineEdit

        api_key, ok = QInputDialog.getText(
            None,
            "Inserisci API Key",
            "Per favore, inserisci la tua API Key di OpenAI:",
            QLineEdit.Normal
        )
        if ok and api_key:
            self.save_api_key(api_key)
        else:
            raise ValueError("API Key non fornita. Impossibile procedere.")

    def get_client(self):
        if not self.client:
            api_key = self.get_api_key()
            self.client = OpenAI(api_key=api_key)
        return self.client

class RuleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Ensure you correctly retrieve the API key from the environment variables
        self.api_manager = APIKeyManager()
        self.client = self.api_manager.get_client()

        self.setWindowTitle("Gestione Regole")
        self.setGeometry(300, 300, 600, 400)  # Increased width for better visibility
        self.layout = QVBoxLayout(self)

        self.ruleList = QListWidget()
        self.ruleList.setWordWrap(True)  # Enable word wrap for long descriptions
        self.layout.addWidget(self.ruleList)

        buttonLayout = QHBoxLayout()
        self.addButton = QPushButton("Aggiungi Regola")
        self.editButton = QPushButton("Modifica Regola")
        self.deleteButton = QPushButton("Elimina Regola")
        self.helpButton = QPushButton("Aiuto")
        self.aiButton = QPushButton("Genera Regola con AI")
        buttonLayout.addWidget(self.addButton)
        buttonLayout.addWidget(self.editButton)
        buttonLayout.addWidget(self.deleteButton)
        buttonLayout.addWidget(self.helpButton)
        buttonLayout.addWidget(self.aiButton)
        self.layout.addLayout(buttonLayout)

        self.addButton.clicked.connect(self.addRule)
        self.editButton.clicked.connect(self.editRule)
        self.deleteButton.clicked.connect(self.deleteRule)
        self.helpButton.clicked.connect(self.showHelp)
        self.aiButton.clicked.connect(self.generateRuleWithAI)


        self.defaultRules = [
            ("Solo lettere, numeri, underscore e trattini", r'^[a-zA-Z0-9_-]+$'),
            ("Non inizia con un punto", r'^[^.]+$'),
            ("Lunghezza tra 1 e 255 caratteri", r'^.{1,255}$'),
        ]
        self.rules_file = 'rules.json'  # Aggiungi questa riga
        self.loadRules()
        if self.ruleList.count() == 0:
            self.loadDefaultRules()


    def showHelp(self):
        helpText = """
        Come creare regole (espressioni regolari):

        1. ^ indica l'inizio della stringa.
        2. $ indica la fine della stringa.
        3. [] definisce un set di caratteri. Ad esempio, [a-z] significa qualsiasi lettera minuscola.
        4. [^] nega un set di caratteri. Ad esempio, [^\s] significa qualsiasi carattere che non sia uno spazio.
        5. + significa "uno o più" del carattere o gruppo precedente.
        6. * significa "zero o più" del carattere o gruppo precedente.
        7. {n,m} specifica un range di ripetizioni. {3,50} significa "da 3 a 50 volte".
        8. \d rappresenta qualsiasi cifra numerica.
        9. \s rappresenta qualsiasi carattere di spazio (spazio, tab, newline).
        10. | agisce come un OR. Ad esempio, (txt|pdf) significa "txt" oppure "pdf".
        11. . rappresenta qualsiasi carattere singolo (eccetto newline).
        12. Per usare caratteri speciali come parte della stringa da cercare, precedili con . Ad esempio, . per cercare un punto letterale.

        Esempi di regole:

        1. Solo lettere minuscole e numeri: ^[a-z0-9]+$
        2. Inizia con una lettera: ^[a-zA-Z]
        3. Non contiene spazi: ^[^\s]+$
        4. Contiene un'estensione di file valida: .*.(txt|pdf|jpg|png)$
        5. Nome file con data in formato YYYYMMDD: ^[a-zA-Z]+_\d{8}.[a-z]+$
        6. Non contiene caratteri speciali eccetto underscore e trattino: ^[a-zA-Z0-9_-]+$
        7. Lunghezza minima di 3 caratteri e massima di 50: ^.{3,50}$
        8. Inizia con "doc_" seguito da numeri: ^doc_\d+

        Esempi di come usare queste regole:
        - ^[a-z0-9]+$: Corrisponde a "hello123" ma non a "Hello123" o "hello_123".
        - ^[a-zA-Z]: Corrisponde a "File1" ma non a "1File".
        - .*.(txt|pdf|jpg)$: Corrisponde a "documento.txt" o "immagine.jpg" ma non a "file.exe".
        - ^[a-zA-Z]+_\d{8}.[a-z]+$: Corrisponde a "report_20230515.pdf" ma non a "report_2023.pdf".

        Ricorda di testare le tue espressioni regolari con vari input per assicurarti che funzionino come previsto.
        """

        helpDialog = QDialog(self)
        helpDialog.setWindowTitle("Aiuto Regole")
        helpDialog.setGeometry(350, 350, 600, 400)
        layout = QVBoxLayout(helpDialog)

        textBrowser = QTextBrowser()
        textBrowser.setPlainText(helpText)
        layout.addWidget(textBrowser)

        closeButton = QPushButton("Chiudi")
        closeButton.clicked.connect(helpDialog.close)
        layout.addWidget(closeButton)

        helpDialog.exec_()

    def loadDefaultRules(self):
        for description, regex in self.defaultRules:
            self.addRuleToList(description, regex)


    def generateRuleWithAI(self):
        description, ok = QInputDialog.getText(self, "Genera Regola con AI",
                                               "Descrivi la regola che vuoi creare in linguaggio naturale:")
        if ok and description:
            try:
                regex = self.getRegexFromAI(description)
                self.addRuleToList(description, regex)
                QMessageBox.information(self, "Successo", f"Regola generata: {regex}")
            except Exception as e:
                QMessageBox.warning(self, "Errore", f"Errore nella generazione della regola: {str(e)}")

    def getRegexFromAI(self, description):
        prompt = f"Genera un'espressione regolare per la seguente descrizione: {description}. " \
                 f"Fornisci solo l'espressione regolare, senza spiegazioni."

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Sei un esperto di espressioni regolari. " \
                                              "Genera espressioni regolari precise e concise."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50,
            n=1,
            temperature=0.7
        )

        regex = response.choices[0].message.content.strip()
        return regex

    def getRules(self):
        return [self.ruleList.item(i).data(Qt.UserRole) for i in range(self.ruleList.count())]

    def loadRules(self):
        if os.path.exists(self.rules_file):
            with open(self.rules_file, 'r') as f:
                rules = json.load(f)
            self.ruleList.clear()
            for description, regex in rules:
                self.addRuleToList(description, regex)
        else:
            self.loadDefaultRules()

    def saveRules(self):
        rules = [self.ruleList.item(i).data(Qt.UserRole) for i in range(self.ruleList.count())]
        with open(self.rules_file, 'w') as f:
            json.dump(rules, f)

    def addRuleToList(self, description, regex):
        item = QListWidgetItem(f"{description}: {regex}")
        item.setData(Qt.UserRole, (description, regex))
        self.ruleList.addItem(item)
        self.saveRules()

    def addRule(self):
        regex, ok = QInputDialog.getText(self, "Aggiungi Regola", "Inserisci la nuova regola (espressione regolare):")
        if ok and regex:
            description, ok = QInputDialog.getText(self, "Aggiungi Descrizione", "Inserisci una breve descrizione della regola:")
            if ok:
                self.addRuleToList(description, regex)

    def editRule(self):
        currentItem = self.ruleList.currentItem()
        if currentItem:
            oldDescription, oldRegex = currentItem.data(Qt.UserRole)
            newRegex, ok = QInputDialog.getText(self, "Modifica Regola", "Modifica la regola:", text=oldRegex)
            if ok and newRegex:
                newDescription, ok = QInputDialog.getText(self, "Modifica Descrizione", "Modifica la descrizione:", text=oldDescription)
                if ok:
                    self.ruleList.takeItem(self.ruleList.row(currentItem))
                    self.addRuleToList(newDescription, newRegex)

    def deleteRule(self):
        currentItem = self.ruleList.currentItem()
        if currentItem:
            self.ruleList.takeItem(self.ruleList.row(currentItem))
            self.saveRules()

    def closeEvent(self, event):
        self.saveRules()
        super().closeEvent(event)


class FileRenamerApp(QWidget):
    def __init__(self):
        super().__init__()
        # Ensure you correctly retrieve the API key from the environment variables

        self.api_manager = APIKeyManager()
        self.client = self.api_manager.get_client()
        self.ruleDialog = RuleDialog(self)
        self.initUI()

    def showRuleDialog(self):
        self.ruleDialog.exec_()

    def check_poorly_named_items(self, directory):
        rules = self.ruleDialog.getRules()
        poorly_named_items = []

        for root, dirs, files in os.walk(directory):
            items = dirs + files if self.allRadio.isChecked() else \
                dirs if self.foldersOnlyRadio.isChecked() else \
                    files if self.filesOnlyRadio.isChecked() else []

            for item in items:
                full_path = os.path.join(root, item)
                failed_rules = []
                for i, (description, rule) in enumerate(rules, 1):
                    if not re.match(rule, item):
                        # Ignora la regola del punto iniziale per i file con estensione
                        if not (os.path.isfile(full_path) and description == "Non inizia con un punto"):
                            failed_rules.append(f"Regola {i}")

                if failed_rules:
                    poorly_named_items.append((full_path, f"Non segue le regole: {', '.join(failed_rules)}"))
                elif os.path.isfile(full_path) and not os.path.splitext(item)[1] and self.filesOnlyRadio.isChecked():
                    poorly_named_items.append((full_path, "File senza estensione"))
                elif len(item) > 255:
                    poorly_named_items.append((full_path, "Nome troppo lungo"))

        return poorly_named_items

    def highlight_poorly_named_items(self):
        directory = self.pathEdit.text()
        if not directory:
            QMessageBox.warning(self, 'Errore', 'Per favore, seleziona una cartella.')
            return

        poorly_named_items = self.check_poorly_named_items(directory)

        if poorly_named_items:
            report = "Elementi con nomi problematici:\n\n"
            for item, reason in poorly_named_items:
                report += f"{item}: {reason}\n"

            # Aggiungi la lista delle regole alla fine del report
            report += "\nRegole applicate:\n"
            for i, (description, rule) in enumerate(self.ruleDialog.getRules(), 1):
                report += f"Regola {i}: {description} ({rule})\n"
        else:
            report = "Nessun elemento con nome problematico trovato."

        self.previewArea.setText(report)

    def get_custom_rules(self):
        # Questa funzione potrebbe essere espansa per permettere all'utente di inserire regole personalizzate
        # Per ora, usiamo alcune regole predefinite
        return [
            r'^[a-zA-Z0-9_-]+$',  # Solo lettere, numeri, underscore e trattini
            r'^[^.]+$',  # Non inizia con un punto
            r'^.{1,255}$',  # Lunghezza tra 1 e 255 caratteri
        ]


    def initUI(self):
        self.setWindowTitle('File Renamer AI')
        self.setGeometry(300, 300, 600, 500)

        layout = QVBoxLayout()

        # Directory selection
        self.label = QLabel('Seleziona la cartella contenente i file da rinominare:')
        layout.addWidget(self.label)
        self.pathEdit = QLineEdit(self)
        layout.addWidget(self.pathEdit)
        self.browseButton = QPushButton('Sfoglia', self)
        self.browseButton.clicked.connect(self.browse_folder)
        layout.addWidget(self.browseButton)

        # Rename options
        self.optionsGroup = QButtonGroup(self)
        optionsLayout = QHBoxLayout()
        self.filesOnlyRadio = QRadioButton("Solo File")
        self.foldersOnlyRadio = QRadioButton("Solo Cartelle")
        self.allRadio = QRadioButton("Tutto")
        self.optionsGroup.addButton(self.filesOnlyRadio)
        self.optionsGroup.addButton(self.foldersOnlyRadio)
        self.optionsGroup.addButton(self.allRadio)
        optionsLayout.addWidget(self.filesOnlyRadio)
        optionsLayout.addWidget(self.foldersOnlyRadio)
        optionsLayout.addWidget(self.allRadio)
        layout.addLayout(optionsLayout)

        # Prompt input
        self.promptLabel = QLabel('Inserisci il prompt per rinominare:')
        layout.addWidget(self.promptLabel)
        self.promptEdit = QTextEdit(self)
        layout.addWidget(self.promptEdit)

        # Buttons
        self.suggestButton = QPushButton('Suggerisci Prompt', self)
        self.suggestButton.clicked.connect(self.suggest_prompt)
        layout.addWidget(self.suggestButton)
        self.previewButton = QPushButton('Anteprima', self)
        self.previewButton.clicked.connect(self.preview_changes)
        layout.addWidget(self.previewButton)
        self.renameButton = QPushButton('Rinomina', self)
        self.renameButton.clicked.connect(self.rename_items)
        layout.addWidget(self.renameButton)

        # Progress bar
        self.progressBar = QProgressBar(self)
        self.progressBar.setVisible(False)
        layout.addWidget(self.progressBar)

        # Preview area
        self.previewArea = QTextEdit(self)
        self.previewArea.setReadOnly(True)
        layout.addWidget(self.previewArea)

        # Aggiungi un nuovo pulsante per gestire le regole
        self.manageRulesButton = QPushButton('Gestisci Regole', self)
        self.manageRulesButton.clicked.connect(self.showRuleDialog)
        layout.addWidget(self.manageRulesButton)

        # Aggiungi un nuovo pulsante per evidenziare gli elementi con nomi problematici
        self.highlightButton = QPushButton('Evidenzia Nomi Problematici', self)
        self.highlightButton.clicked.connect(self.highlight_poorly_named_items)
        layout.addWidget(self.highlightButton)

        self.setLayout(layout)

    def browse_folder(self):
        directory = QFileDialog.getExistingDirectory(self, 'Seleziona Cartella')
        if directory:
            self.pathEdit.setText(directory)

    def suggest_prompt(self):
        suggested_prompt = self.get_ai_suggestion("Suggerisci un prompt per rinominare file e cartelle")
        self.promptEdit.setText(suggested_prompt)

    def preview_changes(self):
        directory = self.pathEdit.text()
        prompt = self.promptEdit.toPlainText()

        if not directory or not prompt:
            QMessageBox.warning(self, 'Errore', 'Per favore, inserisci tutti i campi richiesti.')
            return

        try:
            preview_text = self.get_preview(directory, prompt)
            self.previewArea.setText(preview_text)
        except Exception as e:
            QMessageBox.critical(self, 'Errore', f'Si è verificato un errore durante l anteprima: {str(e)}')

    def rename_items(self):
        directory = self.pathEdit.text()
        prompt = self.promptEdit.toPlainText()

        if not directory or not prompt:
            QMessageBox.warning(self, 'Errore', 'Per favore, inserisci tutti i campi richiesti.')
            return

        self.progressBar.setVisible(True)
        self.progressBar.setValue(0)

        try:
            if self.filesOnlyRadio.isChecked():
                self.rename_files_only(directory, prompt)
            elif self.foldersOnlyRadio.isChecked():
                self.rename_folders_only(directory, prompt)
            elif self.allRadio.isChecked():
                self.rename_all(directory, prompt)
            else:
                raise ValueError("Nessuna opzione di rinomina selezionata")

            QMessageBox.information(self, 'Successo', 'Gli elementi sono stati rinominati con successo.')
        except Exception as e:
            QMessageBox.critical(self, 'Errore', f'Si è verificato un errore: {str(e)}')
        finally:
            self.progressBar.setVisible(False)

    def rename_all(self, directory, prompt):
        for root, dirs, files in os.walk(directory, topdown=False):
            items = dirs + files
            new_names = self.get_new_file_names(items, prompt)
            for old_name, new_name in zip(items, new_names):
                old_path = os.path.join(root, old_name)
                new_path = os.path.join(root, self.sanitize_filename(new_name))
                os.rename(old_path, new_path)

    def rename_files_only(self, directory, prompt):
        for root, _, files in os.walk(directory):
            new_names = self.get_new_file_names(files, prompt)
            for old_name, new_name in zip(files, new_names):
                old_path = os.path.join(root, old_name)
                new_path = os.path.join(root, self.sanitize_filename(new_name))
                os.rename(old_path, new_path)

    def rename_folders_only(self, directory, prompt):
        for root, dirs, _ in os.walk(directory, topdown=False):
            new_names = self.get_new_file_names(dirs, prompt)
            for old_name, new_name in zip(dirs, new_names):
                old_path = os.path.join(root, old_name)
                new_path = os.path.join(root, self.sanitize_filename(new_name))
                os.rename(old_path, new_path)

    def get_ai_suggestion(self, prompt):
        response = self.client.chat.completions.create(
            model="gpt-4o",  # Assicurati di avere accesso a GPT-4
            messages=[
                {"role": "system", "content": "Sei un assistente esperto nella rinominazione dei file."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            n=1,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()

    def get_new_file_names(self, file_names, prompt):
        model_prompt = f"{prompt}\n\nEcco gli elementi da rinominare:\n"
        for file_name in file_names:
            model_prompt += f"- {file_name}\n"
        model_prompt += "\nPer favore, fornisci solo l'elenco dei nuovi nomi, uno per riga, senza numerazione o trattini."

        response = self.client.chat.completions.create(
            model="gpt-4o",  # Assicurati di avere accesso a GPT-4
            messages=[
                {"role": "system", "content": "Sei un assistente esperto nella rinominazione dei file."},
                {"role": "user", "content": model_prompt}
            ],
            max_tokens=1000,
            n=1,
            temperature=0.7
        )

        new_names_text = response.choices[0].message.content.strip()
        new_file_names = [name.strip() for name in new_names_text.split("\n") if name.strip()]
        return new_file_names

    def sanitize_filename(self, filename):
        sanitized = re.sub(r'[<>:"/|?*]', '', filename)
        sanitized = sanitized.replace(' ', '_')
        return sanitized[:255]

    def get_preview(self, directory, prompt):
        preview = "Anteprima delle modifiche:\n\n"
        items = os.listdir(directory)
        new_names = self.get_new_file_names(items[:5], prompt)
        for old_name, new_name in zip(items[:5], new_names):
            preview += f"{old_name} -> {self.sanitize_filename(new_name)}\n"
        preview += "\n... (e altri elementi)"
        return preview


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FileRenamerApp()
    ex.show()
    sys.exit(app.exec_())