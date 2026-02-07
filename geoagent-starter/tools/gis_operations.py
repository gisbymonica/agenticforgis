import os
import geopandas as gpd
from langchain.tools import tool
from shapely.validation import make_valid
from shapely.geometry import Polygon, MultiPolygon
os.environ["OGR_GEOMETRY_ACCEPT_UNCLOSED_RING"] = "NO"
@tool
def get_layer_metadata(file_path: str) -> str:
    """Returns the CRS, bounds, and columns of a GIS file. 
    Use this first to understand any dataset."""
    try:
        gdf = gpd.read_file(file_path, engine="pyogrio")
        return f"CRS: {gdf.crs} | Columns: {list(gdf.columns)} | Geometry: {gdf.geom_type.unique()}"
    except Exception as e:
        return f"Error reading file: {e}"
@tool
def reproject(source_path: str, tgt_crs: str = "EPSG:4326"):
    """Reprojects a layer to a target CRS."""
    print(f"Agent Action: Loaded {source_path} for reprojection.")
    src = gpd.read_file(source_path)
    
    if src.crs != tgt_crs:
        print(f"Agent Action: Re-projecting {source_path} from {src.crs} to {tgt_crs}")
        src = src.to_crs(tgt_crs)
    output_path = source_path.replace(".geojson", "_fixed.geojson")
    src.to_file(output_path, driver="GeoJSON", engine="pyogrio")

@tool
def repair_and_join(source_path: str, target_path:str):
    """Joins two layers. If CRS mismatch is detected, it auto-aligns to the target."""
    src = gpd.read_file(source_path)
    tgt = gpd.read_file(target_path)
    
    if src.crs != tgt.crs:
        print(f"Agent Action: Re-projecting {source_path} from {src.crs} to {tgt.crs}")
        src = src.to_crs(tgt.crs)
    output_path = source_path.replace(".geojson", "_joined.geojson")
    src.to_file(output_path, driver="GeoJSON", engine="pyogrio")
    joined = gpd.sjoin(src, tgt, how="inner", predicate="intersects")
    return f"Join successful. Resulting rows: {len(joined)}"

def close_ring(geom):
    """Force-closes a Polygon ring if the start and end points don't match."""
    if isinstance(geom, Polygon):
        if not geom.exterior.is_ring:
            coords = list(geom.exterior.coords)
            # Add the first point to the end to close it
            return Polygon(coords + [coords[0]])
    elif isinstance(geom, MultiPolygon):
        return MultiPolygon([close_ring(p) for p in geom.geoms])
    return geom

@tool
def repair(file_path: str, target_crs: str = "EPSG:4326"):
    """
    Repairs topological errors and re-projects to a target CRS.
    Use this when metadata indicates invalidity or a CRS mismatch.
    """
    print(f"Agent Action: Loaded {file_path} for repair and re-projection.")
    try:
        # 1. Read using pyogrio for speed
        gdf = gpd.read_file(file_path, engine="pyogrio")
        print(f"Agent Action: Loaded {file_path} with CRS {gdf.crs}")
        
        # 2. Topology Repair
        # .make_valid() handles self-intersections and unclosed rings
        invalid_mask = ~gdf.geometry.is_valid
        if invalid_mask.any():
            gdf.geometry = gdf.geometry.make_valid()  # Fix self-intersections
            # gdf.geometry = gdf.geometry.apply(close_ring)  # Ensure rings are closed
            print(f"Agent Action: Repaired {invalid_mask.sum()} invalid geometries.")
            repair_note = f"Repaired {invalid_mask.sum()} invalid geometries. "
        else:
            repair_note = "Geometry was already valid. "

        # 3. CRS Check & Repair
        current_crs = str(gdf.crs)
        if current_crs != target_crs:
            gdf = gdf.to_crs(target_crs)
            crs_note = f"Re-projected from {current_crs} to {target_crs}."
        else:
            crs_note = f"CRS already matches {target_crs}."

        # Save the result
        output_path = file_path.replace(".geojson", "_fixed.geojson")
        gdf.to_file(output_path, driver="GeoJSON", engine="pyogrio")
        
        return f"{repair_note}{crs_note} Saved to: {output_path}"
    except Exception as e:
        return f"Error during processing: {str(e)}"