import json
from collections import OrderedDict
from typing import (
    override,
)

import yaml
from syrupy.extensions.json import JSONSnapshotExtension
from syrupy.types import (
    PropertyFilter,
    PropertyMatcher,
    SerializableData,
    SerializedData,
)

yaml.SafeDumper.add_representer(
    OrderedDict, lambda dumper, data: dumper.represent_mapping(tag="tag:yaml.org,2002:map", mapping=data.items())
)


def yaml_multiline_string_presenter(dumper: yaml.SafeDumper, data: str) -> yaml.ScalarNode:
    if len(data.splitlines()) > 1:
        data = "\n".join([line.rstrip() for line in data.strip().splitlines()])
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")  # pyright: ignore[reportUnknownMemberType]
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)  # pyright: ignore[reportUnknownMemberType]


yaml.SafeDumper.add_representer(data_type=str, representer=yaml_multiline_string_presenter)


class YAMLSnapshotExtension(JSONSnapshotExtension):
    _file_extension: str = "yaml"

    @override
    def serialize(
        self,
        data: SerializableData,  # pyright: ignore[reportAny]
        *,
        exclude: PropertyFilter | None = None,
        include: PropertyFilter | None = None,
        matcher: PropertyMatcher | None = None,
    ) -> SerializedData:
        data = self._filter(  # pyright: ignore[reportAny]
            data=data,
            depth=0,
            path=(),
            exclude=exclude,
            include=include,
            matcher=matcher,
        )

        as_yaml: str | None = None
        as_json: str | None = None

        if isinstance(data, str):
            return data

        try:
            as_yaml = yaml.safe_dump(data, indent=2, sort_keys=False)
        except Exception as e:
            print(e)
            as_json = json.dumps(data, indent=2, ensure_ascii=False, sort_keys=False)

        if not as_yaml and not as_json:
            msg = "Failed to serialize data to YAML or JSON"
            raise ValueError(msg)

        return as_yaml or as_json  # pyright: ignore[reportReturnType]
