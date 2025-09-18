import os

from github_research_mcp.sampling.google_genai import GoogleGenaiSamplingHandler


def get_sampling_handler():
    return GoogleGenaiSamplingHandler(default_model=os.getenv("MODEL") or "gemini-2.5-flash")
