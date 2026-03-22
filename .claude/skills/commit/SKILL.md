---
name: commit
description: Generate conventional commit messages from git diffs. Use when committing code, writing commit messages, or when user says "commit". Supports -br for Portuguese, -c for commit only, -p/-push for commit + push.
argument-hint: [-br] [-c | -p | -push]
allowed-tools: Bash, Read, Grep
---

# Commit

Generate conventional commit message from staged/unstaged changes.

## Quick Start

1. Run `bash scripts/analyze-changes.sh` or manually: `git status --short && git diff --stat`
2. Determine: type, scope, description
3. Generate message in imperative mood

## Format

```
<type>(<scope>): <description>

<optional body>
```

## Types (priority order)

feat | fix | refactor | perf | style | docs | test | chore | build | ci

## Rules

- **ALWAYS commit ALL changes** from `git status` — nothing should be left behind
- Group changes into **separate logical commits** when they belong to different concerns (e.g. config, feature, docs)
- Imperative mood: "add" not "added" / "adiciona" not "adicionado"
- No capital, no period, max 50 chars
- Scope: nome da entidade principal alterada, em português (ex: usuários, tarefas, pedidos)
  - Exceção: palavras que são estrangeirismos comuns podem ficar em inglês (ex: squads, sprints, dashboards)
- NEVER include Co-Authored-By or any signature lines

## Flags

| Flag            | Language   | Action                      |
| --------------- | ---------- | --------------------------- |
| (none)          | English    | Dry run (show command only) |
| -c              | English    | Stage + commit (no push)    |
| -p / -push      | English    | Stage + commit + push       |
| -br             | Portuguese | Dry run (show command only) |
| -br -c          | Portuguese | Stage + commit (no push)    |
| -br -p / -push  | Portuguese | Stage + commit + push       |

## Examples

- English: See [refs/examples-en.md](refs/examples-en.md)
- Portuguese: See [refs/examples-br.md](refs/examples-br.md)

## Execution

**Dry run**: Show `git add -A && git commit -m "<message>"`
**With -c**: Execute staging and commit, then show `git log -1 --oneline`
**With -p/-push**: Execute staging, commit, push, then show `git log -1 --oneline`
