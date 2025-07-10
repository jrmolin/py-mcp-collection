from fastmcp.utilities.logging import configure_logging, get_logger

configure_logging(level="INFO")
BASE_LOGGER = get_logger("kb_mcp")

if BASE_LOGGER.parent is not None:
    BASE_LOGGER.parent.propagate = False
