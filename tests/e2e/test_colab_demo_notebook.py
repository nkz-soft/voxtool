from __future__ import annotations

import json
from pathlib import Path

NOTEBOOK = Path("apps/notebook/colab_demo.ipynb")


def _sources() -> list[str]:
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    return ["".join(cell.get("source", [])) for cell in notebook["cells"]]


def test_notebook_is_valid_nbformat() -> None:
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))

    assert notebook["nbformat"] == 4
    assert isinstance(notebook["cells"], list) and notebook["cells"]


def test_notebook_documents_required_demo_steps() -> None:
    text = "\n".join(_sources()).lower()

    # Dependency install, repo load, adapter selection, text run, optional audio,
    # validation, execution, final answer, and metrics must all be present.
    assert "pip install" in text
    assert "git clone" in text
    assert "select_adapter" in text
    assert "run_text_demo" in text
    assert "files.upload" in text
    assert "validation" in text
    assert "final_answer" in text or "final answer" in text
    assert "metric" in text


def test_notebook_does_not_eagerly_download_real_model() -> None:
    text = "\n".join(_sources())

    # The default adapter must be the no-download mock so opening the notebook
    # never triggers a real model download before the user opts in.
    assert 'ADAPTER_ID = "mock"' in text
    # The notebook must not call from_pretrained directly; downloads happen
    # lazily inside the adapter implementations.
    assert "from_pretrained" not in text
