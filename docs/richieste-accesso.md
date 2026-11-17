# Bozze di richiesta di accesso (Fase 1)

Bozze da inviare dal titolare del progetto. Riempire i campi tra parentesi quadre. Contesto comune: People Placement è una directory statica, gratuita e senza registrazione di stage HR per studenti universitari. Mostra solo metadati (titolo, datore di lavoro, luogo, date, lingua) e rimanda sempre all'annuncio originale; non pubblica testi completi né dati personali. Il codice è pubblico: https://github.com/nightlydeveloper8/eu-hr-internships.

Dopo la risposta, annotarla in [fonti-pubbliche.md](fonti-pubbliche.md) prima di abilitare qualsiasi fonte.

---

## 1. European Labour Authority – EURES (inglese)

**A:** eures@ela.europa.eu (EURES Helpdesk / Information and EURES Unit)
**Oggetto:** Request for permission to reuse EURES job vacancy data in a non-commercial internship directory

Dear EURES team,

I coordinate People Placement, a free, non-commercial directory of human-resources internships for university students across the EU, Switzerland and the United Kingdom ([project URL]). It is run by [name], [institution].

We would like to show EURES vacancies that are explicitly internships or traineeships in HR. We would display only the title, employer, location, dates and language, with a direct link to the original EURES advertisement. We would not republish full descriptions or any personal or contact data.

Before integrating anything, we would like to confirm three points:

1. The EURES legal notice allows reuse of ELA content with acknowledgement. Does this also cover job vacancies that national public employment services transmit to EURES, or do national licences apply to them?
2. Is there a documented interface (API, export or data feed) that third parties may use to retrieve published vacancies? If so, under what conditions and with what rate limits?
3. If no such interface exists, may we query the public search used by the portal at a low rate (for example, once a day with a few keyword searches)? Or do you prefer that we refrain?

We will follow any attribution, rate-limit or removal requirements you set. We will not proceed until we receive your answer.

Kind regards,
[Name, role, institution, e-mail]

---

## 2. Bundesagentur für Arbeit – Jobsuche (tedesco)

**A:** Kontaktformular der BA / Service für Kooperationspartner (Jobbörse)
**Betreff:** Anfrage zur Nutzung der Jobsuche-Daten für ein nichtkommerzielles Praktikumsverzeichnis

Sehr geehrte Damen und Herren,

wir betreiben People Placement, ein kostenloses, nichtkommerzielles Verzeichnis von HR-Praktika für Studierende ([Projekt-URL], verantwortlich: [Name, Hochschule]).

Ihre Nutzungsbedingungen (§ 2a Abs. 3) untersagen Robots und die unautorisierte Nutzung von Programmierschnittstellen. Deshalb nutzen wir die Jobsuche derzeit nicht. Wir möchten fragen, ob eine autorisierte Nutzung möglich ist, zum Beispiel über eine Kooperation oder eine dokumentierte Schnittstelle. Konkret geht es um Stellenangebote der Angebotsart Praktikum/Trainee im Personalbereich, abgefragt höchstens einmal täglich.

Angezeigt würden nur Titel, Arbeitgeber, Ort und Daten, jeweils mit Link auf das Originalangebot in der Jobbörse. Wir zeigen keine Volltexte und keine personenbezogenen Daten an. Wir löschen Angebote, sobald sie in der Jobbörse nicht mehr verfügbar sind.

Welche Voraussetzungen und Bedingungen gelten dafür?

Mit freundlichen Grüßen
[Name, Funktion, Hochschule, E-Mail]

---

## 3. SECO – Job-Room / arbeit.swiss (tedesco)

**An:** SECO, Direktion für Arbeit, Arbeitsmarkt/Arbeitslosenversicherung (Kontakt über arbeit.swiss)
**Betreff:** Gesuch um schriftliche Zustimmung zur Anzeige von Praktikumsangeboten aus dem Job-Room

Sehr geehrte Damen und Herren,

People Placement ([Projekt-URL]) ist ein kostenloses, nichtkommerzielles Verzeichnis von HR-Praktika für Studierende in der EU, der Schweiz und dem Vereinigten Königreich (verantwortlich: [Name, Hochschule]).

Ihre rechtlichen Hinweise verlangen für die Reproduktion von Elementen und für die Integration in andere Websites eine vorgängige schriftliche Zustimmung. Wir ersuchen deshalb um diese Zustimmung für folgende Nutzung:

- Abruf öffentlich publizierter Stellen mit Praktikumsbezug im Personalbereich, höchstens einmal täglich.
- Anzeige von Titel, Arbeitgeber, Ort und Daten mit Link auf das Originalinserat.
- Keine Volltexte, keine Kontaktdaten.
- Entfernung, sobald das Inserat nicht mehr publiziert ist.

Falls dafür eine dokumentierte Schnittstelle oder eine Vereinbarung vorgesehen ist, teilen Sie uns bitte die Bedingungen mit.

Freundliche Grüsse
[Name, Funktion, Hochschule, E-Mail]

---

## 4. France Travail – API Offres d'emploi (francese)

**À :** support francetravail.io (formulaire de contact de la plateforme)
**Objet :** API Offres d'emploi v2 – robots.txt de api.francetravail.io et réutilisation non commerciale

Madame, Monsieur,

Nous développons People Placement ([URL du projet], responsable : [nom, établissement]). C'est un annuaire gratuit et non commercial de stages en ressources humaines pour étudiants.

Nous souhaitons utiliser l'API Offres d'emploi v2 en adhérant à la licence de réutilisation des offres. Cependant, le fichier `https://api.francetravail.io/robots.txt` interdit l'accès à tous les agents (`User-Agent: *`, `Disallow: /`). Notre politique est de respecter strictement les fichiers robots.txt.

Pourriez-vous nous confirmer qu'une application enregistrée sur francetravail.io, authentifiée par OAuth2 et respectant les quotas, est autorisée à appeler l'API malgré ce fichier ? Nous n'afficherions que le titre, l'employeur, le lieu et les dates, avec un lien vers l'offre originale, sans données de contact.

Nous vous remercions par avance.

Cordialement,
[Nom, fonction, établissement, e-mail]
