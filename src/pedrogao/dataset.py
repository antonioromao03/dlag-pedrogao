"""Dataset construction: read the prepared rasters in data/processed, tile them, normalise
the bands and split into train/validation/test.

Splits must be spatial (whole fires or blocks of tiles), not random pixels or tiles, because
neighbouring pixels are strongly correlated. The Pedrógão Grande fire is the test case and
must not reach training (see data/README.md for the benchmark's `coral` fold).
"""
