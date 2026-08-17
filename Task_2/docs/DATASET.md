# Dataset and indexing

The production source is `ai4bharat/MSMARCO-XI`. It is not fetched at API startup. `download_dataset` writes a bounded raw JSONL artifact and a small source manifest; `inspect_dataset` prints observed fields; `normalize` accepts common query/answer/passage field variations, normalizes whitespace, preserves Unicode, deduplicates passage content through stable SHA-256 IDs, and retains language metadata.

The explicit pipeline is:

```text
download -> inspect -> normalize -> chunk -> embed -> build_index
```

`build_index` persists chunks, vectors, and an `index_manifest` containing dataset, model, strategy, timestamp, document/chunk counts, languages, and index version. Raw, processed, and index artifacts remain untracked because they can be large and may be regenerated. Dataset configuration and split should be recorded alongside an experiment or released index artifact.

Language fields are not translated by default. Retrieval first filters to the detected/declared language when it has matching documents, with `cross_language=true` opting into broad retrieval.
