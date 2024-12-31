"""Static mapping data for F1 statistics"""

from typing import Optional

# Driver ID mapping (API identifier to normalized name)
DRIVER_IDS = {
    "lewis_hamilton": "hamilton",
    "max_verstappen": "max_verstappen",
    "charles_leclerc": "leclerc",
    "sergio_perez": "perez",
    "carlos_sainz": "sainz",
    "george_russell": "russell",
    "lando_norris": "norris",
    "fernando_alonso": "alonso",
    "oscar_piastri": "piastri",
    "valtteri_bottas": "bottas",
    "carlos_sainz_jr": "sainz",
    "piastri": "piastri"
}

# Driver display names to API IDs mapping
DRIVER_DISPLAY_TO_API = {
    "max verstappen": "max_verstappen",
    "lewis hamilton": "hamilton",
    "charles leclerc": "leclerc",
    "carlos sainz": "carlos_sainz_jr",
    "oscar piastri": "piastri",
    "lando norris": "norris",
    "george russell": "russell",
    "fernando alonso": "alonso",
    "sergio perez": "perez",
    "valtteri bottas": "bottas",
    # Historical champions
    "michael schumacher": "michael_schumacher",
    "ayrton senna": "senna",
    "alain prost": "prost",
    "niki lauda": "lauda",
    "juan manuel fangio": "fangio",
    "jim clark": "clark",
    "jackie stewart": "stewart",
    "nelson piquet": "piquet",
    "jack brabham": "brabham",
    "graham hill": "graham_hill",
    "emerson fittipaldi": "fittipaldi",
    "james hunt": "hunt",
    "mario andretti": "andretti",
    "gilles villeneuve": "villeneuve",
    "keke rosberg": "rosberg",
    "nigel mansell": "mansell",
    "damon hill": "damon_hill",
    "mika hakkinen": "hakkinen",
    # Common abbreviations and variations
    "msc": "michael_schumacher",
    "schumi": "michael_schumacher",
    "m. schumacher": "michael_schumacher",
    "ver": "max_verstappen",
    "ham": "hamilton",
    "lec": "leclerc",
    "per": "perez",
    "sai": "carlos_sainz_jr",
    "rus": "russell",
    "nor": "norris",
    "alo": "alonso",
    "pia": "piastri",
    "bot": "bottas"
}

# API endpoint templates
API_TEMPLATES = {
    "driver_results": "http://ergast.com/api/f1/{season}/drivers/{driver}/results.json",
    "driver_qualifying": "http://ergast.com/api/f1/{season}/drivers/{driver}/qualifying.json",
    "race_results": "http://ergast.com/api/f1/{season}/{round}/results.json",
    "qualifying_results": "http://ergast.com/api/f1/{season}/{round}/qualifying.json",
    "constructor_results": "http://ergast.com/api/f1/{season}/constructors/{constructor}/results.json",
    "driver_standings": "http://ergast.com/api/f1/{season}/driverStandings.json",
    "constructor_standings": "http://ergast.com/api/f1/{season}/constructorStandings.json"
}

# Circuit variants and their normalized names
CIRCUIT_MAPPINGS = {
    "monaco": ["monaco", "monte carlo", "monte-carlo"],
    "monza": ["monza", "autodromo nazionale monza", "italian grand prix"],
    "silverstone": ["silverstone", "british grand prix"],
    "spa": ["spa", "spa-francorchamps", "belgian grand prix"],
    "suzuka": ["suzuka", "japanese grand prix"],
    "melbourne": ["melbourne", "albert park", "australian grand prix"],
    "barcelona": ["barcelona", "catalunya", "spanish grand prix"],
    "singapore": ["singapore", "marina bay"]
}

