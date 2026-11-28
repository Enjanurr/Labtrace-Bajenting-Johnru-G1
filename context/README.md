# LabTrace Context Library

Use the focused reference that matches the task instead of treating old notes
or the root `README.md` as the implementation source of truth.

## Canonical references

| File | Use it for |
|---|---|
| [project-overview.md](project-overview.md) | Architecture, app boundaries, stack, environment, settings, and conventions |
| [domain-and-workflows.md](domain-and-workflows.md) | Entities, relationships, role policy, and end-to-end workflows |
| [api-routes-and-forms.md](api-routes-and-forms.md) | URL names, views, forms, templates, and JSON/AJAX behavior |
| [testing-and-ops.md](testing-and-ops.md) | Test map, commands, local operation, deployment caveats, and known verification limits |

These references are based on workspace source inspected on 2026-11-27.
Implementation facts come from source; test execution, production readiness,
and manual behavior are not inferred merely from code existing. Re-check files
when implementing a change.

## Supporting notes

- [improvements.md](improvements.md) is the implementation-checked feature
  backlog. It is not a substitute for issue tracking or acceptance criteria.
- [pd3-hardening-context.md](pd3-hardening-context.md) is a submission starter
  with fields and evidence placeholders; complete it only with verified
  results.
- [WBS_STATUS.md](WBS_STATUS.md) is a historical WBS audit snapshot dated
  2026-11-17. Its statuses and test totals are not current verification.
- [LOG.md](LOG.md) is a short dated handoff/change note.
- [FILETREE.md](FILETREE.md) is a concise module/file map. The route and
  architecture references above are the more useful task entry points.

## Source-of-truth order

1. Current Django source: models, forms, views, URL configurations, settings,
   migrations, templates, and tests.
2. The canonical context references above, updated when source changes.
3. Historical WBS/log notes, which may contain older findings.
4. Root `README.md`, which is currently stale in several details (for example
   dashboard scope, external asset requests, upload/image claims, and file
   tree). Its listed Python packages match `requirements.txt`.

Do not copy credentials, real user data, or password-reset output into context
files. No branch or pull-request workflow has been verified here; follow the
team's repository process and record the actual branch/PR in the PD3 report.
