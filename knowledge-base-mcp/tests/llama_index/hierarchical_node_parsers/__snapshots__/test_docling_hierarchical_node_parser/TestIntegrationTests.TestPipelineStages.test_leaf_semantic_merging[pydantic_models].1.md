# BaseModel

Pydantic models are simply classes which inherit from BaseModel and define fields as annotated attributes.

## pydantic.BaseModel
¶

Usage Documentation

Models

A base class for creating Pydantic models.

Attributes:

| Name                          | Type                                       | Description                                                                                                                                                       |
|-------------------------------|--------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| __class_vars__                | set[str]                                   | The names of the class variables defined on the model.                                                                                                            |
| __private_attributes__        | Dict[str, ModelPrivateAttr]                | Metadata about the private attributes of the model.                                                                                                               |
| __signature__                 | Signature                                  | The synthesized __init__ Signature of the model.                                                                                                                  |
| __pydantic_complete__         | bool                                       | Whether model building is completed, or if there are still undefined fields.                                                                                      |
| __pydantic_core_schema__      | CoreSchema                                 | The core schema of the model.                                                                                                                                     |
| __pydantic_custom_init__      | bool                                       | Whether the model has a custom __init__ function.                                                                                                                 |
| __pydantic_decorators__       | DecoratorInfos                             | Metadata containing the decorators defined on the model. This replaces Model.__validators__ and Model.__root_validators__ from Pydantic V1.                       |
| __pydantic_generic_metadata__ | PydanticGenericMetadata                    | Metadata for generic models; contains data used for a similar purpose to args, origin, parameters in typing-module generics. May eventually be replaced by these. |
| __pydantic_parent_namespace__ | Dict[str, Any] | None                      | Parent namespace of the model, used for automatic rebuilding of models.                                                                                           |
| __pydantic_post_init__        | None | Literal['model_post_init']          | The name of the post-init method for the model, if defined.                                                                                                       |
| __pydantic_root_model__       | bool                                       | Whether the model is a RootModel.                                                                                                                                 |
| __pydantic_serializer__       | SchemaSerializer                           | The pydantic-core SchemaSerializer used to dump instances of the model.                                                                                           |
| __pydantic_validator__        | SchemaValidator | PluggableSchemaValidator | The pydantic-core SchemaValidator used to validate instances of the model.                                                                                        |
| __pydantic_fields__           | Dict[str, FieldInfo]                       | A dictionary of field names and their corresponding FieldInfo objects.                                                                                            |
| __pydantic_computed_fields__  | Dict[str, ComputedFieldInfo]               | A dictionary of computed field names and their corresponding ComputedFieldInfo objects.                                                                           |
| __pydantic_extra__            | Dict[str, Any] | None                      | A dictionary containing extra values, if extra is set to 'allow'.                                                                                                 |
| __pydantic_fields_set__       | set[str]                                   | The names of fields explicitly set during instantiation.                                                                                                          |
| __pydantic_private__          | Dict[str, Any] | None                      | Values of private attributes set on the model instance.                                                                                                           |

Source code in pydantic/main.py

### __init__
¶

```
__init__(**data: Any) -> None
```

Raises ValidationError if the input data cannot be
validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Source code in pydantic/main.py

### model_config

class-attribute

¶

```
model_config: ConfigDict = ConfigDict()
```

Configuration for the model, should be a dictionary conforming to ConfigDict.

### model_fields

classmethod

¶

```
model_fields() -> dict[str, FieldInfo]
```

A mapping of field names to their respective FieldInfo instances.

Warning

Accessing this attribute from a model instance is deprecated, and will not work in Pydantic V3.
Instead, you should access this attribute from the model class.

Source code in pydantic/main.py

### model_computed_fields

classmethod

¶

```
model_computed_fields() -> dict[str, ComputedFieldInfo]
```

A mapping of computed field names to their respective ComputedFieldInfo instances.

Warning

Accessing this attribute from a model instance is deprecated, and will not work in Pydantic V3.
Instead, you should access this attribute from the model class.

Source code in pydantic/main.py

### __pydantic_core_schema__

class-attribute

¶

```
__pydantic_core_schema__: CoreSchema
```

The core schema of the model.

### model_extra

property

¶

```
model_extra: dict[str, Any] | None
```

Get extra fields set during validation.

Returns:

| Type                  | Description                                                                  |
|-----------------------|------------------------------------------------------------------------------|
| dict[str, Any] | None | A dictionary of extra fields, or None if config.extra is not set to "allow". |

### model_fields_set

property

