# DOCX publication synchronization and render audit

Audit date: 2026-08-05 (Asia/Tokyo)

## Scope

The public repository URL and data-availability wording were synchronized in
the following publication files:

- `manuscript/PaperB_AdaptiveBehavior_manuscript_v0_1.docx`
- `../PaperB_日本語版_自然表現改訂稿_v0_4.docx`

The English DOCX changed in exactly two paragraphs: Code Availability and Data
Availability. The Japanese DOCX changed in exactly one paragraph under
`研究データ・コード・申告事項`. The package member set was preserved and, in
each edited DOCX, `word/document.xml` was the only ZIP member whose bytes
changed. Scientific claims, values, tables, figures, equations, citations, and
other prose were not edited.

`supplement/PaperB_AdaptiveBehavior_Supplementary_Materials_v0_1.docx` did not
contain an Availability section and was retained byte-for-byte.

## Render verification

The three DOCX files were opened in Apple Pages and exported to PDF without
saving over the source DOCX files. Every rendered page was inspected:

| Document | Pages | Result |
|---|---:|---|
| English manuscript | 32 | Pass |
| Japanese manuscript | 20 | Pass |
| Supplementary materials | 7 | Pass |

No clipped or overlapping text, missing pages, displaced tables or figures,
or broken headings were found. The full repository URL and the synchronized
availability statements were visible in both manuscripts. The supplement
rendered without change.

The bundled LibreOffice-based renderer could not be used because LibreOffice
and its Python rendering dependency were not installed in this environment.
Pages PDF export plus PDFKit page rendering was therefore used for visual QA.

## Known limitation

The released figure-generation source is unavailable. Existing released
figure files were not regenerated or modified. Before journal submission,
unresolved author metadata and journal-template requirements should be checked
without altering frozen scientific content.
