from llama_index.core.embeddings import BaseEmbedding


def get_model_max_tokens(model: BaseEmbedding, default: int = 256) -> int:
    model_as_dict = model.to_dict()

    return model_as_dict.get("max_length", default)