¶

```
model_fields_set: set[str]
```

Returns the set of fields that have been explicitly set on this model instance.

Returns:

| Type     | Description                                                                                           |
|----------|-------------------------------------------------------------------------------------------------------|
| set[str] | A set of strings representing the fields that have been set, i.e. that were not filled from defaults. |

### model_construct

classmethod

¶

```
model_construct(
  _fields_set: set[str] | None = None, **values: Any
) -> Self
```

Creates a new instance of the Model class with validated data.

Creates a new model setting __dict__ and __pydantic_fields_set__ from trusted or pre-validated data.
Default values are respected, but no other validation is performed.

Note

model_construct() generally respects the model_config.extra setting on the provided model.
That is, if model_config.extra == 'allow', then all extra passed values are added to the model instance's __dict__
and __pydantic_extra__ fields. If model_config.extra == 'ignore' (the default), then all extra passed values are ignored.
Because no validation is performed with a call to model_construct(), having model_config.extra == 'forbid' does not result in
an error if extra values are passed, but they will be ignored.

Parameters:

| Name        | Type            | Description                                                                                                                                                                                                             | Default   |
|-------------|-----------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------|
| _fields_set | set[str] | None | A set of field names that were originally explicitly set during instantiation. If provided, this is directly used for the model_fields_set attribute. Otherwise, the field names from the values argument will be used. | None      |
| values      | Any             | Trusted or pre-validated data dictionary.                                                                                                                                                                               | {}        |

Returns:

| Type   | Description                                            |
|--------|--------------------------------------------------------|
| Self   | A new instance of the Model class with validated data. |

Source code in pydantic/main.py

### model_copy
¶

```
model_copy(
  *,
  update: Mapping[str, Any] | None = None,
  deep: bool = False
) -> Self
```

Usage Documentation

model_copy

Returns a copy of the model.

Note

The underlying instance's __dict__ attribute is copied. This
might have unexpected side effects if you store anything in it, on top of the model
fields (e.g. the value of cached properties).

Parameters:

| Name   | Type                     | Description                                                                                                                       | Default   |
|--------|--------------------------|-----------------------------------------------------------------------------------------------------------------------------------|-----------|
| update | Mapping[str, Any] | None | Values to change/add in the new model. Note: the data is not validated before creating the new model. You should trust this data. | None      |
| deep   | bool                     | Set to True to make a deep copy of the model.                                                                                     | False     |

Returns:

| Type   | Description         |
|--------|---------------------|
| Self   | New model instance. |

Source code in pydantic/main.py

### model_dump
¶

```
model_dump(
  *,
  mode: Literal["json", "python"] | str = "python",
  include: IncEx | None = None,
  exclude: IncEx | None = None,
  context: Any | None = None,
  by_alias: bool | None = None,
  exclude_unset: bool = False,
  exclude_defaults: bool = False,
  exclude_none: bool = False,
  round_trip: bool = False,
  warnings: (
      bool | Literal["none", "warn", "error"]
  ) = True,
  fallback: Callable[[Any], Any] | None = None,
  serialize_as_any: bool = False
) -> dict[str, Any]
```

Usage Documentation

model_dump

Generate a dictionary representation of the model, optionally specifying which fields to include or exclude.

Parameters:

| Name             | Type                                    | Description                                                                                                                                                                                        | Default   |
|------------------|-----------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------|
| mode             | Literal['json', 'python'] | str         | The mode in which to_python should run. If mode is 'json', the output will only contain JSON serializable types. If mode is 'python', the output may contain non-JSON-serializable Python objects. | 'python'  |
| include          | IncEx | None                            | A set of fields to include in the output.                                                                                                                                                          | None      |
| exclude          | IncEx | None                            | A set of fields to exclude from the output.                                                                                                                                                        | None      |
| context          | Any | None                              | Additional context to pass to the serializer.                                                                                                                                                      | None      |
| by_alias         | bool | None                             | Whether to use the field's alias in the dictionary key if defined.                                                                                                                                 | None      |
| exclude_unset    | bool                                    | Whether to exclude fields that have not been explicitly set.                                                                                                                                       | False     |
| exclude_defaults | bool                                    | Whether to exclude fields that are set to their default value.                                                                                                                                     | False     |
| exclude_none     | bool                                    | Whether to exclude fields that have a value of None.                                                                                                                                               | False     |
| round_trip       | bool                                    | If True, dumped values should be valid as input for non-idempotent types such as Json[T].                                                                                                          | False     |
| warnings         | bool | Literal['none', 'warn', 'error'] | How to handle serialization errors. False/"none" ignores them, True/"warn" logs errors, "error" raises a PydanticSerializationError.                                                               | True      |
| fallback         | Callable[[Any], Any] | None             | A function to call when an unknown value is encountered. If not provided, a PydanticSerializationError error is raised.                                                                            | None      |
| serialize_as_any | bool                                    | Whether to serialize fields with duck-typing serialization behavior.                                                                                                                               | False     |

