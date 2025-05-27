from fastmcp.exceptions import ToolError


class MCPoopsError(ToolError):
    pass


class MCPoopsResponseTooLargeError(MCPoopsError):
    pass


class MCPoopsRedirectTooLargeError(MCPoopsError):
    def __init__(self, size: int, max_size: int):
        super().__init__(f"Redirect is too large: {size} bytes. The maximum size is {max_size} bytes.")


class MCPoopsRedirectSerializationError(MCPoopsError):
    def __init__(self, tool: str):
        super().__init__(f"Error serializing redirect for tool {tool}")


class MCPoopsWriteDataError(MCPoopsError):
    def __init__(self, tool: str):
        super().__init__(f"Error writing data for tool {tool}")
