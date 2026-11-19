# Reference generation canvases

These four catalog recipes describe a character and scene reference workflow. Each recipe produces a candidate. A person selects the project asset to use in the next recipe after reviewing the candidate. The approval slots are separate from candidate outputs and have no automatic binding.

## Example review sequence

1. Select the Character **Mara Vale** and set her eye colour to amber. Supply the hairstyle `black braided bob` and the other traits you want preserved, such as the scar over her right eyebrow. Use **Draft reference headshot** with a portrait brief, or select an existing headshot from the project's assets, such as the Character's primary image. Compare the candidate with the chosen eye colour, hairstyle, and traits before selecting it as `approved_headshot`.
2. Use **Draft reference turnaround** with that headshot and the same traits. Ask for full-body front, side, and back views in the brief. Compare the proportions and key details across all three views. Keep the version you accept as a separate project asset and select it as `approved_turnaround`.
3. Use **Draft reference story sheet** with the approved headshot and turnaround. Select the **North Arcade** Location and one of its project artwork assets, then select the **Lantern Thread** Brand and its approved logo artwork. The brief specifies the shot sequence and where the logo belongs. Review the character continuity, location, and brand treatment. Select a single acceptable frame and save that frame as a project asset before binding it as `approved_frame`.
4. Use **Draft video from frame** with that frame, the same Location, and a motion brief. The recipe's video step receives the chosen frame.

Keep the asset ID or version of each accepted reference. When a candidate needs revision, retry that recipe with the same accepted inputs and a revised brief. Save the retry as another candidate. Replace a selected reference only after reviewing the revision and choosing it explicitly. Leaving the earlier accepted asset selected keeps retries from changing downstream inputs.

## Custom entity types

Copy a recipe into your project to adapt it. For a custom `performer` type with authored fields `stage_name`, `iris_colour`, and `haircut`, replace `character` in `entity_types` and bind the same slots to `entity.performer[0].stage_name`, `entity.performer[0].iris_colour`, and `entity.performer[0].haircut`. Keep the approved asset slots as explicit project selections. Make the same field substitutions in any downstream recipe that uses the performer. This preserves the named slots and the review handoffs.

## Runtime scope

The recipes use the catalog's `image-gen` and `video-gen` capability tags. A compatible executor must select a provider that supports the actual inputs, including multiple image references for the story sheet. The review sequence specifies manual checks for the creator. It does not perform visual verification, enforce approval, or certify provider support. Hosted Canvas Play is tracked in [SBAI-7654](https://biloxistudios.atlassian.net/browse/SBAI-7654).
