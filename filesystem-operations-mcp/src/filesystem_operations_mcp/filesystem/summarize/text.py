import re
import zipfile
from functools import cached_property
from typing import Any, override

import nltk
from nltk.downloader import Downloader
from nltk.tokenize import PunktTokenizer
from pydantic import BaseModel, Field
from sumy.models.dom import Sentence
from sumy.nlp.stemmers import Stemmer
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.luhn import LuhnSummarizer
from sumy.utils import get_stop_words  # pyright: ignore[reportUnknownVariableType]

from filesystem_operations_mcp.logging import BASE_LOGGER


def _get_sentence_tokenizer(self, language):
    """We are overriding this as we need to replace punkt with punkt_tab in sumy"""
    if language in self.SPECIAL_SENTENCE_TOKENIZERS:
        return self.SPECIAL_SENTENCE_TOKENIZERS[language]
    try:
        return PunktTokenizer(language)
    except (LookupError, zipfile.BadZipfile) as e:
        msg = "NLTK tokenizers are missing or the language is not supported.\n"
        msg += """Download them by following command: python -c "import nltk; nltk.download('punkt_tab')"\n"""
        msg += "Original error was:\n" + str(e)
        raise LookupError(msg) from e


Tokenizer._get_sentence_tokenizer = _get_sentence_tokenizer


logger = BASE_LOGGER.getChild("summarize")


def ideal_sentences_count(document: str) -> int:
    # Estimate current sentence count as 100 characters (20 words) per sentence
    estimated_sentences = len(document) // 100

    if estimated_sentences < 10:  # noqa: PLR2004
        return 2
    if estimated_sentences < 100:  # noqa: PLR2004
        return 4
    if estimated_sentences < 1000:  # noqa: PLR2004
        return 6

    return 12


def summary_to_text(summary: tuple[Sentence, ...]) -> str:
    return " ".join([sentence._text for sentence in summary])  # pyright: ignore[reportUnknownArgumentType]


def strip_long_non_words(document: str) -> str:
    return re.sub(r"\b\S{25,}\b", "", document)


def strip_code_blocks(document: str) -> str:
    return re.sub(r"```.*?```", "", document, flags=re.DOTALL)


def strip_unwanted(document: str) -> str:
    return strip_code_blocks(strip_long_non_words(document))


class TextSummarizer(BaseModel):
    language: str = Field(default="english", description="The language of the text to summarize.")

    @override
    def model_post_init(self, __context: Any) -> None:  # pyright: ignore[reportAny]
        downloader: Downloader = Downloader()
        if not downloader.download("punkt_tab"):
            msg = "Failed to download punkt"
            raise RuntimeError(msg)

        if not downloader.download("averaged_perceptron_tagger_eng"):
            msg = "Failed to download averaged_perceptron_tagger_eng"
            raise RuntimeError(msg)

    @cached_property
    def summarizer(self) -> LuhnSummarizer:
        summarizer = LuhnSummarizer(self.stemmer)
        summarizer.stop_words = self.stop_words
        return summarizer

    @cached_property
    def stemmer(self) -> Stemmer:
        return Stemmer(self.language)

    @cached_property
    def stop_words(self) -> frozenset[str]:
        return get_stop_words(self.language)  # pyright: ignore[reportUnknownVariableType]

    @cached_property
    def tokenizer(self) -> Tokenizer:
        return Tokenizer(self.language)

    def has_verb_and_noun(self, sentence: str) -> bool:
        tokenized = self.tokenizer.to_words(sentence)
        pos_tagged = nltk.pos_tag(tokenized)
        return any(tag.startswith("VB") for word, tag in pos_tagged) and any(tag.startswith("NN") for word, tag in pos_tagged)

    def summarize(self, document: str) -> str:
        sentences = self.tokenizer.to_sentences(document)
        interesting_sentences = [strip_unwanted(sentence) for sentence in sentences if self.has_verb_and_noun(sentence)]
        sentences_count = ideal_sentences_count(document)
        parser = PlaintextParser.from_string("\n".join(interesting_sentences), self.tokenizer)
        summary: tuple[Sentence, ...] = self.summarizer(parser.document, sentences_count)
        return summary_to_text(summary)


summarizer = TextSummarizer()
