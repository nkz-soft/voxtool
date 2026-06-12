# Notebooks

`voice_benchmark_demo.ipynb` is the final demonstration notebook. It uses
`helpers.py` to load the fixture dataset (or `data/generated/v1/` when
present), synthesize deterministic audio, run pipelines A-D with mock
adapters, show parsed JSON envelopes and optional tool execution, and build
the metrics summary and markdown report.

Notebook outputs and generated report artifacts are written under
`runs/notebook/` and must remain outside Git unless a future task explicitly
documents a bounded fixture.
