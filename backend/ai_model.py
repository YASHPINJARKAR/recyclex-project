import cv2
import numpy as np

def classify(image_path: str) -> str:
    """
    Hackathon AI Model Fallback:
    Uses OpenCV to analyze image heuristics (Edge Density + Color Saturation)
    to deterministically classify waste without needing heavy TensorFlow.
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            return "Unknown (File Unreadable)"

        # 1. Edge Density Analysis (Canny)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        
        # Calculate percentage of edge pixels
        edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])

        # 2. Color Saturation & Brightness Analysis (HSV)l̥
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        avg_saturation = np.mean(hsv[:, :, 1])
        avg_brightness = np.mean(hsv[:, :, 2])

        print(f"[{image_path}] Edge Density: {edge_density:.4f}, Saturation: {avg_saturation:.1f}")

        # Basic Heuristic Logic:
        # High edges + High brightness -> likely crinkled plastic bottles/wrappers
        if edge_density > 0.05 and avg_brightness > 120:
            return "Plastic"
            
        # Very high edges + low saturation -> likely crumpled newspaper/cardboard
        elif edge_density > 0.06 and avg_saturation < 50:
            return "Paper"
            
        # Medium edges + Highly reflective/variable brightness -> likely cans/metal
        elif edge_density > 0.03 and edge_density <= 0.06 and avg_saturation < 100:
            return "Metal"
            
        # Low edges + High structure -> bulky items like E-Waste
        elif edge_density < 0.03 and avg_saturation > 50:
            return "E-Waste"
            
        # Fallback
        return "Mixed Plastic/Paper"
        
    except Exception as e:
        print(f"Error classifying {image_path}: {e}")
        return "Unknown Error"