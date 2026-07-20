# VPS AI ENGINEERING

My personal Claude Code plugin for AI Engineering

## Skills copiate da mattpocock/skills

Le skill in `skills/` partono dal repo [mattpocock/skills](https://github.com/mattpocock/skills), da cui sono state copiate e poi adattate a questo progetto:

- `code-review` — review delle modifiche rispetto a standard di codice e spec del ticket/issue di origine
- `domain-modeling` — costruisce e affina il modello di dominio di un progetto (glossario, ADR)
- `grill-with-docs` — intervista serrata per affinare un piano/design, producendo ADR e glossario
- `grilling` — mette sotto torchio l'utente su un piano, una decisione o un'idea
- `implement` — implementa un pezzo di lavoro a partire da una spec o da un set di ticket
- `init-project` — configura il repo per le skill di engineering (issue tracker locale, domain doc); sostituisce l'originale `setup-matt-pocock-skills`
- `research` — indaga una domanda su fonti primarie affidabili e salva i risultati come file Markdown
- `tdd` — sviluppo test-driven (red-green-refactor)
- `teach` — insegna all'utente una nuova skill o concetto nel contesto del workspace
- `to-spec` — trasforma la conversazione corrente in una spec pubblicata sull'issue tracker
- `to-tickets` — scompone un piano/spec/conversazione in ticket tracer-bullet con dipendenze esplicite
- `writing-great-skills` — riferimento su come scrivere ed editare bene le skill

## Hooks

Hook `PreToolUse` (su `Bash`/`PowerShell`) definiti in `hooks/hooks.json`:

- `block-git-commit.py` — chiede conferma prima di eseguire un `git commit`
- `strip-co-authored-by.py` — rimuove dai messaggi di commit i trailer di attribuzione AI (`Co-Authored-By: Claude <…>` e `🤖 Generated with [Claude Code](…)`), riscrivendo il comando prima dell'esecuzione. I co-author umani non vengono toccati.