Returns:

| Type           | Description                               |
|----------------|-------------------------------------------|
| dict[str, Any] | A dictionary representation of the model. |

Source code in pydantic/main.py

### model_dump_json
¶

```
model_dump_json(
  *,
  indent: int | None = None,
  ensure_ascii: bool = False,
  include: IncEx | None = None,
  exclude: IncEx | None = None,
  context: Any | None = None,
  by_alias: bool | None = None,
  exclude_unset: bool = False,
  exclude_defaults: bool = False,
  exclude_none: bool = False,
  round_trip: bool = False,
  warnings: (
      bool | Literal["none", "warn", "error"]
  ) = True,
  fallback: Callable[[Any], Any] | None = None,
  serialize_as_any: bool = False
) -> str
```

Usage Documentation

model_dump_json

Generates a JSON representation of the model using Pydantic's to_json method.

Parameters:

| Name             | Type                                    | Description                                                                                                                                         | Default   |
|------------------|-----------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|-----------|
| indent           | int | None                              | Indentation to use in the JSON output. If None is passed, the output will be compact.                                                               | None      |
| ensure_ascii     | bool                                    | If True, the output is guaranteed to have all incoming non-ASCII characters escaped. If False (the default), these characters will be output as-is. | False     |
| include          | IncEx | None                            | Field(s) to include in the JSON output.                                                                                                             | None      |
| exclude          | IncEx | None                            | Field(s) to exclude from the JSON output.                                                                                                           | None      |
| context          | Any | None                              | Additional context to pass to the serializer.                                                                                                       | None      |
| by_alias         | bool | None                             | Whether to serialize using field aliases.                                                                                                           | None      |
| exclude_unset    | bool                                    | Whether to exclude fields that have not been explicitly set.                                                                                        | False     |
| exclude_defaults | bool                                    | Whether to exclude fields that are set to their default value.                                                                                      | False     |
| exclude_none     | bool                                    | Whether to exclude fields that have a value of None.                                                                                                | False     |
| round_trip       | bool                                    | If True, dumped values should be valid as input for non-idempotent types such as Json[T].                                                           | False     |
| warnings         | bool | Literal['none', 'warn', 'error'] | How to handle serialization errors. False/"none" ignores them, True/"warn" logs errors, "error" raises a PydanticSerializationError.                | True      |
| fallback         | Callable[[Any], Any] | None             | A function to call when an unknown value is encountered. If not provided, a PydanticSerializationError error is raised.                             | None      |
| serialize_as_any | bool                                    | Whether to serialize fields with duck-typing serialization behavior.                                                                                | False     |

Returns:

| Type   | Description                                |
|--------|--------------------------------------------|
| str    | A JSON string representation of the model. |

Source code in pydantic/main.py

### model_json_schema

classmethod

¶

```
model_json_schema(
  by_alias: bool = True,
  ref_template: str = DEFAULT_REF_TEMPLATE,
  schema_generator: type[
      GenerateJsonSchema
  ] = GenerateJsonSchema,
  mode: JsonSchemaMode = "validation",
) -> dict[str, Any]
```

Generates a JSON schema for a model class.

Parameters:

| Name             | Type                     | Description                                                                                                                 | Default              |
|------------------|--------------------------|-----------------------------------------------------------------------------------------------------------------------------|----------------------|
| by_alias         | bool                     | Whether to use attribute aliases or not.                                                                                    | True                 |
| ref_template     | str                      | The reference template.                                                                                                     | DEFAULT_REF_TEMPLATE |
| schema_generator | type[GenerateJsonSchema] | To override the logic used to generate the JSON schema, as a subclass of GenerateJsonSchema with your desired modifications | GenerateJsonSchema   |
| mode             | JsonSchemaMode           | The mode in which to generate the schema.                                                                                   | 'validation'         |

Returns:

| Type           | Description                                |
|----------------|--------------------------------------------|
| dict[str, Any] | The JSON schema for the given model class. |

Source code in pydantic/main.py

### model_parametrized_name

classmethod

¶

```
model_parametrized_name(
  params: tuple[type[Any], ...]
) -> str
```

