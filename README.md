# VPS AI Engineering — Marketplace

Marketplace Claude Code personale per i miei plugin legati all'AI engineering.

## Scopo

Questo repository ospita un [marketplace di plugin per Claude Code](https://code.claude.com/docs/en/plugin-marketplaces): un unico punto da cui installare e mantenere aggiornati i plugin che uso nei miei progetti (skill, agent, hook), senza doverli copiare manualmente in ogni repo.

Al momento il marketplace pubblica un solo plugin:

- **[vps](plugins/vps)** — il mio plugin personale per l'AI engineering (skill, agent e hook di supporto allo sviluppo)

## Validazione

Per validare il plugin dopo una modifica lanciare

```sh
claude plugin validate .
```

## Installazione

Da Claude Code, aggiungi il marketplace:

```claude
/plugin marketplace add https://github.com/VvsGitH/vps-ai-engineering
```

Poi installa il plugin desiderato:

```claude
/plugin install vps@vps-ai-engineering
```

Per aggiornare il marketplace e i plugin installati quando questo repo viene modificato:

```claude
/plugin marketplace update vps-ai-engineering
```
