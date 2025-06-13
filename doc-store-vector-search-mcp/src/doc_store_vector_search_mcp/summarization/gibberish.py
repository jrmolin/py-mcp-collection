from pydantic import BaseModel
from transformers.pipelines import pipeline

from doc_store_vector_search_mcp.logging.util import BASE_LOGGER

logger = BASE_LOGGER.getChild("gibberish")

detector = pipeline("text-classification", model="madhurjindal/autonlp-Gibberish-Detector-492513457")


class GibberishScore(BaseModel):
    text: str
    label: str
    score: float


def detect_gibberishes(texts: list[str]) -> list[GibberishScore]:
    results: list[dict[str, str | float]] = detector(texts)  # type: ignore

    gibberish_scores = []
    for text, result in zip(texts, results, strict=True):
        if "label" not in result or "score" not in result:
            msg = f"Expected a label and a score, got {result}"
            raise ValueError(msg)

        if not isinstance(result["label"], str) or not isinstance(result["score"], float):
            msg = f"Expected a string and a float, got {type(result['label'])} and {type(result['score'])}"
            raise TypeError(msg)

        label: str = result["label"]
        score: float = result["score"]

        gibberish_scores.append(GibberishScore(text=text, label=label, score=score))

    return gibberish_scores


def remove_gibberish(texts: list[str]) -> list[str]:
    gibberish_scores = detect_gibberishes(texts)

    non_gibberish_texts = []

    for gibberish_score in gibberish_scores:
        if gibberish_score.label == "clean" or gibberish_score.score < 0.90:
            non_gibberish_texts.append(gibberish_score.text)
        else:
            logger.warning(f"Excluding gibberish: {gibberish_score.text}: {gibberish_score.label} {gibberish_score.score}")

    return non_gibberish_texts
