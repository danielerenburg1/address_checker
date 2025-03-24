from typing import List, Dict, Optional, Tuple, Union
from dataclasses import dataclass

@dataclass
class Coordinate:
    lat: float
    lng: float

@dataclass
class Neighborhood:
    name: str
    coordinates: List[Coordinate]

def is_point_in_polygon(point: Coordinate, polygon: List[Coordinate]) -> bool:
    """
    Check if a point lies inside a polygon using ray casting algorithm.
    
    Args:
        point: The coordinate point to check
        polygon: List of coordinates forming the polygon
        
    Returns:
        bool: True if point is inside polygon, False otherwise
    """
    if len(polygon) < 3:
        return False
    
    inside = False
    j = len(polygon) - 1
    
    for i in range(len(polygon)):
        xi = polygon[i].lng
        yi = polygon[i].lat
        xj = polygon[j].lng
        yj = polygon[j].lat
        
        intersect = ((yi > point.lat) != (yj > point.lat)) and \
                   (point.lng < (xj - xi) * (point.lat - yi) / (yj - yi) + xi)
        
        if intersect:
            inside = not inside
        j = i
    
    return inside

def find_neighborhood(point: Coordinate, neighborhoods: List[Neighborhood]) -> Optional[str]:
    """
    Find which neighborhood contains the given point.
    
    Args:
        point: The coordinate point to check
        neighborhoods: List of neighborhoods (polygons with names)
        
    Returns:
        str or None: Name of the neighborhood containing the point, or None if not found
    """
    for neighborhood in neighborhoods:
        if is_point_in_polygon(point, neighborhood.coordinates):
            return neighborhood.name
    return None

    # Alternative version to find all matching neighborhoods
    def find_all_neighborhoods(point: Coordinate, neighborhoods: List[Neighborhood]) -> List[str]:
        """
        Find all neighborhoods that contain the given point (useful for overlapping areas).
        """
        return [
            neighborhood.name 
            for neighborhood in neighborhoods 
            if is_point_in_polygon(point, neighborhood.coordinates)
        ]
