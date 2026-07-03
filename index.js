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
const PLUGINS_DIR = path.join(ROOT, "plugins");
const SCHEMAS_DIR = path.join(ROOT, "schemas");
const SKILLS_DIR = path.join(ROOT, "skills");
const LAYOUTS_DIR = path.join(TEMPLATES_DIR, "Layouts");
const PACKS_DIR = path.join(TEMPLATES_DIR, "Packs");

/**
 * Map of logical schema name -> filename inside schemas/.
 * Keep in sync with schemas/README.md "Schema family overview".
 */
const SCHEMA_FILES = Object.freeze({
  base: "_base.json",
  compat: "_compat.json",
  layout: "layout.json",
  pack: "pack.json",
  plugin: "plugin.json",
  skill: "skill.yaml.json",
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

module.exports = {
  ROOT,
  TEMPLATES_DIR,
  RULES_DIR,
  PLUGINS_DIR,
  SCHEMAS_DIR,
  SKILLS_DIR,
  LAYOUTS_DIR,
  PACKS_DIR,
  SCHEMA_FILES,
  loadSchema,
};
