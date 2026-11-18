"use strict";
/**
 * @studiobrain/templates — pure-data entry point.
 *
 * Re-exports filesystem paths to bundled directories and a small helper for
 * loading JSON Schemas. No runtime logic; safe to import from a browser
 * bundle (paths are string constants, schema loading is opt-in).
 */

const path = require("path");

const ROOT = __dirname;

const TEMPLATES_DIR = path.join(ROOT, "templates");
const RULES_DIR = path.join(ROOT, "rules");
// Intentionally absent. Repo-root plugins/ was removed in SBAI-7665.
// Do not recreate it. Official plugins live in studiobrain-plugins.
const PLUGINS_DIR = path.join(ROOT, "plugins");
const SCHEMAS_DIR = path.join(ROOT, "schemas");
const SKILLS_DIR = path.join(ROOT, "skills");
const TAXONOMIES_DIR = path.join(ROOT, "taxonomies");
const LAYOUTS_DIR = path.join(TEMPLATES_DIR, "Layouts");
/**
 * Export of studiobrain-core's registered widget / component-block / view ids
 * (SBAI-15043). Data, not a JSON Schema. scripts/validate.py lints shipped
 * layouts and templates against it; keep it in sync with core.
 */
const WIDGET_IDS_FILE = path.join(SCHEMAS_DIR, "registry", "widget-ids.json");
const PACKS_DIR = path.join(TEMPLATES_DIR, "Packs");

/**
 * Map of logical schema name -> filename inside schemas/.
 * Keep in sync with schemas/README.md "Schema family overview".
 */
const SCHEMA_FILES = Object.freeze({
  base: "_base.json",
  compat: "_compat.json",
  layout: "layout.json",
  views: "views.json",
  template: "template.json",
  pack: "pack.json",
  // RETIRED Python manifest schema (SBAI-12438). Not the runtime plugin SDK.
  plugin: "plugin.json",
  skill: "skill.yaml.json",
  taxonomy: "taxonomy.json",
  character: "character.json",
  location: "location.json",
  item: "item.json",
  faction: "faction.json",
  brand: "brand.json",
  district: "district.json",
  job: "job.json",
  quest: "quest.json",
  event: "event.json",
  campaign: "campaign.json",
  assembly: "assembly.json",
  dialogue: "dialogue.json",
  timeline: "timeline.json",
  universe: "universe.json",
  style_bible: "style_bible.json",
  biome: "biome.json",
});

/**
 * Load a JSON Schema by logical name. Returns the parsed schema object.
 *
 * @param {keyof typeof SCHEMA_FILES | string} name
 * @returns {object}
 */
function loadSchema(name) {
  const filename = SCHEMA_FILES[name] || `${name}.json`;
  // eslint-disable-next-line global-require
  return require(path.join(SCHEMAS_DIR, filename));
}

/**
 * Load the widget-id export (widgets, aliases, component_blocks, views).
 *
 * @returns {object}
 */
function loadWidgetIds() {
  // eslint-disable-next-line global-require
  return require(WIDGET_IDS_FILE);
}

module.exports = {
  ROOT,
  TEMPLATES_DIR,
  RULES_DIR,
  PLUGINS_DIR,
  SCHEMAS_DIR,
  SKILLS_DIR,
  TAXONOMIES_DIR,
  LAYOUTS_DIR,
  PACKS_DIR,
  WIDGET_IDS_FILE,
  SCHEMA_FILES,
  loadSchema,
  loadWidgetIds,
};
