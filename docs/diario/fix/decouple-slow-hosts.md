## 24 novembre 2026 — raccolta indipendente per gli host lenti

Gi Group passa dalla corsia critica di collect.yml a slow-hosts.yml, con cadenza invariata di 120 s, cron alle 03:17 UTC, timeout di 60 minuti e artefatto valido per 48 ore. Il publish delle 06:17 UTC continua con o senza uno snapshot recente.
Verifiche locali su stato assente, scaduto e riusato, conservazione ID e provisioning idempotente. Baseline [35m30s](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/45387756065), 1.104 ID e 578 stage aperti.
Prossimo passo: dispatch della corsia lenta e verifica del primo publish che consuma l’artefatto, con obiettivo sotto 26 minuti.
