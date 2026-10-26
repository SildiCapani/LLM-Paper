# Experiment

Reproducible task selection and prompt generation for the paper.

```
data/                       EffiBench-X metadata (no test data) + selected tasks
tasks/EB01..EB10/           EffiBench-X tasks: task.json, starter/, reference/, runner/,
                            test_generator.py, evaluator.py
tasks/CLBG01..CLBG04/       CLBG tasks: spec.md, task.json, reference/python3.py, expected/
prompts/template_*.txt      prompt templates (included verbatim in the paper appendix)
prompts/languages.json      language-specific placeholder values
prompts/rendered/           42 final prompts (14 tasks x 3 languages) + index.json (SHA-256)
scripts/                    pipeline scripts (run in this order)
measure/                    energy/time/memory measurement (Linux RAPL, macOS powermetrics);
                            see measure/ANLEITUNG.md
```

## Reproduce

```bash
python3 -m venv .venv && .venv/bin/pip install pyarrow huggingface_hub fsspec
.venv/bin/python scripts/fetch_effibench_metadata.py   # ~1.6 MB metadata
.venv/bin/python scripts/fetch_effibench_extras.py
.venv/bin/python scripts/select_tasks.py               # seed 20261025
.venv/bin/python scripts/fetch_selected_tasks.py
python3 scripts/render_prompts.py
```

`fetch_*` scripts may print "terminate called without an active exception" on exit;
this is a known teardown issue of `HfFileSystem` and does not affect the output.

Note: `test_generator.py` and `evaluator.py` are code from the dataset. Run them only
inside the sandboxed containers of the correctness pipeline.
