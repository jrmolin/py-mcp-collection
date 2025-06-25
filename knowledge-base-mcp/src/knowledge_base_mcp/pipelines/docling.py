from docling.datamodel.base_models import InputFormat
from llama_index.core.ingestion import IngestionPipeline
from llama_index.node_parser.docling import DoclingNodeParser

from knowledge_base_mcp.llama_index.ingestion_pipelines.batching import PipelineGroup
from knowledge_base_mcp.llama_index.node_parsers.document_to_docling_document import DocumentToDoclingDocumentNodeParser
from knowledge_base_mcp.llama_index.transformations.docling_parent_heading import DoclingParentHeading
from knowledge_base_mcp.llama_index.transformations.metadata_trimmer import MetadataTrimmer

MAX_TOKENS_BUFFER = 0.8


def docling_pipeline_factory() -> PipelineGroup:
    """An ingest pipeline for converting Documents with HTML/Markdown/etc to TextNodes."""

    document_to_docling_document_node_parser = DocumentToDoclingDocumentNodeParser(input_formats=[InputFormat.HTML])

    docling_node_parser = DoclingNodeParser()

    docling_parent_heading = DoclingParentHeading(parent_heading_key="parent_headings", heading_key="heading")

    docling_metadata_trimmer = MetadataTrimmer(
        remove_metadata=[
            "doc_items",
            "schema_name",
            "origin",
        ],
        remove_metadata_in_relationships=True,
        rename_metadata_keys={
            "url": "source",
        },
        exclude_embed_metadata_keys=["origin", "url", "source_type", "fetched_at"],
        exclude_llm_metadata_keys=["origin", "url", "source_type", "fetched_at"],
        flatten_list_metadata_keys=["headings", "parent_headings"],
    )

    return PipelineGroup(
        name="Docling from Raw to Text Nodes",
        pipelines=[
            IngestionPipeline(
                name="Document to Docling Document Node Parser",
                transformations=[document_to_docling_document_node_parser],
                disable_cache=True,
            ),
            IngestionPipeline(
                name="Docling Node Parser",
                transformations=[docling_node_parser],
                disable_cache=True,
            ),
            IngestionPipeline(
                name="Docling Parent Heading",
                transformations=[docling_parent_heading],
                disable_cache=True,
            ),
            IngestionPipeline(
                name="Docling Metadata Trimmer",
                transformations=[docling_metadata_trimmer],
                disable_cache=True,
            ),
        ],
    )
