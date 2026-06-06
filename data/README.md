# Data Artifact Policy

`data/raw/` and `data/processed/` are working directories for generated or
downloaded datasets. Generated datasets, large audio files, and intermediate
evaluation data are excluded from Git. Commit only bounded fixtures required for
tests, along with metadata that explains how generated data can be reproduced.
