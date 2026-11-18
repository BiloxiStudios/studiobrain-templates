// Type definitions for @studiobrain/templates
// This is a pure-data package; types cover the runtime entry point only.

export type SchemaName =
  | "base"
  | "compat"
  | "layout"
  | "views"
  | "template"
  | "pack"
  | "plugin" // RETIRED Python manifest schema (SBAI-12438). Not the plugin SDK.
  | "skill"
  | "taxonomy"
  | "character"
  | "location"
  | "item"
  | "faction"
  | "brand"
  | "district"
  | "job"
  | "quest"
  | "event"
  | "campaign"
  | "assembly"
  | "dialogue"
  | "timeline"
  | "universe"
  | "style_bible"
  | "biome";

export interface JsonSchema {
  $schema?: string;
  $id?: string;
  title?: string;
  description?: string;
  type?: string | string[];
  properties?: Record<string, unknown>;
  required?: string[];
  additionalProperties?: boolean | Record<string, unknown>;
  allOf?: unknown[];
  $defs?: Record<string, unknown>;
  [key: string]: unknown;
}

export const ROOT: string;
export const TEMPLATES_DIR: string;
export const RULES_DIR: string;
/** Intentionally absent path. Official plugins are not in this package (SBAI-7665, SBAI-12438). */
export const PLUGINS_DIR: string;
export const SCHEMAS_DIR: string;
export const SKILLS_DIR: string;
export const TAXONOMIES_DIR: string;
export const LAYOUTS_DIR: string;
export const PACKS_DIR: string;

/** schemas/registry/widget-ids.json: core's registered widget/block/view ids (SBAI-15043). */
export const WIDGET_IDS_FILE: string;

export interface WidgetIds {
  version: number;
  widgets: string[];
  aliases: Record<string, string>;
  renderer_only: string[];
  plugin_widget_pattern: string;
  component_blocks: string[];
  plugin_component_pattern: string;
  views: { core: string[]; cloud: string[] };
}

export const SCHEMA_FILES: Readonly<Record<SchemaName, string>>;

export function loadSchema(name: SchemaName | string): JsonSchema;
export function loadWidgetIds(): WidgetIds;
