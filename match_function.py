import spacy
from functools import lru_cache
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

# Function data
functions = [
        {
            "name": "prime_pumps",
            "description": "Primes the ChemSpeed pumps.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pump": {
                        "type": "integer",
                        "description": "pump being primed",
                    },
                    "volume": {
                        "type": "number",
                        "description": "volume with which to prime pumps"},
                },
                "required": ["pump", "volume"],
            },
        },
        {
            "name": "transfer_liquid",
            "description": "Executes a liquid transfer from the source to the target zone.",
            "parameters": {
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "Source zone for the liquid transfer."
                    },
                    "destination": {
                        "type": "string",
                        "description": "Destination zone for the liquid transfer."
                    },
                    "volume": {
                        "type": "number",
                        "description": "Volume to transfer [mL]"
                    },
                    "needle": {
                        "type": "integer",
                        "description": "Number of the needle to use (0 means all needles)."
                    },
                },
                "required": ["source", "destination", "volume", "needle"],
            },
        },
        {
            "name": "transfer_solid",
            "description": "Executes a solid transfer from the source to the target destination.",
            "parameters": {
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "Source zone for the solid transfer."
                    },
                    "destination": {
                        "type": "string",
                        "description": "Destination zone for the solid transfer."
                    },
                    "weight": {
                        "type": "number",
                        "description": "Mass to dispense [mg]"
                    },
                },
                "required": ["source", "destination", "weight"],
            },
        },
        {
            "name": "do_schlenk_cycles",
            "description": "Performs Schlenk Cycles (evacuate-refill cycles) on the specified wells.",
            "parameters": {
                "type": "object",
                "properties": {
                    "wells": {
                        "type": "string",
                        "description": "Zones to be set to inert gas."
                    },
                    "evac_time": {
                        "type": "integer",
                        "description": "Time (in sec) for evacuation. Default: 60 sec."
                    },
                    "backfill_time": {
                        "type": "integer",
                        "description": "Time (in sec) for backfilling with inert gas. Default: 30 sec."
                    },
                },
                "required": ["wells"],
            },
        },
        {
            "name": "heat_under_reflux",
            "description": "Sets up the heating and the reflux condenser for a specified time period. Cools the system back to room temperature for a specified cooling period.",
            "parameters": {
                "type": "object",
                "properties": {
                    "wells": {
                        "type": "string",
                        "description": "wells to be heated under reflux."
                    },
                    "stir_rate": {
                        "type": "number",
                        "description": "Stir rate (in rpm)"
                    },
                    "temperature": {
                        "type": "number",
                        "description": "Heating temperature (in °C)"
                    },
                    "heating_hours": {
                        "type": "integer",
                        "description": "Heating time (in h)"
                    },
                    "cooling_hours": {
                        "type": "integer",
                        "description": "Cooling time (in h)"
                    },
                    "condenser_temperature": {
                        "type": "number",
                        "description": "Temperature (in °C) of the reflux condenser."
                    },
                },
                "required": ["wells", "stir_rate", "temperature", "heating_hours", "cooling_hours"],
            },
        },
        {
            "name": "filter_liquid",
            "description": "Filters a liquid sample on a filtration rack. Allows for collecting the filtrate, washing and eluting the filter.",
            "parameters": {
                "type": "object",
                "properties": {
                    "source_well": {
                        "type": "string",
                        "description": "Source well of the sample to be filtered."
                    },
                    "filtration_zone": {
                        "type": "string",
                        "description": "Zone on the filtration rack to be used."
                    },
                    "filtration_volume": {
                        "type": "number",
                        "description": "Volume (in mL) of liquid to be filtered."
                    },
                },
                "required": ["source_well", "filtration_zone", "filtration_volume"],
            },
        },
    ]

@lru_cache(maxsize=None)
def load_spacy_model():
    return spacy.load("en_core_web_sm")

# Load the English language model
nlp = load_spacy_model()

def preprocess_text(text):
    doc = nlp(text.lower())  # Convert to lowercase and tokenize the text
    return " ".join([token.lemma_ for token in doc if not token.is_stop and not token.is_punct])

def match_to_function(instruction, functions):
    processed_instruction = preprocess_text(instruction)

    # Function descriptions
    function_descriptions = [func["description"] for func in functions]

    # Preprocess the function descriptions
    processed_descriptions = [preprocess_text(desc) for desc in function_descriptions]

    # Calculate the similarity using Cosine Similarity
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([processed_instruction] + processed_descriptions)
    cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    # Get the index of the best matching function
    best_match_index = cosine_similarities.argmax()
    best_match_function = functions[best_match_index]["name"]
    
    return best_match_function

if __name__ == "__main__":
    
    # Define the instruction you want to match
    instructions = """Prime pump 1 with 30 mL using chemspd as manager.
Transfer 10 mL of THF (liquid) from thf to internal_standard with needle 1.
Transfer 0.1 mg of boronic acid (solid) from bmida to rxn_well.
Transfer 0.1 mg of halide (solid) from halide to rxn_well.
Transfer 0.1 mg of base (solid) from base to rxn_well.
Perform Schlenk cycles on rxn_well with 60 sec evacuation and 30 sec backfill_time.
Transfer 0.1 mL of catalyst solution from catalyst_solution to rxn_well with needle 1.
Transfer 1.0 mL of solvent from solvent to rxn_well with needle 1.
Transfer 1.0 mL of water from water to rxn_well with needle 4.
Reflux rxn_well at 100 rpm, 100 C, heat and cool 1 hour and condenser temperature at 20 C.
Transfer 10 mL of internal standard (liquid) from internal_standard to rxn_well with needle 1.
Filter 3 mL liquid sourced from rxn_well. Use filter_cartridge as filtration rack.
Transfer 3.0 mL of THF (liquid) from thf into filter_cartridge with needle 1.
Transfer 0.2 mL liquid from filtrate_well to hplc_port with needle 1."""
    for instruction in instructions.split("\n"):
        print(f"Instruction: {instruction}")
        # Find the best matching function
        best_match_function = match_to_function(instruction, functions)

        print(f"The best matching function is: {best_match_function}")