# Round numbers for each circuit by season
ROUND_NUMBERS = {
    "2023": {
        "bahrain": 1,
        "jeddah": 2,
        "melbourne": 3,
        "baku": 4,
        "miami": 5,
        "monaco": 6,
        "barcelona": 7,
        "montreal": 8,
        "spielberg": 9,
        "silverstone": 10,
        "budapest": 11,
        "spa": 12,
        "zandvoort": 13,
        "monza": 14,
        "singapore": 15,
        "suzuka": 16,
        "losail": 17,
        "austin": 18,
        "mexico_city": 19,
        "sao_paulo": 20,
        "las_vegas": 21,
        "yas_marina": 22
    },
    "2022": {
        "bahrain": 1,
        "jeddah": 2,
        "melbourne": 3,
        "imola": 4,
        "miami": 5,
        "barcelona": 6,
        "monaco": 7,
        "baku": 8,
        "montreal": 9,
        "silverstone": 10,
        "spielberg": 11,
        "paul_ricard": 12,
        "budapest": 13,
        "spa": 14,
        "zandvoort": 15,
        "monza": 16,
        "singapore": 17,
        "suzuka": 18,
        "austin": 19,
        "mexico_city": 20,
        "sao_paulo": 21,
        "yas_marina": 22
    }
}

# Circuit ID to normalized name mapping
CIRCUIT_IDS = {
    "monaco": "monte_carlo",
    "monza": "monza",
    "silverstone": "silverstone",
    "spa": "spa",
    "suzuka": "suzuka",
    "melbourne": "albert_park",
    "barcelona": "catalunya",
    "singapore": "marina_bay",
    "jeddah": "jeddah",
    "baku": "baku",
    "miami": "miami",
    "montreal": "montreal",
    "spielberg": "red_bull_ring",
    "budapest": "hungaroring",
    "zandvoort": "zandvoort",
    "losail": "losail",
    "austin": "americas",
    "mexico_city": "rodriguez",
    "sao_paulo": "interlagos",
    "las_vegas": "las_vegas",
    "yas_marina": "yas_marina",
    "imola": "imola",
    "paul_ricard": "paul_ricard"
}

# Circuit name variations to normalized ID
CIRCUIT_NAME_TO_ID = {
    "monaco grand prix": "monaco",
    "monte carlo": "monaco",
    "monza": "monza",
    "italian grand prix": "monza",
    "british grand prix": "silverstone",
    "silverstone": "silverstone",
    "belgian grand prix": "spa",
    "spa-francorchamps": "spa",
    "japanese grand prix": "suzuka",
    "suzuka": "suzuka",
    "australian grand prix": "melbourne",
    "albert park": "melbourne",
    "spanish grand prix": "barcelona",
    "catalunya": "barcelona",
    "singapore grand prix": "singapore",
    "marina bay": "singapore",
    "saudi arabian grand prix": "jeddah",
    "azerbaijan grand prix": "baku",
    "miami grand prix": "miami",
    "canadian grand prix": "montreal",
    "austrian grand prix": "spielberg",
    "hungarian grand prix": "budapest",
    "dutch grand prix": "zandvoort",
    "qatar grand prix": "losail",
    "united states grand prix": "austin",
    "mexico city grand prix": "mexico_city",
    "são paulo grand prix": "sao_paulo",
    "brazilian grand prix": "sao_paulo",
    "las vegas grand prix": "las_vegas",
    "abu dhabi grand prix": "yas_marina",
    "emilia romagna grand prix": "imola",
    "french grand prix": "paul_ricard"
}

# Driver name variations
DRIVER_VARIATIONS = {
    "michael_schumacher": [
        "msc", "schumi", "m. schumacher", "michael schumacher",
        "m schumacher", "m_schumacher", "m.schumacher"
    ],
    "max_verstappen": [
        "ver", "verstappen", "max verstappen",
        "m verstappen", "m. verstappen"
    ],
    "hamilton": [
        "ham", "lewis", "lewis hamilton",
        "l hamilton", "l. hamilton"
    ],
    "leclerc": [
        "lec", "charles", "charles leclerc",
        "c leclerc", "c. leclerc"
    ],
    "carlos_sainz_jr": [
        "sai", "sainz", "carlos sainz",
        "c sainz", "c. sainz"
    ],
    "piastri": [
        "pia", "oscar", "oscar piastri",
        "o piastri", "o. piastri"
    ],
    "norris": [
        "nor", "lando", "lando norris",
        "l norris", "l. norris"
    ],
    "russell": [
        "rus", "george", "george russell",
        "g russell", "g. russell"
    ],
    "alonso": [
        "alo", "fernando", "fernando alonso",
        "f alonso", "f. alonso"
    ],
    "perez": [
        "per", "checo", "sergio perez",
        "s perez", "s. perez"
    ]
}

