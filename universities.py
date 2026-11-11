"""
Curated High-Success University List
Rotated list to avoid saturation. Includes High-Acceptance Targets.
"""

UNIVERSITIES = {
    # Large Public Universities (High Trust)
    "University of Florida": {"id": 2548, "domain": "ufl.edu"},
    "The Ohio State University": {"id": 2552, "domain": "osu.edu"},
    "Purdue University": {"id": 2576, "domain": "purdue.edu"},
    "University of Arizona": {"id": 2530, "domain": "arizona.edu"},
    "University of Illinois Urbana-Champaign": {"id": 2544, "domain": "illinois.edu"},
    "Michigan State University": {"id": 2546, "domain": "msu.edu"},
    
    # High-Volume Online Friendly (The "Green" Zone)
    "Liberty University": {"id": 1224, "domain": "liberty.edu"},
    "Southern New Hampshire University": {"id": 8326, "domain": "snhu.edu"},
    "Grand Canyon University": {"id": 5069, "domain": "gcu.edu"},
    "Utah Valley University": {"id": 14216, "domain": "uvu.edu"}
}

def get_random_university():
    import random
    name = random.choice(list(UNIVERSITIES.keys()))
    data = UNIVERSITIES[name]
    
    return {
        "name": name, 
        "id": data["id"],
        "idExtended": str(data["id"]),
        "domain": data["domain"]
    }
