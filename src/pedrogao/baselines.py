"""Spectral-index baselines for burnt-area mapping.

The Normalized Burn Ratio contrasts near-infrared (high over healthy vegetation) with
short-wave infrared (high over burnt ground). On Sentinel-2 that is B8 (10 m) and B12 (20 m):

    NBR  = (B8 - B12) / (B8 + B12)
    dNBR = NBR_pre - NBR_post        (high = more severe burning)

Inputs are surface reflectance. For the L2A products in data/raw/sentinel2 (processing
baseline 05.00), reflectance = (DN - 1000) / 10000; see data/README.md. Resample B12 to
10 m (or B8 to 20 m) before combining them.
"""
import numpy as np


def nbr(nir: np.ndarray, swir2: np.ndarray, eps: float = 1e-6) -> np.ndarray:
    """Normalized Burn Ratio from NIR (B8) and SWIR-2 (B12) reflectance."""
    nir = nir.astype("float32")
    swir2 = swir2.astype("float32")
    return (nir - swir2) / (nir + swir2 + eps)


def dnbr(nbr_pre: np.ndarray, nbr_post: np.ndarray) -> np.ndarray:
    """Differenced NBR: pre-fire NBR minus post-fire NBR."""
    return nbr_pre - nbr_post
