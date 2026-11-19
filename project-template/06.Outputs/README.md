# Using the outputs

This folder gathers the deliverables created or updated in the project. It is the default destination for any version derived from a base file in `05.Working_Files`.

The folder can stay with only this `README.md` while there is no deliverable yet.

## Versioning

The rule is in the global `CLAUDE.md`, section "Versioning of outputs", and the procedure in the skill `versions-and-folders`. In short:

- do not overwrite an output already delivered, generate a new version;
- name it `material_name_vX.Y.ext`, starting at `v1.1`. A small change bumps the second digit (`v1.2`), a large change bumps the first and resets the second (`v2.1`);
- a material with a new purpose, which coexists with the previous one, gets a new base name and starts again at `v1.1`;
- do not use suffixes such as `final`, `revised`, `ok` or initials;
- when the same analysis comes out in more than one format, keep the number synchronized between them, even if one of the formats did not change. Mismatched numbering forces you to explain which version each file corresponds to every time one of them is cited.

If the user asks to overwrite, reread the file first: they may have edited it between turns.

## What this folder never is

It is not a factual source for a new task without confirming that the output is still current. A deliverable reflects the data as of the date it was made, not the current materials in `04.Materials_and_Sources`.

Superseded versions go to the `old/` subfolder of the folder where the material is, and are not deleted. When the root piles up too many materials, each material can get its own subfolder, with its own `old/`, once the user approves. `99.Archive` receives only material that has gone out of circulation entirely.
