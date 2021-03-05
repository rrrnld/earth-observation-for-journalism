# Overview

As mentioned before, the Sentinel-2 satellites capture data far outside the range of visible light. With wavelengths of up to 2100nm, some bands go far into the infra-red spectrum.
The invisible parts of the spectrum are especially useful to calculate _Spectral Indices_ or _Indicators_.

These indicators can be used for a range of different tasks. The Normalized Difference in Water Index (NDWI) for example provides a value containing information about how likely a pixel represents water. The Bare-Soil Index (BSI) gives an estimate about how likely a pixel represents soil that is not covered by vegetation. Other indices give an indication about vegetation health or plant activity. The method these indices rely on is the transfer knowledge about the different reflective properties of material in specific wavelengths into mathematical formulas that allow drawing conclusions about surface phenomena.

This chapter explores how to calculate these indices over long and short time spans, leveraging the high spatial resolution to provide highly localized information.

It ends with a notebook that implements several indices and can be used to calculate them for any product offered by the Copernicus Open Access Hub with only minimal modifications.

It is important to note that these explorations cannot substitute the work of experienced scientists performing earth observation tasks.
They are rather to be seen as part of a process that aims to understand in how far these data sources have merit for a data journalism process, which is a process that heavily relies on gathering information from external sources.
That being said, the following sections aim to understand in how far a data source that positions itself as openly can be a part of this process and provide useful insights.
