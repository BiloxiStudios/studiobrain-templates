// Type definitions for @studiobrain/templates
// This is a pure-data package; types cover the runtime entry point only.

export type SchemaName =
  | "base"
  | "compat"
  | "layout"
  | "pack"
  | "plugin"
  | "skill"
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
export const PLUGINS_DIR: string;
export const SCHEMAS_DIR: string;
export const SKILLS_DIR: string;
export const LAYOUTS_DIR: string;
export const PACKS_DIR: string;

export const SCHEMA_FILES: Readonly<Record<SchemaName, string>>;

export function loadSchema(name: SchemaName | string): JsonSchema;
