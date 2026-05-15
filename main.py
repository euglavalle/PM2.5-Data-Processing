##### Library required to handle directory definitions ############
import os
###################################################################

##### Data processing libraries ###################################
import numpy as np
import pandas as pd
###################################################################

##### Geospatial data processing libraries ########################
import geopandas as gpd                 # required for processing shapefiles
import rasterio                         # required for processing .tiff files
from rasterio.enums import Resampling   # required for resampling .tiff files to given grid resolution
import rioxarray as rxr                 # used for exception handling
import xarray as xr                     # required for processing NetCDF files
###################################################################

##### Self-defined functions to ease code readability #############
from extract_population_density import extract_population_density
from raster_to_edges import raster_to_edges
from spherical_patch_area import spherical_patch_area
###################################################################

# 1. Set NetCDF and .TIFF file path, read country shapefile
countries = gpd.read_file(r"C:\Users\elavalle\Documents\Spatial Data Processing\World Bank Official Boundaries - Admin 0_all_layers.zip")

tiff_file_path = r"C:\Users\elavalle\Documents\Spatial Data Processing\Global_2000_PopulationDensity30sec_GPWv4.tiff"

netcdf_folder_path = r"C:\Users\elavalle\Documents\Spatial Data Processing\PM2.5\resolution0p010\V5.GL.06\year2000"
output_folder_path = r"C:\Users\elavalle\Documents\Spatial Data Processing\PM2.5\resolution0p010\V5.GL.06\results_year_2000.csv"

results = [] # list where PM2.5 pixel-level means and population-weighted concentration results will be stored

