from syrupy.extensions.single_file import SingleFileSnapshotExtension, WriteMode


class MarkdownSnapshotExtension(SingleFileSnapshotExtension):
    _file_extension: str = "md"
    _write_mode = WriteMode.TEXT
