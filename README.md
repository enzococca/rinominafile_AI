# File Renamer AI

## Descrizione
File Renamer AI è un'applicazione desktop che utilizza l'intelligenza artificiale per rinominare file e cartelle in modo intelligente e personalizzato. Sfruttando le potenzialità di GPT-4, questo programma offre suggerimenti di rinomina basati su prompt dell'utente e applica regole personalizzabili per garantire nomi di file coerenti e organizzati.

## Caratteristiche principali
- Rinomina intelligente di file e cartelle utilizzando l'AI
- Interfaccia grafica user-friendly
- Possibilità di rinominare solo file, solo cartelle o entrambi
- Anteprima delle modifiche prima dell'applicazione
- Gestione di regole personalizzate per la rinomina
- Evidenziazione di nomi di file problematici

## Requisiti di sistema
- Windows 10 o superiore
- Python 3.7 o superiore
- Connessione internet (per l'utilizzo dell'API OpenAI)

## Installazione e avvio

1. **Scaricare il progetto**:
   Scarica tutti i file del progetto e posizionali in una cartella sul tuo computer.

2. **Preparazione**:
   Assicurati di avere Python installato sul tuo sistema. Puoi scaricarlo da [python.org](https://www.python.org/downloads/).

3. **Avvio del programma**:
   - Fai doppio clic sul file `rinomina.bat`.
   - Questo script batch farà quanto segue:
     1. Verificherà la presenza di Python sul tuo sistema.
     2. Creerà un ambiente virtuale Python.
     3. Installerà tutte le dipendenze necessarie.
     4. Avvierà l'applicazione.

4. **Primo avvio**:
   Al primo avvio, ti verrà richiesto di inserire la tua API key di OpenAI. Questa verrà salvata in un file di testo per usi futuri.

## Utilizzo del programma

1. **Seleziona la cartella**: Usa il pulsante "Sfoglia" per selezionare la cartella contenente i file/cartelle da rinominare.

2. **Scegli cosa rinominare**: Seleziona se vuoi rinominare solo file, solo cartelle o entrambi.

3. **Inserisci il prompt**: Scrivi un prompt che descrive come vuoi rinominare i tuoi file/cartelle.

4. **Anteprima**: Clicca su "Anteprima" per vedere come verranno rinominati i tuoi file/cartelle.

5. **Rinomina**: Se sei soddisfatto dell'anteprima, clicca su "Rinomina" per applicare le modifiche.

6. **Gestione regole**: Usa il pulsante "Gestisci Regole" per creare, modificare o eliminare regole di rinomina.

7. **Evidenzia problemi**: Il pulsante "Evidenzia Nomi Problematici" ti mostrerà quali file/cartelle non rispettano le regole impostate.

## Nota sulla sicurezza
L'API key di OpenAI viene salvata localmente sul tuo computer. Assicurati di mantenere questo file sicuro e non condividerlo.

## Supporto
Per problemi o domande, apri una issue su GitHub o contatta il supporto tecnico.
