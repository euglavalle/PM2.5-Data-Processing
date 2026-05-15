import numpy as np

def raster_to_edges(raster, transformation_matrix, raster_from_resampling=False):
    """
    Compute longitude and latitude edge coordinates from a raster and its transform.

    This function derives the geographic coordinates of pixel edges based on the
    raster's shape and its affine transformation matrix.

    Parameters
    ----------
    raster : numpy.ndarray
        A 3D NumPy array representing the raster data with shape
        (bands, height, width).
    transformation_matrix : affine.Affine
        The affine transformation associated with the raster, mapping pixel
        coordinates to geographic coordinates.

    Returns
    -------
    lon_edges : numpy.ndarray
        A 1D array of longitude values representing the vertical pixel edges
        (length = width + 1).
    lat_edges : numpy.ndarray
        A 1D array of latitude values representing the horizontal pixel edges
        (length = height + 1).

    Notes
    -----
    - The affine transform is assumed to follow the standard rasterio convention:
      (a, b, c, d, e, f), where:
        * a: pixel width (x resolution)
        * e: pixel height (y resolution, typically negative)
        * c: x-coordinate of the upper-left corner
        * f: y-coordinate of the upper-left corner
    - Latitude edges are typically decreasing if the pixel height (e) is negative.
    """
    # Extract pixel size and edges from raster
    if raster_from_resampling == False:
        height = raster.shape[1]
        width = raster.shape[2]
    else:
        height = raster.shape[0]
        width = raster.shape[1]

    # Pixel size
    dx = transformation_matrix.a # pixel width (longitude step)
    dy = transformation_matrix.e # pixel height (latitude step, negative)
    x0 = transformation_matrix.c # left edge (min longitude)
    y0 = transformation_matrix.f # top edge (max latitude)

    lon_edges = x0 + np.arange(width + 1) * dx
    lat_edges = y0 + np.arange(height + 1) * dy

    return lon_edges, lat_edges