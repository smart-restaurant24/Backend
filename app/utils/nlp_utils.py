import spacy
from typing import Dict, Any

nlp = spacy.load("en_core_web_sm")


def extract_preferences(query: str) -> Dict[str, Any]:
    doc = nlp(query)

    preferences = {
        "dietary": [],
        "cuisine": [],
        "ingredients": {"include": [], "exclude": []},
        "price_range": None,
        "spiciness": None,
        "occasion": None
    }

    dietary_keywords = {
        "vegetarian": "Vegetarian",
        "vegan": "Vegan",
        "gluten-free": "GlutenFree",
        "dairy-free": "DairyFree",
        "halal": "Halal",
        "kosher": "Kosher"
    }

    cuisine_types = ["italian", "chinese", "indian", "mexican", "japanese", "thai", "french", "greek"]
    spiciness_levels = {"mild": 1, "medium": 2, "spicy": 3, "very spicy": 4}
    occasion_types = ["date", "birthday", "anniversary", "business", "family"]

    for token in doc:
        # Check for dietary preferences
        for keyword, preference in dietary_keywords.items():
            if keyword in token.text.lower():
                preferences["dietary"].append(preference)

        # Check for cuisine types
        if token.text.lower() in cuisine_types:
            preferences["cuisine"].append(token.text.lower())

        # Check for price range
        if token.text.lower() in ["cheap", "affordable", "inexpensive"]:
            preferences["price_range"] = "low"
        elif token.text.lower() in ["moderate", "mid-range"]:
            preferences["price_range"] = "medium"
        elif token.text.lower() in ["expensive", "high-end", "luxurious"]:
            preferences["price_range"] = "high"

        # Check for spiciness
        for level, value in spiciness_levels.items():
            if level in token.text.lower():
                preferences["spiciness"] = value

        # Check for occasion
        for occasion in occasion_types:
            if occasion in token.text.lower():
                preferences["occasion"] = occasion

    # Extract ingredients to include or exclude
    for ent in doc.ents:
        if ent.label_ == "PRODUCT" or ent.label_ == "FOOD":
            if any(excl in doc.text.lower() for excl in ["no", "without", "exclude"]):
                preferences["ingredients"]["exclude"].append(ent.text.lower())
            else:
                preferences["ingredients"]["include"].append(ent.text.lower())

    # Remove duplicates
    preferences["dietary"] = list(set(preferences["dietary"]))
    preferences["cuisine"] = list(set(preferences["cuisine"]))
    preferences["ingredients"]["include"] = list(set(preferences["ingredients"]["include"]))
    preferences["ingredients"]["exclude"] = list(set(preferences["ingredients"]["exclude"]))

    return preferences