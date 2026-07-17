# Marketplace

Questo repository è un [marketplace di plugin Claude Code](https://code.claude.com/docs/en/plugin-marketplaces): `.claude-plugin/marketplace.json` alla radice elenca i plugin pubblicati, ciascuno vive sotto `plugins/<nome>/` con il proprio `.claude-plugin/plugin.json`.

Struttura:

```
.claude-plugin/marketplace.json   # manifest del marketplace (name, owner, plugins[])
README.md                         # descrizione del marketplace e istruzioni d'installazione
plugins/
  vps/                            # unico plugin pubblicato al momento
    .claude-plugin/plugin.json    # manifest del plugin (name, version, author, ...)
    README.md                     # descrizione del plugin e delle sue skill
    skills/                       # auto-discovered da Claude Code
    hooks/                        # hooks.json + script, auto-discovered
    agents/                       # auto-discovered
```

Regole da rispettare quando si tocca questa struttura:

- Il campo `source` di ogni entry in `plugins[]` (in `marketplace.json`) deve essere un path relativo che inizia con `./` (es. `./plugins/vps`), risolto rispetto alla directory che contiene `.claude-plugin/`. Path assoluti (`/plugins/vps`) o con `../` non sono validi.
- Skill, hook e agent di un plugin vanno messi a livello root del plugin (`plugins/<nome>/skills`, `plugins/<nome>/hooks`, ecc.), **non** dentro `.claude-plugin/`: quella cartella contiene solo `plugin.json`.
- Dopo modifiche a `marketplace.json` o `plugin.json`, valida con `claude plugin validate .` (o il path del singolo plugin).
- Per aggiungere un nuovo plugin: creare `plugins/<nome>/.claude-plugin/plugin.json` e aggiungere una entry `{ "name": "<nome>", "source": "./plugins/<nome>" }` in `plugins[]`.

# Plugin `vps` — origine delle skill e workflow di aggiornamento

Le skill in `plugins/vps/skills/` sono state copiate da [mattpocock/skills](https://github.com/mattpocock/skills) (commit `70cdeea`) e poi adattate localmente (commit `3c7b1d9`). Questa sezione serve a **rendere veloce il prossimo aggiornamento**: quando mattpocock cambia qualcosa a monte, qui trovi da dove viene ogni skill e cosa abbiamo modificato rispetto all'originale, così puoi capire cosa va ripreso pari pari e cosa invece va riadattato.

## Mappa skill copiata → percorso upstream

Nel repo di mattpocock le skill sono organizzate in bucket (`engineering/`, `productivity/`, ecc.), qui invece sono tutte appiattite sotto `plugins/vps/skills/`. Mappa:

| Skill locale           | Percorso upstream                             |
| ---------------------- | ---------------------------------------------- |
| `code-review`          | `skills/engineering/code-review`                |
| `domain-modeling`      | `skills/engineering/domain-modeling`            |
| `grill-with-docs`      | `skills/engineering/grill-with-docs`            |
| `implement`            | `skills/engineering/implement`                  |
| `research`             | `skills/engineering/research`                   |
| `tdd`                  | `skills/engineering/tdd`                        |
| `to-spec`              | `skills/engineering/to-spec`                    |
| `to-tickets`           | `skills/engineering/to-tickets`                 |
| `grilling`             | `skills/productivity/grilling`                  |
| `teach`                | `skills/productivity/teach`                     |
| `writing-great-skills` | `skills/productivity/writing-great-skills`      |
| `init-project`         | `skills/engineering/setup-matt-pocock-skills` (riscritta, non 1:1 — vedi sotto) |

Skill upstream **non copiate** (scelta consapevole, non dimenticanza): `ask-matt`, `codebase-design`, `diagnosing-bugs`, `improve-codebase-architecture`, `prototype`, `resolving-merge-conflicts`, `triage`, `wayfinder`, `grill-me`, `handoff`.

## Cosa abbiamo modificato rispetto all'originale

Queste sono le uniche divergenze intenzionali dall'upstream. Quando risincronizzi una skill, **riapplica queste modifiche** invece di sovrascriverle:

- **`setup-matt-pocock-skills` → `init-project`**: rinominata e semplificata. L'originale supporta issue tracker locale, GitHub e GitLab (`issue-tracker-local.md`, `issue-tracker-github.md`, `issue-tracker-gitlab.md`, `triage-labels.md`); la nostra versione tiene solo il tracker locale (file markdown sotto `docs/issues/`) e ha buttato via il vocabolario delle triage label.
- **`code-review`, `to-spec`, `to-tickets`**: i riferimenti a `` `/setup-matt-pocock-skills` `` sono stati sostituiti con `` `/init-project` ``.
- **`to-spec`, `to-tickets`**: le menzioni di "triage label" sono diventate "status", coerentemente con la rimozione del vocabolario di triage.
- **`to-tickets`**: il percorso dei ticket locali è `docs/issues/<feature-slug>/<NN>-<slug>.md` invece di `.scratch/<feature-slug>/issues/<NN>-<slug>.md`.

Tutto il resto (incluse le `agents/openai.yaml` di ogni skill) è stato copiato senza modifiche.

## Workflow di aggiornamento

1. Clona/pulla `mattpocock/skills` a parte e fai il diff tra la versione upstream di una skill e la nostra copia in `plugins/vps/skills/<nome>` (usando la mappa sopra per trovare il percorso).
2. Se l'upstream è cambiato, applica le stesse modifiche qui, **ripassando poi la lista "Cosa abbiamo modificato"** per non perdere gli adattamenti locali (in particolare i riferimenti a `/init-project` e i percorsi `docs/issues/`).
3. Per `init-project`: non fare un copia-incolla di `setup-matt-pocock-skills` — è stata riscritta da zero per il solo tracker locale, quindi confronta solo le parti di logica/contenuto rilevanti (es. `docs/agents/domain.md`, formato issue tracker locale).
4. Aggiorna la tabella sopra se aggiungi, rimuovi o rinomini una skill copiata.
