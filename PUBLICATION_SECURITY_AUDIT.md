# Publication security audit

**Audit date:** 2026-08-05  
**Scope:** Files selected for the GitHub public tree on `docs/public-release-v1`

## Result

`PASS_WITH_DOCUMENTED_PROVENANCE_PATHS`

No credential or private-information blocker was found in the selected public
tree. The original local workspace and all-in-one source directory are excluded
by `.gitignore` and were not treated as Git publication candidates.

## Checks

| Check | Result |
|---|---|
| Concrete Mac user paths with the `/Users/` prefix | 0 hits (the literal prefix appears only in this audit description) |
| High-confidence API key/token/private-key/password patterns | 0 hits |
| Email-address patterns | 0 private addresses; 1 public GitHub noreply address in this audit |
| `sandbox:/mnt/data` and ChatGPT internal `file-...` IDs | 0 hits |
| `.env` files | 0 |
| `.DS_Store` files | 0 |
| Python bytecode and cache directories | 0 |
| Symlinks | 0 |
| Broken symlinks | 0 |

## Documented path provenance

`/mnt/data/paperB-unified-v1` occurs in 127 selected files:

- 120 immutable execution receipts;
- 2 archived original post-run analysis scripts; and
- 5 public documents that explain the provenance path.

The path identifies the original container execution layout. It is not a Mac
user path, credential, API endpoint, or current secret location. The receipts
and archived scripts were not normalized because doing so would alter execution
provenance. Portable public analysis uses separate helper scripts and writes to
`build/`.

## Binary artifacts

PDF and PNG files were copied byte-for-byte from the source package. The
English and Japanese manuscript DOCX files received Availability-only text
updates documented in `docs/DOCX_REGENERATION.md`; the supplementary DOCX was
preserved byte-for-byte. The source package's own packaging report recorded
zero credential/private-key pattern hits, zero caches, zero `.env` files, and
zero `.DS_Store` files.

## Git commit identity

The pre-existing global Git configuration contained a personal Gmail address.
It was not used for this repository. Repository-local identity was set to the
public GitHub handle `Louis-Takeuchi` and GitHub noreply address
`266043071+Louis-Takeuchi@users.noreply.github.com` before commits were made.

## Publication decision

The secret scan does not require a STOP. Licenses and the minimum citation
record are finalized. Remaining author and article metadata listed in
`PUBLICATION_OPEN_FIELDS.md` does not block the public reproducibility release.
