; (comment) @comment

; Module docstring
(
  (module
    . (expression_statement (string (string_content) @doc)))
)

; Class docstring
(class_definition
  body: (block . (expression_statement (string (string_content) @doc))))

; Function/method docstring
(function_definition
  body: (block . (expression_statement (string (string_content) @doc))))

; Attribute docstring
((expression_statement (assignment)) . (expression_statement (string (string_content) @doc)))