Compute the class name for parametrizations of generic classes.

This method can be overridden to achieve a custom naming scheme for generic BaseModels.

Parameters:

| Name   | Type                  | Description                                                                                                                                                          | Default   |
|--------|-----------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------|
| params | tuple[type[Any], ...] | Tuple of types of the class. Given a generic class Model with 2 type variables and a concrete model Model[str, int], the value (str, int) would be passed to params. | required  |

Returns:

| Type   | Description                                                                         |
|--------|-------------------------------------------------------------------------------------|
| str    | String representing the new class where params are passed to cls as type variables. |

Raises:

| Type      | Description                                                           |
|-----------|-----------------------------------------------------------------------|
| TypeError | Raised when trying to generate concrete names for non-generic models. |

Source code in pydantic/main.py

### model_post_init
¶

```
model_post_init(context: Any) -> None
```

Override this method to perform additional initialization after __init__ and model_construct.
This is useful if you want to do some validation that requires the entire model to be initialized.

Source code in pydantic/main.py

### model_rebuild

classmethod

¶

```
model_rebuild(
  *,
  force: bool = False,
  raise_errors: bool = True,
  _parent_namespace_depth: int = 2,
  _types_namespace: MappingNamespace | None = None
) -> bool | None
```

Try to rebuild the pydantic-core schema for the model.

This may be necessary when one of the annotations is a ForwardRef which could not be resolved during
the initial attempt to build the schema, and automatic rebuilding fails.

Parameters:

| Name                    | Type                    | Description                                                             | Default   |
|-------------------------|-------------------------|-------------------------------------------------------------------------|-----------|
| force                   | bool                    | Whether to force the rebuilding of the model schema, defaults to False. | False     |
| raise_errors            | bool                    | Whether to raise errors, defaults to True.                              | True      |
| _parent_namespace_depth | int                     | The depth level of the parent namespace, defaults to 2.                 | 2         |
| _types_namespace        | MappingNamespace | None | The types namespace, defaults to None.                                  | None      |

Returns:

| Type        | Description                                                                             |
|-------------|-----------------------------------------------------------------------------------------|
| bool | None | Returns None if the schema is already "complete" and rebuilding was not required.       |
| bool | None | If rebuilding was required, returns True if rebuilding was successful, otherwise False. |

Source code in pydantic/main.py

### model_validate

classmethod

¶

```
model_validate(
  obj: Any,
  *,
  strict: bool | None = None,
  from_attributes: bool | None = None,
  context: Any | None = None,
  by_alias: bool | None = None,
  by_name: bool | None = None
) -> Self
```

Validate a pydantic model instance.

Parameters:

| Name            | Type        | Description                                                                       | Default   |
|-----------------|-------------|-----------------------------------------------------------------------------------|-----------|
| obj             | Any         | The object to validate.                                                           | required  |
| strict          | bool | None | Whether to enforce types strictly.                                                | None      |
| from_attributes | bool | None | Whether to extract data from object attributes.                                   | None      |
| context         | Any | None  | Additional context to pass to the validator.                                      | None      |
| by_alias        | bool | None | Whether to use the field's alias when validating against the provided input data. | None      |
| by_name         | bool | None | Whether to use the field's name when validating against the provided input data.  | None      |

Raises:

| Type            | Description                           |
|-----------------|---------------------------------------|
| ValidationError | If the object could not be validated. |

Returns:

| Type   | Description                   |
|--------|-------------------------------|
| Self   | The validated model instance. |

Source code in pydantic/main.py

### model_validate_json

classmethod

¶

```
model_validate_json(
  json_data: str | bytes | bytearray,
  *,
  strict: bool | None = None,
  context: Any | None = None,
  by_alias: bool | None = None,
  by_name: bool | None = None
) -> Self
```

Usage Documentation

JSON Parsing

Validate the given JSON data against the Pydantic model.

Parameters:

| Name      | Type                    | Description                                                                       | Default   |
|-----------|-------------------------|-----------------------------------------------------------------------------------|-----------|
| json_data | str | bytes | bytearray | The JSON data to validate.                                                        | required  |
| strict    | bool | None             | Whether to enforce types strictly.                                                | None      |
| context   | Any | None              | Extra variables to pass to the validator.                                         | None      |
| by_alias  | bool | None             | Whether to use the field's alias when validating against the provided input data. | None      |
| by_name   | bool | None             | Whether to use the field's name when validating against the provided input data.  | None      |

Returns:

