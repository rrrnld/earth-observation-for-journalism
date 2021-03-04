# Overview

As mentioned before, the Sentinel-2 satellites capture data far outside the range of visible light. With wavelengths of up to 2100nm, some bands go far into the infra-red spectrum.
The higher parts of the spectrum are especially useful to calculate _Spectral Indices_ or _Indicators_.

These indicators can be used for a range of different tasks. The Normalised Difference in Water Index (NDWI) for example provides a value containing information about how likely a pixel represents water. The Bare-Soil Index (BSI) gives an estimate about how likely a pixel represents unvegetaed soil. Other indices give an indication about vegetation health or plant activity. Methodolically these indices transfer knowledge about the reflective properties of different material in specific wavelengths and convert them into mathematical formulas that allow drawing conclusions on surface phenomena.

This chapter explores how to calculate these indices over long and short time spans, leveraging the high spatial resolution to provide highly localized information.

It ends with a notebook that implements several indices and can be used to calculate them for any product offered by the Copernicus Open Access Hub with only minimal modifications.
