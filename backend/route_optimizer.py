import numpy as np
from sklearn.cluster import KMeans

def optimize_routes(locations: list) -> list:
    """
    locations: list of dicts like [{"id": 1, "lat": 18.5204, "lon": 73.8567}, ...]
    returns ordered list by simple clustering (for demo purposes)
    """
    if len(locations) < 2:
        return locations
        
    coords = np.array([[loc["lat"], loc["lon"]] for loc in locations])
    
    try:
        # Determine number of clusters based on how many collectors we have
        # For MVP we just sort them into 2 clusters
        n_clusters = min(2, len(locations))
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        kmeans.fit(coords)
        
        for i, loc in enumerate(locations):
            loc["cluster"] = int(kmeans.labels_[i])
            
        # Return sorted by cluster then simple distance
        return sorted(locations, key=lambda x: x.get("cluster", 0))
    except Exception as e:
        print(f"Error optimizing route: {e}")
        return locations