def normalize_driver_id(driver_name: str) -> str:
    """
    Normalize a driver name to a consistent format.
    
    Args:
        driver_name: The driver name in any format (e.g., "Max Verstappen", "MAX VERSTAPPEN", "max_verstappen")
        
    Returns:
        str: The normalized driver name (lowercase, spaces replaced with underscores)
    """
    if not driver_name:
        return ""
        
    # Remove extra spaces and convert to lowercase
    normalized = driver_name.strip().lower()
    
    # Replace special characters with spaces
    normalized = normalized.replace(".", " ").replace("-", " ").replace("_", " ")
    
    # Remove any double spaces
    normalized = " ".join(normalized.split())
    
    # Check for abbreviations first
    if len(normalized) == 3 and normalized.upper() == normalized.upper():
        return normalized.lower()
    
    # Handle special case of initials (e.g., "M. Schumacher")
    parts = normalized.split()
    if len(parts) == 2 and len(parts[0]) == 1:
        # Look for full name matches
        for api_id, variations in DRIVER_VARIATIONS.items():
            for variation in variations:
                if variation.startswith(parts[0]) and variation.endswith(parts[1]):
                    return api_id
    
    return normalized

def get_driver_api_id(driver_id: str) -> str:
    """
    Get the API driver ID from a normalized driver ID.
    
    Args:
        driver_id: The normalized driver ID
        
    Returns:
        str: The API driver ID used in endpoints
    """
    normalized = normalize_driver_id(driver_id)
    
    # Check direct mapping first
    if normalized in DRIVER_DISPLAY_TO_API:
        return DRIVER_DISPLAY_TO_API[normalized]
    
    # Check variations
    for api_id, variations in DRIVER_VARIATIONS.items():
        if normalized in variations:
            return api_id
        # Check if any variation contains the normalized form
        for variation in variations:
            if normalized in variation or variation in normalized:
                return api_id
    
    # If no match found, convert spaces to underscores as fallback
    return normalized.replace(" ", "_")

def build_url(template_name: str, **kwargs) -> str:
    """
    Build a URL for the F1 API using the specified template and parameters.
    
    Args:
        template_name: The name of the template to use
        **kwargs: The parameters to fill in the template
        
    Returns:
        str: The complete URL
        
    Raises:
        ValueError: If the template name is unknown
    """
    if template_name not in API_TEMPLATES:
        raise ValueError(f"Unknown template: {template_name}")
        
    template = API_TEMPLATES[template_name]
    
    # Handle driver ID mapping if present
    if "driver" in kwargs:
        kwargs["driver"] = get_driver_api_id(kwargs["driver"])
        
    try:
        return template.format(**kwargs)
    except KeyError as e:
        raise ValueError(f"Missing required parameter: {e}")

def get_round_number(season: str, circuit_id: str) -> Optional[int]:
    """Get the round number for a specific circuit in a season"""
    if season in ROUND_NUMBERS and circuit_id in ROUND_NUMBERS[season]:
        return ROUND_NUMBERS[season][circuit_id]
    return None

def normalize_circuit_id(circuit_id: str) -> str:
    """Normalize a circuit ID"""
    circuit_id = circuit_id.lower().replace(" ", "_")
    for normalized_id, variants in CIRCUIT_MAPPINGS.items():
        if circuit_id in variants or any(variant.replace(" ", "_") == circuit_id for variant in variants):
            return normalized_id
    return circuit_id 