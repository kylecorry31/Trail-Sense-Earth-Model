from .summarizer import Summarizer
from scripts import openai
import json

summary_schema = {
    "name": "Species",
    "strict": True,
    "schema": {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "species.schema.json",
        "title": "Species",
        "description": "A species of plant, animal, or fungus.",
        "type": "object",
        "properties": {
            "commonName": {
                "description": "The common name of the species.",
                "type": "string"
            },
            "description": {
                "description": "A one sentence description of the species.",
                "type": "string"
            },
            "notes": {
                "description": "Important notes about the species such as rarity, behavior, aggression, or poison/venom.",
                "type": ["string", "null"]
            },
            "appearance": {
                "description": "A short and simple description of the appearance of the species to assist in identification.",
                "type": ["string", "null"]
            },
            "uses": {
                "description": "How can this species be used by a human in a wilderness survival situation. Includes whether it is edible, medicinal, or use for tools. Includes a brief description of the preparation required.",
                "type": ["string", "null"]
            },
            "continents": {
                "description": "The continents the species is found on in the wild.",
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": ['Africa', 'Antarctica', 'Asia', 'Australia', 'Europe', 'North America', 'South America']
                },
            },
            "habitats": {
                "description": "The habitats the species is found in.",
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": ['Forest', 'Desert', 'Grassland', 'Wetland', 'Mountain', 'Urban', 'Marine', 'Freshwater', 'Cave', 'Tundra']
                },
            },
            "kingdom": {
                "description": "The kingdom this species is classified under.",
                "type": "string",
                "enum": ['Plant', 'Animal', 'Fungus'],
            },
            "class": {
                "description": "The class this species is classified under or null if not one of the common classes.",
                "type": ["string", "null"],
                "enum": ['Bird', 'Mammal', 'Reptile', 'Amphibian', 'Fish', 'Insect', 'Arachnid', 'Crustacean', 'Mollusk'],
            },
            "isDangerous": {
                "description": "Whether the species is dangerous to humans.",
                "type": "boolean"
            },
        },
        "required": ["commonName", "description", "notes", "appearance", "uses", "continents", "habitats", "kingdom", "class", "isDangerous"],
        "additionalProperties": False
    }
}


class OpenAISummarizer(Summarizer):

    def __init__(self, regenerate=False):
        super().__init__()
        self.regenerate = regenerate

    def summarize(self, scientific_name, common_name, wikipedia_sections):
        # TODO: If it is invalid, reprocess once
        response = openai.process(scientific_name, f"Instructions: Summarize the species for my field guide, be very brief in your responses.\n\n{wikipedia_sections['full']}", self.regenerate, response_format={
            "type": "json_schema",
            "json_schema": summary_schema
        })

        response = json.loads(response)

        tags = []
        if 'continents' in response:
            tags.extend(response['continents'])
        else:
            print(f"Missing continents for {scientific_name}")
        if 'habitats' in response:
            tags.extend(response['habitats'])
        else:
            print(f"Missing habitats for {scientific_name}")
        if 'kingdom' in response:
            tags.append(response['kingdom'])
        else:
            print(f"Missing kingdom for {scientific_name}")
        if 'class' in response and response['kingdom'] == 'Animal':
            tags.append(response['class'])
        if 'isDangerous' in response and response['isDangerous']:
            tags.append('Dangerous')

        name = response['commonName'] if 'commonName' in response else common_name

        notes = []
        if 'description' in response:
            notes.append(response['description'])
        else:
            print(f"Missing description for {scientific_name}")
        # if 'appearance' in response and response['appearance'] != '':
        #     notes.append(f"APPEARANCE\n{response['appearance']}")
        # if 'uses' in response and response['uses'] != '':
        #     notes.append(f"USES\n{response['uses']}")
        # if 'notes' in response and response['notes'] != '':
        #     notes.append(f"ADDITIONAL NOTES\n{response['notes']}")

        notes = '\n\n'.join(notes)

        return {
            "name": name,
            "notes": notes,
            "tags": tags
        }
