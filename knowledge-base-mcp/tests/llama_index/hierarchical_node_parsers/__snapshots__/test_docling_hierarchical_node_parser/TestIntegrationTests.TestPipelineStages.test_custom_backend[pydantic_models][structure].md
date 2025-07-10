 : 0 - 35053: # BaseModel  Pydantic models are simply classes wh
   : 1 - 11: # BaseModel
   : 2 - 106: Pydantic models are simply classes which inherit f
   : 3 - 29832: ## pydantic.BaseModel ¶  Usage Documentation  Mode
     : 4 - 21: ## pydantic.BaseModel
     : 5 - 19: Usage Documentation
     : 6 - 6: Models
     : 7 - 42: A base class for creating Pydantic models.
     : 8 - 11: Attributes:
     : 9 - 4859: | Name                          | Type            
     : 10 - 31: Source code in pydantic/main.py
     : 11 - 238: ### __init__ ¶  ``` __init__(**data: Any) -> None 
     : 12 - 164: ### model_config  class-attribute  ¶  ``` model_co
     : 13 - 350: ### model_fields  classmethod  ¶  ``` model_fields
       : 14 - 27: ### model_fieldsclassmethod
       : 15 - 46: ``` model_fields() -> dict[str, FieldInfo] ```
       : 16 - 65: A mapping of field names to their respective Field
       : 17 - 7: Warning
       : 18 - 159: Accessing this attribute from a model instance is 
       : 19 - 31: Source code in pydantic/main.py
     : 20 - 393: ### model_computed_fields  classmethod  ¶  ``` mod
       : 21 - 36: ### model_computed_fieldsclassmethod
       : 22 - 63: ``` model_computed_fields() -> dict[str, ComputedF
       : 23 - 82: A mapping of computed field names to their respect
       : 24 - 7: Warning
       : 25 - 159: Accessing this attribute from a model instance is 
       : 26 - 31: Source code in pydantic/main.py
     : 27 - 125: ### __pydantic_core_schema__  class-attribute  ¶  
     : 28 - 439: ### model_extra  property  ¶  ``` model_extra: dic
       : 29 - 23: ### model_extraproperty
       : 30 - 42: ``` model_extra: dict[str, Any] | None ```
       : 31 - 39: Get extra fields set during validation.
       : 32 - 8: Returns:
       : 33 - 314: | Type                  | Description             
     : 34 - 512: ### model_fields_set  property  ¶  ``` model_field
       : 35 - 28: ### model_fields_setproperty
       : 36 - 34: ``` model_fields_set: set[str] ```
       : 37 - 79: Returns the set of fields that have been explicitl
       : 38 - 8: Returns:
       : 39 - 350: | Type     | Description                          
     : 40 - 2200: ### model_construct  classmethod  ¶  ``` model_con
       : 41 - 30: ### model_constructclassmethod
       : 42 - 87: ``` model_construct(   _fields_set: set[str] | Non
       : 43 - 62: Creates a new instance of the Model class with val
       : 44 - 168: Creates a new model setting __dict__ and __pydanti
       : 45 - 4: Note
       : 46 - 516: model_construct() generally respects the model_con
       : 47 - 11: Parameters:
       : 48 - 1055: | Name        | Type            | Description     
       : 49 - 8: Returns:
       : 50 - 203: | Type   | Description                            
       : 51 - 31: Source code in pydantic/main.py
     : 52 - 1262: ### model_copy ¶  ``` model_copy(   *,   update: M
       : 53 - 14: ### model_copy
       : 54 - 98: ``` model_copy(   *,   update: Mapping[str, Any] |
       : 55 - 19: Usage Documentation
       : 56 - 10: model_copy
       : 57 - 28: Returns a copy of the model.
       : 58 - 4: Note
       : 59 - 190: The underlying instance's __dict__ attribute is co
       : 60 - 11: Parameters:
       : 61 - 727: | Name   | Type                     | Description 
       : 62 - 8: Returns:
       : 63 - 98: | Type   | Description         | |--------|-------
       : 64 - 31: Source code in pydantic/main.py
     : 65 - 4714: ### model_dump ¶  ``` model_dump(   *,   mode: Lit
       : 66 - 14: ### model_dump
       : 67 - 498: ``` model_dump(   *,   mode: Literal["json", "pyth
       : 68 - 19: Usage Documentation
       : 69 - 10: model_dump
       : 70 - 108: Generate a dictionary representation of the model,
       : 71 - 11: Parameters:
       : 72 - 3807: | Name             | Type                         
       : 73 - 8: Returns:
       : 74 - 188: | Type           | Description                    
       : 75 - 31: Source code in pydantic/main.py
     : 76 - 4240: ### model_dump_json ¶  ``` model_dump_json(   *,  
       : 77 - 19: ### model_dump_json
       : 78 - 499: ``` model_dump_json(   *,   indent: int | None = N
       : 79 - 19: Usage Documentation
       : 80 - 15: model_dump_json
       : 81 - 77: Generates a JSON representation of the model using
       : 82 - 11: Parameters:
       : 83 - 3374: | Name             | Type                         
       : 84 - 8: Returns:
       : 85 - 167: | Type   | Description                            
       : 86 - 31: Source code in pydantic/main.py
     : 87 - 1746: ### model_json_schema  classmethod  ¶  ``` model_j
       : 88 - 32: ### model_json_schemaclassmethod
       : 89 - 231: ``` model_json_schema(   by_alias: bool = True,   
       : 90 - 42: Generates a JSON schema for a model class.
       : 91 - 11: Parameters:
       : 92 - 1181: | Name             | Type                     | De
       : 93 - 8: Returns:
       : 94 - 191: | Type           | Description                    
       : 95 - 31: Source code in pydantic/main.py
     : 96 - 1531: ### model_parametrized_name  classmethod  ¶  ``` m
       : 97 - 38: ### model_parametrized_nameclassmethod
       : 98 - 73: ``` model_parametrized_name(   params: tuple[type[
       : 99 - 63: Compute the class name for parametrizations of gen
       : 100 - 87: This method can be overridden to achieve a custom 
       : 101 - 11: Parameters:
       : 102 - 641: | Name   | Type                  | Description    
       : 103 - 8: Returns:
       : 104 - 290: | Type   | Description                            
       : 105 - 7: Raises:
       : 106 - 257: | Type      | Description                         
       : 107 - 31: Source code in pydantic/main.py
     : 108 - 295: ### model_post_init ¶  ``` model_post_init(context
       : 109 - 19: ### model_post_init
       : 110 - 45: ``` model_post_init(context: Any) -> None ```
       : 111 - 192: Override this method to perform additional initial
       : 112 - 31: Source code in pydantic/main.py
     : 113 - 1771: ### model_rebuild  classmethod  ¶  ``` model_rebui
       : 114 - 28: ### model_rebuildclassmethod
       : 115 - 183: ``` model_rebuild(   *,   force: bool = False,   r
       : 116 - 54: Try to rebuild the pydantic-core schema for the mo
       : 117 - 173: This may be necessary when one of the annotations 
       : 118 - 11: Parameters:
       : 119 - 839: | Name                    | Type                  
       : 120 - 8: Returns:
       : 121 - 423: | Type        | Description                       
       : 122 - 31: Source code in pydantic/main.py
     : 123 - 1701: ### model_validate  classmethod  ¶  ``` model_vali
       : 124 - 29: ### model_validateclassmethod
       : 125 - 211: ``` model_validate(   obj: Any,   *,   strict: boo
       : 126 - 35: Validate a pydantic model instance.
       : 127 - 11: Parameters:
       : 128 - 1039: | Name            | Type        | Description     
       : 129 - 7: Raises:
       : 130 - 179: | Type            | Description                   
       : 131 - 8: Returns:
       : 132 - 128: | Type   | Description                   | |------
       : 133 - 31: Source code in pydantic/main.py
     : 134 - 1768: ### model_validate_json  classmethod  ¶  ``` model
       : 135 - 34: ### model_validate_jsonclassmethod
       : 136 - 203: ``` model_validate_json(   json_data: str | bytes 
       : 137 - 19: Usage Documentation
       : 138 - 12: JSON Parsing
       : 139 - 56: Validate the given JSON data against the Pydantic 
       : 140 - 11: Parameters:
       : 141 - 951: | Name      | Type                    | Descriptio
       : 142 - 8: Returns:
       : 143 - 128: | Type   | Description                   | |------
       : 144 - 7: Raises:
       : 145 - 281: | Type            | Description                   
       : 146 - 31: Source code in pydantic/main.py
     : 147 - 1344: ### model_validate_strings  classmethod  ¶  ``` mo
       : 148 - 37: ### model_validate_stringsclassmethod
       : 149 - 180: ``` model_validate_strings(   obj: Any,   *,   str
       : 150 - 70: Validate the given object with string data against
       : 151 - 11: Parameters:
       : 152 - 860: | Name     | Type        | Description            
       : 153 - 8: Returns:
       : 154 - 128: | Type   | Description                   | |------
       : 155 - 31: Source code in pydantic/main.py
   : 156 - 5098: ## pydantic.create_model ¶  ``` create_model(   mo
     : 157 - 24: ## pydantic.create_model
     : 158 - 365: ``` create_model(   model_name: str,   /,   *,   _
     : 159 - 390: ``` create_model(   model_name: str,   /,   *,   _
     : 160 - 419: ``` create_model(   model_name: str,   /,   *,   _
     : 161 - 19: Usage Documentation
     : 162 - 22: Dynamic Model Creation
     : 163 - 127: Dynamically creates and returns a new Pydantic mod
     : 164 - 11: Parameters:
     : 165 - 3289: | Name                | Type                      
     : 166 - 8: Returns:
     : 167 - 101: | Type         | Description    | |--------------|
     : 168 - 7: Raises:
     : 169 - 203: | Type              | Description                 
     : 170 - 31: Source code in pydantic/main.py
     : 171 - 25: Thanks for your feedback!
     : 172 - 25: Thanks for your feedback!