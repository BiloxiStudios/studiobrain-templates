# Platform defaults (SBAI-7974)

Per-surface declarations of engine/framework choice and default catalog
weight/model rows. **This is where platform divergence lives.** Catalog
bodies stay in `templates/Providers/*.provider.yaml` — never a single
`providers.yaml`.

| File | Surface |
|---|---|
| `web.platform.yaml` | Browser |
| `desktop.platform.yaml` | Desktop app |
| `ios.platform.yaml` | iOS |
| `android.platform.yaml` | Android |

A project or build may overlay a singular `platform.yaml` — same schema
(`schemas/platform.json`). Settings overlay `limits` at runtime.

`engine.category` reuses model-manager `engines.schema.json` v2 taxonomy.
`wire` is protocol-level and does not belong in these files.
