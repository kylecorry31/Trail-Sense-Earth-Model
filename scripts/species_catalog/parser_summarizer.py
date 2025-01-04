from .summarizer import Summarizer
import re

all_tags = {
    # Location
    # TODO: Add all countries
    'Africa': ['Africa'],
    'Antarctica': ['Antarctica'],
    'Asia': ['Asia', 'Japan', 'Korea', 'China', 'Russia', 'India'],
    'Australia': ['Australia', 'Oceania'],
    'Europe': ['Europe'],
    'North America': ['North America'],
    'South America': ['South America'],
    # Kingdom
    'Plant': ['| Kingdom: | Plantae |'],
    'Animal': ['| Kingdom: | Animalia |'],
    'Fungus': ['| Kingdom: | Fungi |'],
    # Class
    'Bird': ['| Class: | Aves |'],
    'Mammal': ['| Class: | Mammalia |'],
    'Reptile': ['| Class: | Reptilia |'],
    'Amphibian': ['| Class: | Amphibia |'],
    'Fish': ['| Class: | Actinopterygii |', '| Class: | Chondrichthyes |', '| Class: | Sarcopterygii |'],
    'Insect': ['| Class: | Insecta |'],
    'Arachnid': ['| Class: | Arachnida |'],
    'Crustacean': ['| Class: | Crustacea |'],
    'Mollusk': ['| Class: | Mollusca |'],
    # Habitat
    'Forest': ['Forest', 'Woodland', 'Woods'],
    'Desert': ['Desert'],
    'Grassland': ['Grassland', 'Meadow', 'Grassy', 'Steppe', 'Prairie', 'Savanna', 'Lawn', 'Pasture', 'Field'],
    'Wetland': ['Wetland', 'Swamp', 'Marsh', 'Bog', 'Swampy', 'Marshes', 'Fen', 'riverbank', 'riverbed', 'wet soil'],
    'Mountain': ['Mountain', 'Alpine'],
    'Urban': ['Urban', 'City', 'Roadside', 'along road', 'cities'],
    'Marine': ['Marine', 'Ocean', 'Sea', 'Saltwater', 'Salt-water'],
    'Freshwater': ['Freshwater', 'fresh water', 'River', 'Lake', 'Pond', 'Stream'],
    'Cave': ['Cave'],
    'Tundra': ['Tundra', 'Arctic', 'Polar'],
}


def regex_word(word):
    return r'(^|[^\w"-])' + word + r'($|[^\w"-])'


def contains_word(text, word, should_print=False):
    escaped = re.escape(word) + r's?'
    # Near isn't a negation in all cases, maybe pass in a list of additional negations for a single word
    negations_before = ['except', 'not', 'near', 'apart from']
    negations_after = []
    false_positivies = ['river basin', 'rocky mountains', 'seasonal pasture myopathy',
                        'fields of', 'field of', 'the field', 'field studies', 'field study', 'field research', 'field testing', 'field test', 'field guide', 'field work',
                        'cave painting', 'river valley', 'tethys ocean']
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s|\n', text)
    matches = list(filter(lambda x: x is not None, [
        sentence for sentence in sentences
        if re.search(regex_word(escaped), sentence) is not None
        and not any(re.search(regex_word(re.escape(false_positive) + r's?'), sentence) for false_positive in false_positivies)
        and not any(re.search(regex_word(re.escape(negation)) + r'[^\.\n]*' + regex_word(escaped), sentence) for negation in negations_before)
        and not any(re.search(regex_word(escaped) + r'?[^\.\n]*' + regex_word(re.escape(negation)), sentence) for negation in negations_after)
    ]))
    has_keyword = any(matches)
    if not has_keyword:
        return False

    if should_print:
        print("KEYWORD:", word)
        for match in matches:
            print("MATCH:", match)
            print()

    return True


class ParserSummarizer(Summarizer):

    def __init__(self, scientific_name_debug_tags=[]):
        super().__init__()
        self.scientific_name_debug_tags = scientific_name_debug_tags

    def summarize(self, scientific_name, common_name, wikipedia_sections):
        lower_page = wikipedia_sections['full'].lower()
        tags = []
        for tag in all_tags:
            if any([contains_word(lower_page, t.lower(), scientific_name in self.scientific_name_debug_tags) for t in all_tags[tag]]):
                tags.append(tag)
        return {
            "name": common_name,
            "notes": wikipedia_sections.get("extract", "").strip(),
            "tags": tags
        }