# 2. Initialize loop over NetCDF files and extract PM2.5 values
for file in os.listdir(netcdf_folder_path):
    if file.endswith(".nc"):

        year = file.split("-")[0][-6:-2]
        xrds = xr.open_dataset(os.path.join(netcdf_folder_path, file))
        print(f"Processing file {file}; year is {year}")

        pm25 = xrds["GWRPM25"] #V5GL06 variable name
        #pm25 = xrds["PM25"] #V6GL0204 variable name
        pm25 = pm25.rio.set_spatial_dims(x_dim="lon", y_dim="lat")
        pm25 = pm25.rio.write_crs("EPSG:4326")

        for country in np.sort(countries["NAM_0"].unique()):
            country_shape = countries[countries["NAM_0"] == country] # Extract country geometries from shapefile
            print(f'Processing {country}')

            # 3. Limit NetCDF and .TIFF file to one country at a time and
            # extract population density raster for country. Resample raster to NetCDF resolution
            minx, miny, maxx, maxy = country_shape.total_bounds
            pm25_subset = pm25.sel(lon=slice(minx, maxx), lat=slice(miny, maxy))
            # the next two lines had to be added because of MissingSpatialDimensionError error appearing
            # when processing NetCDF version V6GL02.04
            pm25_subset = pm25_subset.rio.set_spatial_dims(x_dim="lon", y_dim="lat")
            pm25_subset = pm25_subset.rio.write_crs("EPSG:4326")

            try:
                pm25_clipped = pm25_subset.rio.clip(country_shape.geometry, country_shape.crs, all_touched=True)

            except rxr.exceptions.NoDataInBounds:
                print(f"No PM2.5 data overlaps for {country}")
                #pm25_clipped = None
                centroid = country_shape.geometry.to_crs("EPSG:3857").centroid.to_crs("EPSG:4326").iloc[0] # centroid computation requires distance measurement, therefore EPSG 3857 reprojection
                # Use a small buffer around the centroid to preserve spatial dimensions
                delta = 0.005 
                pm25_clipped = pm25.sel(
                    lon=slice(centroid.x - delta, centroid.x + delta),
                    lat=slice(centroid.y - delta, centroid.y + delta)
                )
                # Set spatial dims and CRS as done for pm25_subset
                pm25_clipped = pm25_clipped.rio.set_spatial_dims(x_dim="lon", y_dim="lat")
                pm25_clipped = pm25_clipped.rio.write_crs("EPSG:4326")

            with rasterio.open(tiff_file_path) as src:
                population_density, out_image, out_transform = extract_population_density(src, countries, "NAM_0", country)

            # resample population_density raster to match PM2.5 grid
            height, width = population_density.shape
            res = out_transform.a  # pixel width in degrees

            population_density_lons = out_transform.c + res * (np.arange(width) + 0.5) # out_transform.c: left edge (min longitude)
            population_density_lats = out_transform.f + out_transform.e * (np.arange(height) + 0.5) # out_transform.f: top edge (max latitude), out_transform.e: pixel height

            pop_da = xr.DataArray(
                population_density,
                dims=["y", "x"],
                coords={"y": population_density_lats, "x": population_density_lons}
            )
            pop_da = pop_da.rio.write_crs("EPSG:4326")
            pop_da = pop_da.rio.set_spatial_dims(x_dim="x", y_dim="y")

            try:
                if country != 'United States of America':
                    pop_regridded = pop_da.rio.reproject_match(
                        pm25_clipped,
                        resampling=Resampling.nearest # needed because of low values in island states
                        #resampling=Resampling.bilinear # memory issues with Resampling.nearest when processing US
                    )
                else:
                    pop_regridded = pop_da.rio.reproject_match(
                        pm25_clipped,
                        #resampling=Resampling.nearest # needed because of low values in island states
                        resampling=Resampling.bilinear # memory issues with Resampling.nearest when processing US
                    )

            except rxr.exceptions.NoDataInBounds:
                print(f"Reproject_match failed for {country}. Setting clipped country area to None.")
                pm25_clipped = None

            if pm25_clipped is not None:

                new_transform = pop_regridded.rio.transform()

                # Compute raster edges for area calculation in step 5
                pop_regridded_lon_edges, pop_regridded_lat_edges = raster_to_edges(pop_regridded, new_transform, raster_from_resampling=True)

                # 4. Calculate simple mean of PM2.5 concentration
                #pm25_clipped = pm25_clipped.where(pm25_clipped >= 0) #V6GL0204 contains the negative value -999 as placeholder
                pm25_simple_mean = pm25_clipped.mean().item()
                #print(pm25_simple_mean)

                # 5. For each cell of country, calculate population and multiply this by PM2.5 concentration of that cell
                # Compute per-pixel area
                authalic_radius = 6371007.180918
                area_m2 = spherical_patch_area(authalic_radius, pop_regridded_lon_edges, pop_regridded_lat_edges)
                area_km2 = area_m2 / 1e6

                # For each country cell, compute population count
                population_per_pixel = np.where(np.isnan(pop_regridded), 0, pop_regridded * area_km2) #if NaN replace with 0
                total_population = np.sum(population_per_pixel)

                if total_population == 0:
                    population_weighted_pm25 = np.nan

                else:
                    population_per_pixel_share = population_per_pixel / total_population
                    population_weighted_pm25 = np.nansum(pm25_clipped * population_per_pixel_share) #with np.nansum, NaN treated as 0
                    #print(population_weighted_pm25)
            else:
                pm25_simple_mean = np.nan
                population_weighted_pm25 = np.nan

            results.append({
                "year": year,
                "country": country,
                "pm25_simple_mean_v5gl06": pm25_simple_mean,
                "pop_weighted_mean_v5gl06": population_weighted_pm25
            })

        xrds.close()

# 7. Store results in .csv
batch_csv = os.path.join(netcdf_folder_path, f"results_year_{results[0]['year']}.csv")
pd.DataFrame(results).to_csv(batch_csv, index=False)
print(f"Processing finished and results saved to {batch_csv}")

df = pd.read_csv(batch_csv)

# Group by year and country, compute mean of PM2.5 columns
df_yearly = df.groupby(["year", "country"], as_index=False).agg({
    "pm25_simple_mean_v5gl06": "mean",
    "pop_weighted_mean_v5gl06": "mean"
})
print(df_yearly)

df_yearly.to_csv(output_folder_path, sep=';', index=False)
print("Processing completed.")