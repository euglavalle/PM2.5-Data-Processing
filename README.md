# PM2.5-Data-Processing
The Python script *main.py* is used to calculate particulate matter (PM) concentrations and population-weighted PM concentration for each country around the globe on a 0.01*0.01 degree grid. We use the following data sources:

- PM2.5 data is provided on https://www.satpm.org/data-access and based on [[1]](#1) and [[2]](#2)
- Country shapefiles retrieved from https://datacatalog.worldbank.org/infrastructure-data/search/dataset/0038272/world-bank-official-boundaries
- Population densities retrieved from https://pacific-data.sprep.org/dataset/gridded-population-world-v4 [[3]](#3)

The other scripts provided, which are called in *main.py*, do the following:

- *extract_population_density.py*: extract population density data for a specific country from the raster file (.tiff) provided by [[3]](#3)
- *raster_to_edges.py*: compute longitude and latitude edge coordinates from a raster and its transform
- *spherical_patch_area.py*: compute are of each pixel on spherical surface

## References
<a id="1">[1]</a> 
Aaron van Donkelaar, Melanie S. Hammer, Liam Bindle, Michael Brauer, Jeffery R. Brook, Michael J. Garay, N. Christina Hsu, Olga V. Kalashnikova, Ralph A. Kahn, Colin Lee, Robert C. Levy, Alexei Lyapustin, Andrew M. Sayer and Randall V. Martin (2021). Monthly Global Estimates of Fine Particulate Matter and Their Uncertainty Environmental Science & Technology, 2021, doi:10.1021/acs.est.1c05309. 

<a id="2">[2]</a>
Hammer, M. S., van Donkelaar, A., Bindle, L., Sayer, A. M., Lee, J., Hsu, N. C., Levy, R.C., Sawyer, V., Garay, M. J., Kalashnikova, O. V., Kahn, R. A., Lyapustin, A., and Martin, R. V.: Assessment of the impact of discontinuity in satellite instruments and retrievals on global PM2.5 estimates. Remote Sensing of Environment, Volume 294, 2023, 113624, ISSN 0034-4257, https://doi.org/10.1016/j.rse.2023.113624.

<a id="3">[3]</a>
Center for International Earth Science Information Network - CIESIN - Columbia University. 2018. Gridded Population of the World, Version 4 (GPWv4): Population Density, Revision 11. Palisades, NY: NASA Socioeconomic Data and Applications Center (SEDAC). https://doi.org/10.7927/H49C6VHW. Accessed DAY MONTH YEAR.
