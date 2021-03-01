# Overview

The parts of the Sentinel-2 data that extend the visible spectrum can be used to calculate _Spectral Indices_ or _Spectral Indicators_.

These indicators can be used for a range of different tasks. The Normalised Difference in Water Index (NDWI) for example gives information about how likely a pixel represents water, the Bare-Soil Index (BSI) gives an estimate about how likely a pixel represents unvegetaed soil. Other indices give an indication about vegetation health or plant activity using reflectance properties of the ground in different spectra of light.

This chapter explores how to calculate these indices over long and short time spans, leveraging the high spatial resolution to provide highly localized information using these indices.

It ends with a notebook that implements the BSI, the NDWI, the Normalized Difference In Vegetation Index (NDVI) and the Normalized Burn Ratio (NBR) which can be used to determine burn severity after a fire. The implementation is extensible enough to perform many different kinds of index calculations on downloaded products with only minimal changes.
