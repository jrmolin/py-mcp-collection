from math import sqrt
import re

import nltk
from nltk import lm
from nltk.lm.vocabulary import Vocabulary
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
from nltk.tokenize import punkt, word_tokenize
from nltk.util import bigrams, ngrams
from textstat import textstat
from nltk.corpus import brown

from doc_store_vector_search_mcp.logging.util import BASE_LOGGER

logger = BASE_LOGGER.getChild("summarize")


english_stemmer = Stemmer("english")

summarizers = [
    EdmundsonSummarizer(english_stemmer),
    LsaSummarizer(english_stemmer),
    LexRankSummarizer(english_stemmer),
    LuhnSummarizer(english_stemmer),
    TextRankSummarizer(english_stemmer),
    ReductionSummarizer(english_stemmer),
]

logger.info("Initializing lang model")

nltk.download("punkt")
logger.info("Lang model initialized")

one_letter_words = [
    "a", "i"
]

two_letter_words = [
    "am", "an", "as", "at", "ax", "be", "by", "do", "go", "he", "if", "in", "is", "it", "me", "my", "no", "of", "ok", "on", "or", "ox", "so", "to", "up", "us", "we"
]

def ideal_sentences_count(sentences: list[str]) -> int:

    # Formula: keep the information for small documents, but summarize more and more as the document gets longer
    if len(sentences) <= 2:
        return len(sentences)
    
    # 4 -> 4
    # 9 -> 6
    # 16 -> 8
    # 25 -> 10
    # 36 -> 12
    # 49 -> 14
    # 64 -> 16
    # 81 -> 18
    # 100 -> 20

    return int(sqrt(len(sentences)) * 2)



def summary_to_text(summary: tuple[Sentence, ...]) -> str:
    sentences_with_endings = []

    for sentence in summary:

        sentence_length = len(sentence._text)
        sentence_reading_ease = textstat.flesch_reading_ease(sentence._text)

        if sentence_length > 200 and sentence_reading_ease < -100:
           logger.warning(f"Skipping sentence because it is very long and has a low flesch reading ease: {sentence._text[:200]}...")
           continue

        if sentence._text.endswith("."):
            sentences_with_endings.append(sentence._text)
        else:
            sentences_with_endings.append(sentence._text + ".")

    return "\n".join(sentences_with_endings)

def get_tokenizer(language: str) -> Tokenizer:
    return Tokenizer(language)

def get_luhn_summarizer(language: str) -> tuple[LuhnSummarizer, Tokenizer]:
    stemmer = Stemmer(language)
    summarizer = LuhnSummarizer(stemmer)
    summarizer.stop_words = get_stop_words("english")
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


def strip_non_az_09_punctuation(document: str) -> str:
    return re.sub(r"[^a-zA-Z0-9\s]+", "", document)

def strip_short_words(document: str) -> str:
    words = document.split()
    keep_words = []

    for i, word in enumerate(words):
        if len(word) == 1 and word not in one_letter_words:  # noqa: SIM114
            keep_words.append(word)
        elif len(word) == 2 and word not in two_letter_words:  # noqa: PLR2004
            keep_words.append(word)
        else:
            keep_words.append(word)

    return " ".join(keep_words)

def strip_unwanted(document: str) -> str:
    return strip_code_blocks(strip_short_words(strip_long_non_words(strip_non_az_09_punctuation(document))))

def extract_sentences(document: str) -> list[str]:
    tokenizer = get_tokenizer("english")
    sentences = tokenizer.to_sentences(document)

    return list(sentences)

def remove_horrible_sentences(sentences: list[str]) -> list[str]:
    new_sentences = []

    for sentence in sentences:
        sentence_length = len(sentence)
        sentence_reading_ease = textstat.flesch_reading_ease(sentence)

        if sentence_length > 200 and sentence_reading_ease < -100:
            logger.warning(f"Skipping sentence because it is very long and has a low flesch reading ease: {sentence[:200]}...")
            continue

        new_sentences.append(sentence)

    return new_sentences

def clean_sentences(sentences: list[str]) -> list[str]:
    new_sentences = []

    for sentence in sentences:
        # If the sentence does not contain at least 3 words, skip it
        if len(sentence.split()) < 3:
            continue

        # Remove any leading symbols and whitespace
        new_sentence = sentence.lstrip().lstrip(".,:;!?").lstrip()

        # Remove any trailing whitespace and periods
        new_sentence = new_sentence.rstrip().rstrip(".").rstrip()

        # If the last char is a-zA-Z0-9, add a period
        if new_sentence[-1].isalnum() or new_sentence[-1] in  ")]":
            new_sentence += "."

        new_sentences.append(new_sentence)

    return new_sentences

def clean_text_embeddings(document: str) -> str:
    tokenizer = get_tokenizer("english")

    sentences = tokenizer.to_sentences(document)

    new_sentences = []
    for sentence in sentences:
        #new_sentences.append(strip_unwanted(sentence))

        sentence_length = len(sentence)
        sentence_reading_ease = textstat.flesch_reading_ease(sentence)

        if sentence_length > 200 and sentence_reading_ease < -100:
           logger.warning(f"Skipping sentence because it is very long and has a low flesch reading ease: {sentence[:200]}...")
           continue

        if sentence.endswith("."):
            new_sentences.append(sentence)
        else:
            new_sentences.append(sentence + ".")

    return "\n".join(new_sentences)

def summarize_text(document: str) -> str:
    summarizer, tokenizer = get_luhn_summarizer("english")

    original_sentences = tokenizer.to_sentences(document)

    stripped_sentences = [strip_unwanted(sentence) for sentence in original_sentences]

    interesting_sentences = [sentence for sentence in stripped_sentences if has_verb_and_noun(tokenizer, sentence)]

    sentences_count = ideal_sentences_count(interesting_sentences)

    parser = PlaintextParser.from_string(".\n".join(interesting_sentences), tokenizer)

    summary: tuple[Sentence, ...] = summarizer(parser.document, sentences_count)

    return summary_to_text(summary)


# def print_sentence_stats(sentence: str):
#     print("--------------------------------")
#     print("sentence", sentence)
#     print("standard", textstat.text_standard(sentence))
#     print("flesch_reading_ease", textstat.flesch_reading_ease(sentence))
#     print("flesch_kincaid_grade", textstat.flesch_kincaid_grade(sentence))
#     print("smog_index", textstat.smog_index(sentence))
#     print("coleman_liau_index", textstat.coleman_liau_index(sentence))
#     print("automated_readability_index", textstat.automated_readability_index(sentence))
#     print("dale_chall_readability_score", textstat.dale_chall_readability_score(sentence))
#     print("difficult_words", textstat.difficult_words(sentence))
#     print("linsear_write_formula", textstat.linsear_write_formula(sentence))
#     print("gunning_fog", textstat.gunning_fog(sentence))
#     print("text_standard", textstat.text_standard(sentence))
#     print("fernandez_huerta", textstat.fernandez_huerta(sentence))
#     print("szigriszt_pazos", textstat.szigriszt_pazos(sentence))
#     print("gutierrez_polini", textstat.gutierrez_polini(sentence))
#     print("crawford", textstat.crawford(sentence))
#     print("gulpease_index", textstat.gulpease_index(sentence))
#     print("osman", textstat.osman(sentence))