| Type   | Description                   |
|--------|-------------------------------|
| Self   | The validated Pydantic model. |

Raises:

| Type            | Description                                                             |
|-----------------|-------------------------------------------------------------------------|
| ValidationError | If json_data is not a JSON string or the object could not be validated. |

Source code in pydantic/main.py

### model_validate_strings

classmethod

¶

```
model_validate_strings(
  obj: Any,
  *,
  strict: bool | None = None,
  context: Any | None = None,
  by_alias: bool | None = None,
  by_name: bool | None = None
) -> Self
```

Validate the given object with string data against the Pydantic model.

Parameters:

| Name     | Type        | Description                                                                       | Default   |
|----------|-------------|-----------------------------------------------------------------------------------|-----------|
| obj      | Any         | The object containing string data to validate.                                    | required  |
| strict   | bool | None | Whether to enforce types strictly.                                                | None      |
| context  | Any | None  | Extra variables to pass to the validator.                                         | None      |
| by_alias | bool | None | Whether to use the field's alias when validating against the provided input data. | None      |
| by_name  | bool | None | Whether to use the field's name when validating against the provided input data.  | None      |

Returns:

| Type   | Description                   |
|--------|-------------------------------|
| Self   | The validated Pydantic model. |

Source code in pydantic/main.py

## pydantic.create_model
¶

```
create_model(
  model_name: str,
  /,
  *,
  __config__: ConfigDict | None = None,
  __doc__: str | None = None,
  __base__: None = None,
  __module__: str = __name__,
  __validators__: (
      dict[str, Callable[..., Any]] | None
  ) = None,
  __cls_kwargs__: dict[str, Any] | None = None,
  **field_definitions: Any | tuple[str, Any],
) -> type[BaseModel]
```

```
create_model(
  model_name: str,
  /,
  *,
  __config__: ConfigDict | None = None,
  __doc__: str | None = None,
  __base__: type[ModelT] | tuple[type[ModelT], ...],
  __module__: str = __name__,
  __validators__: (
      dict[str, Callable[..., Any]] | None
  ) = None,
  __cls_kwargs__: dict[str, Any] | None = None,
  **field_definitions: Any | tuple[str, Any],
) -> type[ModelT]
```

```
create_model(
  model_name: str,
  /,
  *,
  __config__: ConfigDict | None = None,
  __doc__: str | None = None,
  __base__: (
      type[ModelT] | tuple[type[ModelT], ...] | None
  ) = None,
  __module__: str | None = None,
  __validators__: (
      dict[str, Callable[..., Any]] | None
  ) = None,
  __cls_kwargs__: dict[str, Any] | None = None,
  **field_definitions: Any | tuple[str, Any],
) -> type[ModelT]
```

Usage Documentation

Dynamic Model Creation

Dynamically creates and returns a new Pydantic model, in other words, create_model dynamically creates a
subclass of BaseModel.

Parameters:

| Name                | Type                                           | Description                                                                                                                                                                                                                                       | Default   |
|---------------------|------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------|
| model_name          | str                                            | The name of the newly created model.                                                                                                                                                                                                              | required  |
| __config__          | ConfigDict | None                              | The configuration of the new model.                                                                                                                                                                                                               | None      |
| __doc__             | str | None                                     | The docstring of the new model.                                                                                                                                                                                                                   | None      |
| __base__            | type[ModelT] | tuple[type[ModelT], ...] | None | The base class or classes for the new model.                                                                                                                                                                                                      | None      |
| __module__          | str | None                                     | The name of the module that the model belongs to; if None, the value is taken from sys._getframe(1)                                                                                                                                               | None      |
| __validators__      | dict[str, Callable[..., Any]] | None           | A dictionary of methods that validate fields. The keys are the names of the validation methods to be added to the model, and the values are the validation methods themselves. You can read more about functional validators here.                | None      |
| __cls_kwargs__      | dict[str, Any] | None                          | A dictionary of keyword arguments for class creation, such as metaclass.                                                                                                                                                                          | None      |
| **field_definitions | Any | tuple[str, Any]                          | Field definitions of the new model. Either:  a single element, representing the type annotation of the field. a two-tuple, the first element being the type and the second element the assigned value (either a default or the Field() function). | {}        |

Returns:

| Type         | Description    |
|--------------|----------------|
| type[ModelT] | The new model. |

Raises:

| Type              | Description                                 |
|-------------------|---------------------------------------------|
| PydanticUserError | If __base__ and __config__ are both passed. |

Source code in pydantic/main.py

Thanks for your feedback!

Thanks for your feedback!