# Oracle Recruiting, verifica di accesso del 24 novembre 2026

L'API Recruiting CE è esclusa dal campione. Oracle specifica «the service endpoints in this resource category are only for Oracle internal use». La sezione 7 dei termini Oracle vieta l'automazione in assenza di autorizzazione scritta con la formula «not to use any robot, spider, scraper or other automated means to access the Site». L'applicabilità di quei termini ai distinti siti pubblici dei datori richiede una verifica per host. [Documentazione API](https://docs.oracle.com/en/cloud/saas/human-resources/farws/api-recruiting-ce-job-requisitions.html) · [Termini Oracle §7](https://www.oracle.com/legal/terms/#section7).

| Datore | Prova robots del percorso candidato | Esito del sito pubblico e volume HR |
|---|---|---|
| Eni | [jobs.eni.com](https://jobs.eni.com/robots.txt) → 302 | Incerto, non dimostrato |
| Poste Italiane | [Oracle tenant](https://fa-emza-saasfaprod1.fa.ocs.oraclecloud.com/robots.txt) → 404 | Incerto, non dimostrato |
| Unipol | [Oracle tenant](https://hdix.fa.em3.oraclecloud.com/robots.txt) → 404 | Incerto, non dimostrato |
| A2A | [Oracle tenant](https://hdeh.fa.em3.oraclecloud.com/robots.txt) → 404 | Incerto, non dimostrato |
| Hera | [Oracle tenant](https://hdbj.fa.em2.oraclecloud.com/robots.txt) → 404 | Incerto, non dimostrato |
| BPER | [Oracle tenant](https://fa-ewnv-saasfaprod1.fa.ocs.oraclecloud.com/robots.txt) → 404 | Incerto, non dimostrato |
| Nexi | [Oracle tenant](https://fa-ewwx-saasfaprod1.fa.ocs.oraclecloud.com/robots.txt) → 404 | Incerto, non dimostrato |
| Amplifon | [careers.amplifon.com](https://careers.amplifon.com/robots.txt) → 302 | Incerto, non dimostrato |
| INWIT | [www.inwit.it](https://www.inwit.it/robots.txt) → 200 | Tenant Oracle e percorso non dimostrati, volume non dimostrato |

9 GET di preflight. Il censimento riporta `stage_hr_visibili=non_verificato` per tutti e nove.
