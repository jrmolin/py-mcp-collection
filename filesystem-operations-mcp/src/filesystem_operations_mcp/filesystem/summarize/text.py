import re

import nltk
from sumy.models.dom import Sentence
from sumy.nlp.stemmers import Stemmer
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.edmundson import EdmundsonSummarizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.summarizers.luhn import LuhnSummarizer
from sumy.summarizers.reduction import ReductionSummarizer
from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.utils import get_stop_words

from filesystem_operations_mcp.logging import BASE_LOGGER

logger = BASE_LOGGER.getChild("summarize")

nltk.download("punkt")

english_stemmer = Stemmer("english")

summarizers = [
    EdmundsonSummarizer(english_stemmer),
    LsaSummarizer(english_stemmer),
    LexRankSummarizer(english_stemmer),
    LuhnSummarizer(english_stemmer),
    TextRankSummarizer(english_stemmer),
    ReductionSummarizer(english_stemmer),
]

stop_words = get_stop_words("english")


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
    return " ".join([sentence._text for sentence in summary])


def get_luhn_summarizer(language: str) -> tuple[LuhnSummarizer, Tokenizer]:
    stemmer = Stemmer(language)
    summarizer = LuhnSummarizer(stemmer)
    summarizer.stop_words = stop_words
    tokenizer = Tokenizer(language)

    return summarizer, tokenizer


def has_verb_and_noun(tokenizer: Tokenizer, sentence: str) -> bool:
    tokenized = tokenizer.to_words(sentence)
    pos_tagged = nltk.pos_tag(tokenized)
    return any(tag.startswith("VB") for word, tag in pos_tagged) and any(tag.startswith("NN") for word, tag in pos_tagged)


def strip_long_non_words(document: str) -> str:
    return re.sub(r"\b\S{25,}\b", "", document)


def strip_code_blocks(document: str) -> str:
    return re.sub(r"```.*?```", "", document, flags=re.DOTALL)


def strip_unwanted(document: str) -> str:
    return strip_code_blocks(strip_long_non_words(document))


summarizer, tokenizer = get_luhn_summarizer("english")


def summarize_text(document: str) -> str:
    sentences = tokenizer.to_sentences(document)

    interesting_sentences = [strip_unwanted(sentence) for sentence in sentences if has_verb_and_noun(tokenizer, sentence)]

    sentences_count = ideal_sentences_count(document)

    parser = PlaintextParser.from_string("\n".join(interesting_sentences), tokenizer)

    summary: tuple[Sentence, ...] = summarizer(parser.document, sentences_count)

    return summary_to_text(summary)
