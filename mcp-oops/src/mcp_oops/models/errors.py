class MCPoopsError(Exception):
    def __init__(self, message: str):
        self.message = message


class MCPoopsResponseTooLargeError(MCPoopsError):
    def __init__(self, tool: str, size: int, max_size: int):
        super().__init__(f"Response for tool {tool} is too large: {size} bytes. The maximum size is {max_size} bytes.")


class MCPoopsRedirectTooLargeError(MCPoopsError):
    def __init__(self, tool: str, size: int, max_size: int):
        super().__init__(f"Redirect for tool {tool} is too large: {size} bytes. The maximum size is {max_size} bytes.")


class MCPoopsRedirectSerializationError(MCPoopsError):
    def __init__(self, tool: str):
        super().__init__(f"Error serializing redirect for tool {tool}")


class MCPoopsWriteDataError(MCPoopsError):
    def __init__(self, tool: str):
        super().__init__(f"Error writing data for tool {tool}")
