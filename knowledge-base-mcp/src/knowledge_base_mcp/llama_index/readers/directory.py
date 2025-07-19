from collections.abc import AsyncGenerator
from pathlib import Path, PurePosixPath
from typing import Any, cast, override

from llama_index.core.readers import SimpleDirectoryReader
from llama_index.core.schema import Document
from llama_index.core.utils import get_tqdm_iterable  # pyright: ignore[reportUnknownVariableType]


class FastDirectoryReader(SimpleDirectoryReader):
    """A faster directory reader."""

    def count_files(self) -> int:
        """Count the number of files to process."""
        return len(self.input_files)

    async def afile(self, input_file: Path) -> list[Document]:
        """Load a file."""
        return await self.aload_file(  # pyright: ignore[reportUnknownMemberType]
            input_file=input_file,
            file_metadata=self.file_metadata,  # pyright: ignore[reportUnknownMemberType]
            file_extractor=self.file_extractor,
            filename_as_id=self.filename_as_id,
            encoding=self.encoding,
            errors=self.errors,
            raise_on_error=self.raise_on_error,
            fs=self.fs,
        )

    @override
    async def alazy_load_data(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, show_progress: bool = False
    ) -> AsyncGenerator[Document, Any]:
        """
        Load data iteratively from the input directory.

        Args:
            show_progress (bool): Whether to show tqdm progress bars. Defaults to False.

        Returns:
            Generator[List[Document]]: A list of documents.

        """

        resolved_input_dir = Path(self.input_dir).resolve()

        files_to_process = cast(
            "list[Path | PurePosixPath]",
            get_tqdm_iterable(
                self.input_files,
                show_progress=show_progress,
                desc="Loading files",
            ),
        )
        for input_file in files_to_process:
            input_file_relative_path: Path | PurePosixPath | None = None

            if input_file.is_relative_to(resolved_input_dir):
                input_file_relative_path = input_file.relative_to(resolved_input_dir)

            documents = await self.aload_file(  # pyright: ignore[reportUnknownMemberType]
                input_file=input_file,
                file_metadata=self.file_metadata,  # pyright: ignore[reportUnknownMemberType]
                file_extractor=self.file_extractor,
                filename_as_id=self.filename_as_id,
                encoding=self.encoding,
                errors=self.errors,
                raise_on_error=self.raise_on_error,
                fs=self.fs,
            )

            documents = self._exclude_metadata(documents)

            if len(documents) > 0:
                for document in documents:
                    document.metadata["file_path"] = str(input_file_relative_path or input_file)
                    document.metadata["dir_path"] = str(resolved_input_dir)

                    yield document
