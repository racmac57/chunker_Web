# Chunking_Master_Prompt (Final – Drop-In)

**Context:**
You have one or more raw chat transcripts that must be cleanly segmented, documented, indexed, and archived for long-term retrieval.

**Trigger:**
If the user says **“proceed”** or requests combination/processing of logs, run the entire pipeline below automatically.

---

## 0) Pre-Processing

* Normalize source (PDF, HTML share link, pasted text) into plain text.
* Standardize speaker labels (`User:` / `Assistant:`).
* Remove navigation/UI debris (e.g., “Load More”, “Show More”, reaction icons).
* Preserve original order.

## 1) Chunking

* Split into natural conversational segments of **≤300 lines**.
* End chunks only at **speaker turn boundaries**.
* Chunk headers: `## Chunk {NN}: {Short Topic Label}`.

## 2) Cleaning

* Remove duplicate lines; normalize whitespace.
* Preserve logical order and all code in place.
* Ensure code fences are **closed** and language tags remain intact.

## 3) Code Processing

* Detect all code blocks; assign IDs `CODE_YYYYMMDD_###`.
* Insert a one-line header above each block describing purpose.
* Merge multi-part code sent across consecutive turns into a single block where appropriate.
* Track revisions with suffixes (`…_v2`, `…_v3`) when the same code is modified later.
* Apply status tags: `[FINAL]`, `[DRAFT]`, `[FIXED]` when evident.

## 4) Per-Chunk Outputs

* **Cleaned transcript** (`.txt`)
* **2–3 sentence summary** (`.md`) including **≥3 keywords** for search
* **Transformation scripts** (`.py` and/or `.m`) if applicable
* **Metadata** (`.json`) with:

  * `timestampRange: [startISO, endISO]`
  * `primaryTopics: 2–3 themes`
  * `participants: [list]`
  * `codeIndex: [CODE IDs]`
  * `checksum: SHA256 of cleaned text`

## 5) Consolidation & QC

* **CombinedSummary.md**: concatenate all chunk summaries in chronological order (split into sequential parts if >5,000 words).
* **Searchable Index**:

  * All CODE IDs with short descriptions
  * Topic → chunk mapping
  * **Global keyword index** mapping terms → `{chunkId, lineRange}`
  * **Conversation map**: ordered chunk list with brief topic labels
* **CombinedTranscript.md** (new):

  * Produce a **single Markdown file** that **combines all cleaned chunks** in order.
  * Structure:

    * Title and date range
    * **Table of Contents** with anchors to each chunk and each CODE ID
    * For each chunk:

      * `## Chunk {NN}: {Short Topic Label}`
      * Inline cleaned text for that chunk
      * Per-chunk mini-index (topics, CODE IDs, timestamps)
  * Include anchor links like `#chunk-01`, `#code-YYYYMMDD-001` and cross-references.
  * If the file exceeds platform limits, split into `CombinedTranscript_Part1.md`, `Part2.md`, etc., and generate a small `CombinedTranscript_TOC.md` linking all parts.

## 6) Archive Index

* Create `archive_index.json` with:

  * `fileCount` by type
  * `globalTimestampRange`
  * `topicTags` for retrieval
  * `allCodeIds` with `{file, lineHint, status}`

## 7) Packaging

* Deliver a `.zip` containing:

  * All cleaned transcripts (`.txt`)
  * All summaries (`.md`)
  * All scripts (`.py`, `.m`) generated
  * All per-chunk metadata (`.json`)
  * `CombinedSummary.md`
  * **CombinedTranscript.md** (or split parts + TOC)
  * `archive_index.json`
  * **Global checksum** file `archive_SHA256.txt`
  * **README.md** describing structure, filenames, and how to locate code, topics, and chunks

---

If you want, I can also provide a minimal **naming convention** block to lock in predictable filenames (e.g., `Chunk_01.txt`, `Chunk_01.md`, `Chunk_01.meta.json`, etc.).
