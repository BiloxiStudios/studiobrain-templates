# Catalog PR Automation Token (SBAI-8846)

Provisioning runbook for the narrowly scoped GitHub App token that the
`regenerate-catalog-index` CI job uses to open, mark auto-merge on, and land
`catalog-index.json` refresh PRs against a branch-protected `main`.

## Why this exists

Since SBAI-8394 landed branch protection with `enforce_admins` on `main`, the
old direct `git push origin HEAD:main` bot-commit fails GH006. SBAI-8599 moves
the bot to a PR + auto-merge flow. That flow requires a token that:

1. **Triggers required PR workflows on PR-open.** GitHub's default `GITHUB_TOKEN`
   suppresses the recursive-workflow chain by design — a PR opened via the
   default token does **not** fire `pull_request` workflows. The required
   status check (`hold-label-gate`) would therefore never report, and
   `gh pr merge --auto` would wait forever. A PR opened via a **GitHub App
   installation token** or **user PAT** does fire those workflows.
2. **Is narrowly scoped to this repo.** The shared org admin PAT
   (`GH_ADMIN_PAT`) that every agent authenticates as would work, but it
   carries admin scope across every repo in the org. A dedicated App with
   only the permissions this job needs is the least-privilege option and the
   one the manager approved for this ticket.
3. **Has a documented rotation path.** Personal Access Tokens tied to an
   individual expire and get revoked when that person leaves. An App is owned
   by the org and its private key can be rotated without touching workflows.

## Recommended: Dedicated GitHub App

Create a new GitHub App under the **BiloxiStudios** organization.

### App metadata

| Field | Value |
|---|---|
| **App name** | `studiobrain-templates-catalog-bot` |
| **Homepage URL** | `https://github.com/BiloxiStudios/studiobrain-templates` |
| **Webhook** | Disabled (unchecked "Active"; no webhook URL needed) |
| **Description** | "Opens PRs to refresh `catalog-index.json` on branch-protected `main`. See SBAI-8846." |

### Repository permissions (least-privilege)

| Permission | Access | Reason |
|---|---|---|
| **Contents** | Read & write | Create the `bot/catalog-index-update` branch and commit the regenerated file. |
| **Pull requests** | Read & write | Open the PR, enable auto-merge, close stale bot PRs. |
| **Metadata** | Read (mandatory default) | Required by every App. |
| **Workflows** | *(no access — do NOT grant)* | The regenerated `catalog-index.json` is data-only; App must not be able to modify `.github/workflows/**` even if a future bug tried to. |
| **Actions** | *(no access — do NOT grant)* | Same reason; the App has no legitimate need to trigger or cancel Actions runs. |

Organization permissions: **none required.**

Account permissions: **none required.**

### Installation

- Install the App on **only** `BiloxiStudios/studiobrain-templates`
  (choose "Only select repositories" — never "All repositories").
- Record the numeric **Installation ID** shown on the install page for the
  admin runbook; the CI job does not need it because
  `actions/create-github-app-token@v1` derives it from the repo context.

### Secrets to add

Add these **on the `plugins-publish` environment** (never as repo-wide
secrets — the catalog job already runs `environment: plugins-publish`, and
environment-scoping keeps them unreachable from any `pull_request`-triggered
job by branch-protection default):

| Secret name | Value | Rotation cadence |
|---|---|---|
| `CATALOG_BOT_APP_ID` | The App's numeric App ID (visible on the App settings page). | Only when the App itself is replaced. |
| `CATALOG_BOT_PRIVATE_KEY` | The full PEM contents of a private key generated on the App settings page. Include `-----BEGIN...-----` and trailing newline. | **Every 90 days minimum.** Generate a new key, upload it, then delete the old one from the App settings page. |

Do **not** paste the App ID or private key into any PR, comment, or log.
`gh secret set` reads values from stdin so nothing lands on disk:

```bash
# From an admin machine (never CI)
printf '%s' "$APP_ID"    | gh secret set CATALOG_BOT_APP_ID     --repo BiloxiStudios/studiobrain-templates --env plugins-publish
cat /path/to/private-key.pem | gh secret set CATALOG_BOT_PRIVATE_KEY --repo BiloxiStudios/studiobrain-templates --env plugins-publish
```

## Interim fallback: existing `GH_ADMIN_PAT`

The `plugins-publish` environment already carries `GH_ADMIN_PAT` (created
2026-08-22). It is a shared org admin PAT with far broader scope than this
job needs, but it **does** trigger `pull_request` workflows on PR-open, so
it is a valid fall-back while the App above is being provisioned. The CI
job in SBAI-8599 will consume the App token when both `CATALOG_BOT_APP_ID`
and `CATALOG_BOT_PRIVATE_KEY` are set, and fall back to `GH_ADMIN_PAT`
otherwise. Remove the fall-back once the App is confirmed working.

## Why not other options

- **Default `GITHUB_TOKEN`** — GitHub deliberately suppresses recursive
  workflow triggers for PRs it opens, so `hold-label-gate` never fires,
  and `gh pr merge --auto` waits forever. Ruled out.
- **Repo-level PAT of an individual maintainer** — expires and gets revoked
  when the maintainer leaves; not org-owned. Ruled out.
- **Fine-grained user PAT** — same expiry / individual-ownership problem;
  fine-grained tokens also have a hard 1-year max lifetime.
- **Deploy key** — has no `pull_request` API surface, so it can't open the PR
  or enable auto-merge. Ruled out.

## Proving the mechanism works

After adding the two secrets to the `plugins-publish` environment, run the
smoke workflow to prove a token-created PR triggers required workflows and
lands cleanly:

```bash
gh workflow run catalog-bot-token-smoke.yml --repo BiloxiStudios/studiobrain-templates
```

The workflow will:

1. Mint a short-lived installation token from the App credentials.
2. Open a no-op PR against `main` from a `bot/catalog-token-smoke-<sha>` branch.
3. Wait up to 3 minutes for the required `hold-label-gate` status check to
   report on that PR.
4. Enable auto-merge (squash) using the App token.
5. Report **pass** if the PR merged and the check ran, **fail** otherwise.
6. Clean up the smoke branch on either outcome.

A green run of the smoke workflow is the acceptance evidence for SBAI-8846.

## Rotation runbook

Every 90 days:

1. On the App settings page, generate a new private key. Download the `.pem`.
2. Upload the new PEM to the `plugins-publish` environment as
   `CATALOG_BOT_PRIVATE_KEY` (overwrite).
3. Re-run `catalog-bot-token-smoke.yml` and confirm it stays green.
4. On the App settings page, **delete the old private key.**
5. Note the rotation date in this file (append below).

### Rotation history

- *(none yet — first entry belongs to whoever completes SBAI-8846.)*
