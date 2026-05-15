import numpy as np

def spherical_patch_area(
    R: float, # Authalic radius, in meters
    lon_edges: list[float], # longitude edges, in degrees
    lat_edges: list[float] # latitude edges, in degrees
) -> list[list[float]]:
    """
    Source: https://www.analyze.earth/posts/on-areas-on-earth/
    """
    # Convert from degrees to radians
    lon_min = np.array(lon_edges[:-1]) * (np.pi / 180)
    lon_max = np.array(lon_edges[1:]) * (np.pi / 180)
    lat_min = np.array(lat_edges[:-1]) * (np.pi / 180)
    lat_max = np.array(lat_edges[1:]) * (np.pi / 180)
    h = np.reshape(
        R * (np.sin(lat_max) - np.sin(lat_min)),
        shape=(-1, 1)
    )
    w = np.reshape(
        R * (lon_max - lon_min),
        shape=(-1, 1)
    )
    area_patch = np.abs((w @ h.T).T)  # matrix multiplication (@ is * for matrices)
    return area_patch