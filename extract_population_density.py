from rasterio.mask import mask
import numpy as np


def extract_population_density(tiff_file, shapefile, country_column, country):
    """
    Extract population density data for a specific country from a raster file.

    This function masks and crops a raster dataset (e.g., GeoTIFF) to the
    boundaries of a given country defined in a shapefile. It returns the
    population density values along with the dimensions of the cropped raster.

    Parameters
    ----------
    tiff_file : rasterio.io.DatasetReader
        An open raster dataset containing population density data.
    shapefile : geopandas.GeoDataFrame
        A GeoDataFrame containing country boundaries.
    country_column : str
        The name of the column in the shapefile that identifies countries
        (e.g., 'NAM_0').
    country : str
        The name of the country to extract.

    Returns
    -------
    population_density : numpy.ndarray
        A 2D array of population density values for the specified country,
        with nodata values replaced by 0.
    out_image : numpy.ndarray
        The cropped raster data as a NumPy array (all bands).
    out_transform : affine.Affine
        The affine transformation matrix for the cropped raster, mapping
        pixel coordinates to geographic coordinates.
        
    Notes
    -----
    - Assumes that the raster contains population density data in its first band.
    - Any nodata values in the raster are set to 0 in the output array.
    - The function relies on rasterio.mask.mask for cropping the raster.
    """

    # Extract country shape from shapefile
    country_shape = shapefile[shapefile[country_column] == country] # NAM_0 is the relevant column from the World Bank Official Boundaries file

    # Convert geometry to GeoJSON-like format
    geometries = country_shape.geometry.values

    # Mask (crop raster to country)
    out_image, out_transform = mask(tiff_file, geometries, crop=True)

    population_density = out_image[0]  # Get the first band i.e. the population density

    if tiff_file.nodata is not None:
        #population_density[population_density == tiff_file.nodata] = 0
        #change on April 1, 2026
        population_density = population_density.astype(float)  # ensure NaN can be stored
        population_density[population_density == tiff_file.nodata] = np.nan

    return population_density, out_image, out_transform