# Fase 3 — Percorsi di candidatura Adecco Francia

Catalogo `a71b260`, 21 novembre 07:35 UTC. Tutti gli **87** lead con `missing-application-entry` della fonte `employer-adecco-group` sono in Francia. Campione mirato di cinque posting distinti: tre località dal catalogo e due già esaminate nel pilota. GET delle vacancy e delle sole destinazioni Talentsoft osservate, dopo robots.txt su entrambi gli host, con almeno un secondo fra richieste allo stesso host. Tutte e cinque le vacancy rispondono HTTP 200, con titolo e ID strutturato coincidenti e nessun modulo di candidatura specifico visibile.

| Vacancy Radancy | ID catalogo | ID Talentsoft | Destinazione della CTA |
| --- | --- | --- | --- |
| [Aire-sur-l’Adour](https://careers.adeccogroup.com/en/job/aire-sur-l-adour/charge-de-recrutement-en-stage-h-f/26094/89175218336) | `203125dcc3b2a46d7a29` | 18464 | [Scheda Talentsoft](https://theadeccogroup-career.talent-soft.com/Pages/Offre/detailoffre.aspx?idOffre=18464&idOrigine=502&LCID=1036&offerReference=01W10%2fZAA%2f01182%2fCR-18464) |
| [Albi](https://careers.adeccogroup.com/en/job/albi/stage-assistant-recrutement-h-f/26094/95243497168) | `a73a92cc966a3ac72d88` | 19323 | [Scheda Talentsoft](https://theadeccogroup-career.talent-soft.com/Pages/Offre/detailoffre.aspx?idOffre=19323&idOrigine=502&LCID=1036&offerReference=2026-19323) |
| [Argentan](https://careers.adeccogroup.com/en/job/argentan/charge-de-recrutement-h-f-stagiaire-h-f/26094/103424521360) | `b49492af907d10143760` | 20124 | [Scheda Talentsoft](https://theadeccogroup-career.talent-soft.com/Pages/Offre/detailoffre.aspx?idOffre=20124&idOrigine=502&LCID=1036&offerReference=W13%2fZBC%2f384+STAGIAIRE+RECRUTEMENT+H%2fF-20124) |
| [Pornic](https://careers.adeccogroup.com/en/job/pornic/charge-de-recrutement-en-stage-h-f/26094/95575810976) | `fd30839bb766e2c567a6` | 19376 | [Scheda Talentsoft](https://theadeccogroup-career.talent-soft.com/Pages/Offre/detailoffre.aspx?idOffre=19376&idOrigine=502&LCID=1036&offerReference=01W10%2fZAH%2f01I61%2fCR-19376) |
| [Saint-Martin-sur-le-Pré](https://careers.adeccogroup.com/en/job/saint-martin-sur-le-pre/stagiaire-charge-e-de-recrutement-h-f/26094/99388372416) | `fe8122bf9c6d7d0de11c` | 19813 | [Scheda Talentsoft](https://theadeccogroup-career.talent-soft.com/Pages/Offre/detailoffre.aspx?idOffre=19813&idOrigine=502&LCID=1036&offerReference=ZCR%2fST+MARTIN+SUR++PRE+(51)%2fSTAGIAIRE+CR-19813) |

In tutti e cinque i casi **Apply for Role** apre una scheda Talentsoft HTTP 200 con titolo coincidente. Il parametro `offerReference` della CTA coincide esattamente con l'ID strutturato della pagina Adecco e `idOffre` distingue le cinque schede. L'HTML Talentsoft mostra gli stessi due percorsi per il candidato:

| Link osservato | Destinazione | ID del posting nel collegamento |
| --- | --- | --- |
| Candidature spontanée | `/mon-compte/mon-fichier-cv.aspx?ApplicationType=…`, percorso generico CV/spontanea | Assente |
| Je me crée un espace candidat | `/my-account/log-in.aspx?titletype=…`, creazione account/login | Assente |

Non sono emersi link email di candidatura, né moduli visibili con campi candidato e invio abilitato. I percorsi account/CV sono stati classificati dagli URL osservati, senza aprirli. La prova copre l'HTML pubblico dei cinque posting e non stabilisce cosa sia disponibile dopo login o esecuzione di JavaScript. Il [pilota precedente](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44736268862) aveva documentato lo stesso passaggio a un CV/account senza ID.

**Esito B per il campione:** proporre la causale «Percorso di candidatura specifico non disponibile presso il datore» per i posting in cui si osserva la scheda Talentsoft con i soli percorsi generico e account. Questi casi escono dalla coda delle correzioni di estrazione finché non appare un percorso pubblico specifico. Per gli altri lead della fonte serve evidenza equivalente prima di attribuire la causale. Recupero previsto da questa PR: **0**.

Costo in staging, contando i byte dei corpi letti: prima passata **6 GET HTTP e 1 tentativo interrotto dal TLS**, **441,422 byte**, **5.773 s**. Seconda passata sugli stessi cinque posting, con il trust store di macOS: **12 GET**, **1,243,585 byte**, **8.412 s**. Totale **18 GET HTTP (19 tentativi), 1,685,007 byte, 14.185 s** di tempo a muro cumulato. Zero login, POST o invii. Il catalogo prima/dopo conserva **906 → 906 ID, 402 → 402 stage verificati, 37 → 37 candidature dirette, 367 → 367 lead**, con zero ID persi.
