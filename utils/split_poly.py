import geopandas as gpd
from shapely.geometry import box
import math

def split_polygon_into_n(polygon, n=4, mode='grid'):
    """
    Split a polygon into approximately n equal parts using a rectangular grid.
    
    Parameters:
    -----------
    polygon : shapely.geometry.Polygon
        The polygon to split (in any CRS, but typically EPSG:4326).
    n : int
        Desired number of parts (the function may return a bit more or less,
        depending on the shape and grid alignment).
    mode : str, optional
        'grid' : keep full squares that intersect the polygon (simple polygons).
        'clip' : clip each square to the polygon boundary (exact parts).
    
    Returns:
    --------
    gpd.GeoDataFrame
        A GeoDataFrame with the parts (geometry) and an 'id' column.
    """
    
    # Get the bounding box
    minx, miny, maxx, maxy = polygon.bounds
    
    # Decide the number of columns and rows.
    # We want n ≈ cols * rows. Use square root to keep cells roughly square.
    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)
    
    # Compute grid step sizes
    step_x = (maxx - minx) / cols
    step_y = (maxy - miny) / rows
    
    # Generate grid cells
    cells = []
    for i in range(cols):
        for j in range(rows):
            x0 = minx + i * step_x
            y0 = miny + j * step_y
            x1 = x0 + step_x
            y1 = y0 + step_y
            cell = box(x0, y0, x1, y1)
            
            # Check intersection
            if cell.intersects(polygon):
                if mode == 'clip':
                    # Clip the cell to the polygon
                    clipped = cell.intersection(polygon)
                    if not clipped.is_empty:
                        # intersection may be MultiPolygon; we can split
                        if clipped.geom_type == 'Polygon':
                            cells.append(clipped)
                        elif clipped.geom_type == 'MultiPolygon':
                            cells.extend([p for p in clipped.geoms])
                else:  # 'grid' mode
                    cells.append(cell)
    
    # Create a GeoDataFrame
    gdf = gpd.GeoDataFrame({'geometry': cells}, crs=polygon.crs if hasattr(polygon, 'crs') else None)
    gdf['id'] = range(len(gdf))
    return gdf