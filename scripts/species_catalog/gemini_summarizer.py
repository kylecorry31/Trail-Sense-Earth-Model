from .summarizer import Summarizer
from .parser_summarizer import ParserSummarizer
from scripts import gemini

summarize_prompt = """You are a professional content summarizer. Only use information presented in the text to summarize. If something isn't mentioned, leave it out. Write a description of the species. It should include some key features to help identify it, whether it is edible (but only if explicitely mentioned), and where it can be found (habitat and geographic location). If the common name is provided, use that instead of the scientific name. Your entire summarization MUST have at most 4 sentences.

TEXT TO SUMMARIZE:
<>

SUMMARY:"""

class GeminiSummarizer(Summarizer):

    def __init__(self, regenerate=False, scientific_name_debug_tags=[]):
        super().__init__()
        self.regenerate = regenerate
        self.scientific_name_debug_tags = scientific_name_debug_tags

    def summarize(self, scientific_name, common_name, wikipedia_sections):
        prompt = summarize_prompt.replace("<>", wikipedia_sections['full'])
        parser = ParserSummarizer(self.scientific_name_debug_tags)
        return {
            "name": common_name,
            "notes": gemini.process(scientific_name, prompt, self.regenerate),
            "tags": parser.summarize(scientific_name, common_name, wikipedia_sections)['tags']
        }
        