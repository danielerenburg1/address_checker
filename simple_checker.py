import os
from dotenv import load_dotenv
import googlemaps
from shapely.geometry import Polygon, Point
import folium
import json
from pathlib import Path

# Load environment variables
load_dotenv()

def create_neighborhood():
    """Create and save a new neighborhood"""
    # Get neighborhood name
    name = input("Enter neighborhood name: ").strip()
    
    print(f"\nEnter coordinates for {name} (lat,lng format). Enter 'done' when finished:")
    print("Example: 32.0853,34.7818")
    
    polygon_coords = []
    while True:
        user_input = input("Enter coordinate (lat,lng) or 'done': ")
        if user_input.lower() == 'done':
            if len(polygon_coords) < 3:
                print("A neighborhood needs at least 3 points!")
                continue
            break
        
        try:
            lat, lng = map(float, user_input.split(','))
            polygon_coords.append([lat, lng])
        except ValueError:
            print("Invalid format! Please use 'latitude,longitude' format")
            continue

    # Close the polygon
    if polygon_coords[0] != polygon_coords[-1]:
        polygon_coords.append(polygon_coords[0])
    
    # Save to JSON file
    neighborhood_data = {
        "name": name,
        "coordinates": polygon_coords
    }
    
    # Load or create neighborhoods file
    if Path("neighborhoods.json").exists():
        with open("neighborhoods.json", 'r', encoding='utf-8') as f:
            neighborhoods = json.load(f)
    else:
        neighborhoods = {"neighborhoods": []}
    
    # Add new neighborhood
    neighborhoods["neighborhoods"].append(neighborhood_data)
    
    # Save updated data
    with open("neighborhoods.json", 'w', encoding='utf-8') as f:
        json.dump(neighborhoods, f, ensure_ascii=False, indent=2)
    
    print(f"\nNeighborhood '{name}' has been saved!")

def delete_neighborhood():
    """Delete a saved neighborhood"""
    # Check if neighborhoods file exists
    if not Path("neighborhoods.json").exists():
        print("No saved neighborhoods to delete!")
        return
    
    # Load neighborhoods
    with open("neighborhoods.json", 'r', encoding='utf-8') as f:
        neighborhoods = json.load(f)
    
    if not neighborhoods["neighborhoods"]:
        print("No neighborhoods to delete!")
        return
    
    # Show available neighborhoods
    print("\nAvailable neighborhoods:")
    for idx, n in enumerate(neighborhoods["neighborhoods"], 1):
        print(f"{idx}. {n['name']}")
    
    # Get user choice
    while True:
        try:
            choice = input("\nEnter the number of the neighborhood to delete (or 'cancel'): ")
            
            if choice.lower() == 'cancel':
                print("Deletion cancelled.")
                return
            
            idx = int(choice) - 1
            if 0 <= idx < len(neighborhoods["neighborhoods"]):
                # Get neighborhood name before deletion
                deleted_name = neighborhoods["neighborhoods"][idx]["name"]
                
                # Remove the neighborhood
                neighborhoods["neighborhoods"].pop(idx)
                
                # Save updated data
                with open("neighborhoods.json", 'w', encoding='utf-8') as f:
                    json.dump(neighborhoods, f, ensure_ascii=False, indent=2)
                
                print(f"\nNeighborhood '{deleted_name}' has been deleted!")
                break
            else:
                print("Invalid number! Please try again.")
        except ValueError:
            print("Please enter a valid number or 'cancel'")

def list_neighborhoods():
    """Show all available neighborhoods"""
    if not Path("neighborhoods.json").exists():
        print("No saved neighborhoods!")
        return []
    
    with open("neighborhoods.json", 'r', encoding='utf-8') as f:
        neighborhoods = json.load(f)
    
    print("\nAvailable neighborhoods:")
    for idx, n in enumerate(neighborhoods["neighborhoods"], 1):
        print(f"{idx}. {n['name']}")
    
    return neighborhoods["neighborhoods"]

def select_neighborhoods():
    """Let user select neighborhoods to check"""
    all_neighborhoods = list_neighborhoods()
    if not all_neighborhoods:
        return []
    
    print("\nEnter neighborhood numbers to check (separate with commas)")
    print("Example: 1,3,4")
    print("Or type 'all' to check all neighborhoods")
    
    while True:
        choice = input("Choice: ").strip()
        
        if choice.lower() == 'all':
            return all_neighborhoods
        
        try:
            # Convert input to list of indices
            selected_idx = [int(x.strip()) for x in choice.split(',')]
            # Convert to 0-based index and get neighborhoods
            selected = [all_neighborhoods[i-1] for i in selected_idx]
            return selected
        except (ValueError, IndexError):
            print("Invalid choice! Please try again")
            continue

def check_address():
    """Check if a Hebrew/English address is within selected neighborhoods"""
    # Initialize Google Maps client
    gmaps = googlemaps.Client(key=os.getenv('GOOGLE_MAPS_API_KEY'))
    
    # Check if neighborhoods file exists
    if not Path("neighborhoods.json").exists():
        print("No saved neighborhoods! Please create a neighborhood first.")
        return

    # Let user select neighborhoods
    selected_neighborhoods = select_neighborhoods()
    if not selected_neighborhoods:
        return

    print("\nEnter address to check (Hebrew or English):")
    print("Example: דיזנגוף 50 תל אביב")
    address = input("Address: ").strip()
    
    if len(address) < 3:
        print("Address too short!")
        return

    # Add Israel if not present
    if "ישראל" not in address and "israel" not in address.lower():
        address += ", ישראל"

    try:
        # Geocode the address with Israel region bias
        result = gmaps.geocode(
            address,
            region='il',
            language='iw'
        )
        
        if not result:
            print("Address not found!")
            return
        
        # Get coordinates
        location = result[0]['geometry']['location']
        address_coords = (location['lat'], location['lng'])
        
        # Show found address for confirmation
        print(f"\nFound address: {result[0]['formatted_address']}")
        print(f"Coordinates: {location['lat']}, {location['lng']}")
        
        confirm = input("\nIs this the correct address? (yes/no): ").strip().lower()
        if confirm not in ['yes', 'y']:
            print("Check cancelled.")
            return
        
        # Check each selected neighborhood
        found_in = []
        for n in selected_neighborhoods:
            polygon = Polygon(n["coordinates"])
            point = Point(address_coords)
            
            if polygon.contains(point):
                found_in.append(n["name"])
        
        # Print results
        if found_in:
            print("\nAddress is in these neighborhoods:")
            for name in found_in:
                print(f"- {name}")
        else:
            print("\nAddress is not in any of the selected neighborhoods")
            
    except Exception as e:
        print(f"Error checking address: {e}")

def main_menu():
    while True:
        print("\n=== Neighborhood Checker ===")
        print("1. Create new neighborhood")
        print("2. Check address")
        print("3. List saved neighborhoods")
        print("4. Delete neighborhood")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == "1":
            create_neighborhood()
        elif choice == "2":
            check_address()
        elif choice == "3":
            list_neighborhoods()
        elif choice == "4":
            delete_neighborhood()
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main_menu()