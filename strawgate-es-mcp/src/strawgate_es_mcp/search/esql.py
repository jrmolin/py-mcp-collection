from collections.abc import Awaitable, Callable

from fastmcp.tools import Tool

QUERY_ESQL_TIPS = '''
# ESQL Query Language Guide for Agents

## 1. Introduction to ESQL

ESQL (Elasticsearch Query Language) is a powerful, piped query language designed for exploring and analyzing data within Elasticsearch. It provides a user-friendly and intuitive syntax, making it accessible for various data processing tasks, from simple queries to complex data transformations and aggregations.

### What is ESQL?

ESQL is a domain-specific language tailored for Elasticsearch. It allows users to interact with their data using a syntax that is familiar to those with experience in other query languages, particularly SQL, but with a focus on the unique capabilities of Elasticsearch. The "piped" nature of ESQL means that commands are chained together using the pipe character (`|`), where the output of one command becomes the input for the next, enabling a clear and sequential flow of data processing.

### Why use ESQL?

*   **Simplicity and Readability**: ESQL's syntax is designed to be easy to read and write, reducing the learning curve for new users.
*   **Powerful Data Manipulation**: It offers a rich set of commands, functions, and operators for filtering, transforming, aggregating, and combining data.
*   **Integration with Elasticsearch**: ESQL is built specifically for Elasticsearch, allowing seamless interaction with indices, data streams, and various data types.
*   **Advanced Workflows**: Supports complex operations like data enrichment, joining data from multiple sources, and processing unstructured text.

### Basic Query Structure

An ESQL query always begins with a **source command**, which defines where the data originates (typically an Elasticsearch index or data stream). This is followed by an optional series of **processing commands**, each separated by a pipe character (`|`).

The general structure looks like this:

```esql
source-command
| processing-command1
| processing-command2
| ...
```

The result of an ESQL query is the table produced by the final processing command in the chain. For readability, it's common practice to place each processing command on a new line, though ESQL allows the entire query to be written on a single line.

**Example:**

```esql
FROM my_index
| WHERE status == "success"
| STATS count() BY user_id
| SORT count DESC
| LIMIT 10
```

This query:
1.  Retrieves data from `my_index`.
2.  Filters records where the `status` field is "success".
3.  Counts the number of successful events grouped by `user_id`.
4.  Sorts the results by the count in descending order.
5.  Limits the output to the top 10 results.

## 2. ESQL Syntax Reference

Understanding the fundamental syntax elements is crucial for writing effective ESQL queries.

### Identifiers

Identifiers refer to field names, aliases, or other named entities within an ESQL query. They generally follow standard naming conventions. However, if an identifier contains special characters (e.g., starts with a number, contains spaces, or other non-alphanumeric characters besides `_` or `@`), it must be quoted using backticks (`` ` ``).

**Examples:**

```esql
FROM my_index
| KEEP `1.field` // Quoted because it starts with a number
```

When referencing a function alias that itself uses a quoted identifier, the backticks of the quoted identifier need to be escaped with another backtick.

**Example:**

```esql
FROM index
| STATS COUNT(`1.field`)
| EVAL my_count = `COUNT(``1.field``)` // Escaping backticks for the alias
```

### Literals

ESQL supports various types of literals for representing constant values in queries.

#### String Literals

String literals are sequences of Unicode characters enclosed in double quotes (`"`).

```esql
FROM index
| WHERE first_name == "Georgi"
```

If a string literal itself contains double quotes, these must be escaped using a backslash (`\"`). For convenience, ESQL also supports triple-quotes (`"""`) as delimiters, which do not require escaping for internal double quotes.

```esql
ROW name = """Indiana "Indy" Jones"""
```

Special characters like carriage return (`\r`), line feed (`\n`), and tab (`\t`) can be included using their respective escape sequences.

#### Numerical Literals

Numerical literals can be integers or floating-point numbers, and can be expressed in decimal or scientific notation (using `e` or `E` for the exponent). They can start with a digit, a decimal point, or a negative sign.

```sql
1969    -- integer notation
3.14    -- decimal notation
.1234   -- decimal notation starting with decimal point
4E5     -- scientific notation (with exponent marker)
1.2e-3  -- scientific notation with decimal point
-.1e2   -- scientific notation starting with the negative sign
```

Integer literals are implicitly converted to `integer`, `long`, or `double` based on their value. Floating-point literals are implicitly converted to `double`. For explicit type conversion, ESQL provides dedicated type conversion functions.

#### Timespan Literals

Timespan literals represent intervals between datetime values. They combine a numeric value with a temporal unit (e.g., `1 day`, `5 hours`). They are not whitespace sensitive.

**Examples:**

*   `1day`
*   `1 day`
*   `1       day`

Timespan literals are used with functions like `BUCKET` and `DATE_TRUNC`, and with arithmetic operators (`+`, `-`) for date calculations.

### Comments

ESQL supports C++ style comments:

*   **Single-line comments**: Start with `//`
*   **Block comments**: Enclosed between `/*` and `*/`

**Examples:**

```esql
// Query the employees index
FROM employees
| WHERE height > 2
```

```esql
FROM /* Query the employees index */ employees
| WHERE height > 2
```

```esql
FROM employees
/* Query the
 * employees
 * index */
| WHERE height > 2
```

### Function Named Parameters

Some ESQL functions, like `match()`, accept named parameters to provide additional options. These are specified as JSON objects with `option_name: option_value` pairs.

**Syntax:**

```
{"option_name": option_value, "another_option_name": another_value}
```

Valid value types for named parameters include strings, numbers, and booleans.

**Example using `match()`:**

```esql
FROM library
| WHERE match(author, "Frank Herbert", {"minimum_should_match": 2, "operator": "AND"})
| LIMIT 5
```

You can also use query parameters within function named parameters, allowing for dynamic query construction.

```esql
POST /_query
{
"query": """
FROM library
| EVAL year = DATE_EXTRACT("year", release_date)
| WHERE page_count > ? AND match(author, ?, {"minimum_should_match": ?})
| LIMIT 5
""",
"params": [300, "Frank Herbert", 2]
}
```

## 3. ESQL Commands

ESQL commands are the building blocks of queries, allowing you to retrieve, filter, transform, and aggregate data. Commands are categorized into source commands and processing commands.

### Source Commands

A source command is always the first command in an ESQL query. It produces the initial table of data, typically from Elasticsearch indices or data streams.

*   **`FROM`**: The most common source command, used to specify the index or data stream from which to retrieve data.

    ```esql
    FROM my_logs
    ```

### Processing Commands

Processing commands take an input table (from a source command or a previous processing command) and modify it by adding, removing, or changing rows and columns.

*   **`WHERE`**: Filters rows based on a specified condition.

    ```esql
    FROM logs
    | WHERE status == 200 AND bytes > 1000
    ```

*   **`EVAL`**: Creates new columns or modifies existing ones using expressions.

    ```esql
    FROM sales
    | EVAL total_price = quantity * price
    ```

*   **`KEEP`**: Selects specific columns to retain in the output, discarding all others.

    ```esql
    FROM users
    | KEEP user_id, username, email
    ```

*   **`DROP`**: Removes specified columns from the output.

    ```esql
    FROM logs
    | DROP sensitive_data, temp_field
    ```

*   **`RENAME`**: Renames one or more columns.

    ```esql
    FROM products
    | RENAME item_name AS product_name
    ```

*   **`SORT`**: Orders the rows based on one or more columns, in ascending or descending order.

    ```esql
    FROM events
    | SORT timestamp DESC, severity ASC
    ```

*   **`LIMIT`**: Restricts the number of rows returned by the query.

    ```esql
    FROM articles
    | LIMIT 5
    ```

*   **`STATS`**: Performs aggregations on data, often used with `BY` to group results.

    ```esql
    FROM orders
    | STATS total_sales = SUM(price) BY region
    ```

### `DISSECT` and `GROK` for Unstructured Data

Many log messages and other data sources contain unstructured text that needs to be parsed to extract meaningful information. ESQL provides `DISSECT` and `GROK` commands for this purpose.

#### `DISSECT` vs `GROK`

*   **`DISSECT`**: Works by breaking up a string using a delimiter-based pattern. It's faster and more efficient when data is reliably structured and repeated (e.g., fixed-width fields or consistent delimiters).
*   **`GROK`**: Uses regular expressions for pattern matching. It's more powerful and flexible, suitable for data with varying structures or when complex pattern matching is required, but generally slower than `DISSECT`.

You can use both `DISSECT` and `GROK` together for hybrid scenarios, where `DISSECT` handles the consistently structured parts and `GROK` processes the more variable sections.

#### `DISSECT` Patterns and Modifiers

The `DISSECT` command matches a string against a delimiter-based pattern and extracts specified keys as columns.

**Example:**

```esql
ROW a = "2023-01-23T12:15:00.000Z - some text - 127.0.0.1"
| DISSECT a """%{date} - %{msg} - %{ip}"""
| KEEP date, msg, ip
```

This would produce:

| date:keyword             | msg:keyword | ip:keyword  |
| :----------------------- | :---------- | :---------- |
| 2023-01-23T12:15:00.000Z | some text   | 127.0.0.1   |

By default, `DISSECT` outputs keyword string data types. You can use type conversion functions to change them.

**Key Modifiers:**

*   **`->` (Skip right padding)**: Allows for repetition of characters after a key, useful for handling variable whitespace.
    ```esql
    ROW message="1998-08-10T17:15:42          WARN"
    | DISSECT message """%{ts->} %{level}"""
    ```
*   **`+` (Append)**: Appends two or more fields together.
    ```esql
    ROW message="john jacob jingleheimer schmidt"
    | DISSECT message """%{+name} %{+name} %{+name} %{+name}""" APPEND_SEPARATOR=" "
    ```
*   **`+` with `/n` (Append with order)**: Appends fields in a specified order.
    ```esql
    ROW message="john jacob jingleheimer schmidt"
    | DISSECT message """%{+name/2} %{+name/4} %{+name/3} %{+name/1}""" APPEND_SEPARATOR=","
    ```
*   **`?` (Named skip key)**: Matches a value but excludes it from the output, similar to an empty key (`%{}`).
    ```esql
    ROW message="1.2.3.4 - - 30/Apr/1998:22:00:52 +0000"
    | DISSECT message """%{clientip} %{?ident} %{?auth} %{@timestamp}"""
    ```

#### `GROK` Patterns and Regular Expressions

The `GROK` command matches a string against a pattern based on regular expressions.

**Syntax:** `%{SYNTAX:SEMANTIC}`

*   **`SYNTAX`**: The name of a predefined pattern (e.g., `IP`, `TIMESTAMP_ISO8601`, `GREEDYDATA`).
*   **`SEMANTIC`**: The name you assign to the extracted piece of text, which becomes a new column.

**Example:**

```esql
ROW a = "1.2.3.4 [2023-01-23T12:15:00.000Z] Connected"
| GROK a """%{IP:ip} \\[%{TIMESTAMP_ISO8601:@timestamp}\\] %{GREEDYDATA:status}"""
```

This would produce:

| @timestamp:keyword       | ip:keyword  | status:keyword |
| :----------------------- | :---------- | :------------- |
| 2023-01-23T12:15:00.000Z | 1.2.3.4     | Connected      |

**Important Note on Escaping:** When using `GROK` patterns, special regex characters (like `[`, `]`) need to be escaped with a backslash (`\\`). If your ESQL query uses single quotes for the string literal, the backslash itself needs to be escaped (`\\`). Using triple quotes (`"""`) for `GROK` patterns is generally more convenient as it avoids the need to escape backslashes.

You can also specify a target data type for the semantic by appending `:type` (e.g., `%{NUMBER:num:int}`). For other type conversions, use ESQL's type conversion functions.

### `ENRICH` for Combining Data

The `ENRICH` processing command combines data from your ESQL query results with data from Elasticsearch enrich indices. It's ideal for adding context to your data at query time, especially when the enrichment data doesn't change frequently.

**Use Cases:**

*   Identifying web services or vendors based on IP addresses.
*   Adding product information to orders.
*   Supplementing contact information.

#### How `ENRICH` Works

`ENRICH` adds new columns to a table using data from Elasticsearch enrich indices. It relies on:

1.  **Enrich Policy**: A configuration that defines source indices, policy type (e.g., `match`, `geo_match`, `range`), a match field, and enrich fields.
2.  **Source Index**: Regular Elasticsearch indices storing the data used for enrichment.
3.  **Enrich Index**: A special, read-only system index (`.enrich-*`) created by executing an enrich policy. This index is optimized for fast retrieval during enrichment.

#### Setting Up and Using `ENRICH`

1.  **Add Enrich Data**: Populate one or more source indices with the data you want to use for enrichment.
2.  **Create an Enrich Policy**: Define the policy using the Elasticsearch API or Kibana. Note that once created, an enrich policy cannot be updated or changed directly; you must create a new one.
3.  **Execute the Enrich Policy**: This step creates the optimized enrich index from your source indices.
4.  **Use the `ENRICH` Command**: Apply the `ENRICH` command in your ESQL query, specifying the enrich policy and the field to match on.

**Example:**

```esql
ROW language_code = "1"
| ENRICH languages_policy
```

This would add columns from `languages_policy` based on `language_code`.

You can specify a different column to match on using `ON <column-name>`:

```esql
ROW a = "1"
| ENRICH languages_policy ON a
```

You can also explicitly select which enrich fields to add using `WITH <field1>, <field2>, ...` and rename them using `WITH new_name=<field1>`.

#### Enrich Policy Types and Limitations

`ENRICH` supports three policy types:

*   **`geo_match`**: Matches based on `geo_shape` queries.
*   **`match`**: Matches based on `term` queries (exact values).
*   **`range`**: Matches a number, date, or IP address to a range.

**Limitations:**

*   Enrichment data should not change frequently.
*   Multiple matches are combined into multi-values.
*   Limited to predefined match fields.
*   No fine-grained security restrictions on enrich policies.
*   `geo_match` only supports `intersects`.
*   Match fields must have compatible data types.
*   Can impact query speed due to operations performed.

### `LOOKUP JOIN` for Joining Data

The `LOOKUP JOIN` processing command combines data from your ESQL query results with matching records from a specified lookup index. It's similar to a left join in SQL, adding fields from the lookup index as new columns.

**Use Cases:**

*   Retrieving environment or ownership details for hosts.
*   Correlating source IPs with known malicious addresses.
*   Tagging logs with team or escalation information.

#### How `LOOKUP JOIN` Works

`LOOKUP JOIN` takes an input table and a `lookup_index` (which must have `index.mode: lookup` set). It joins rows based on a specified `field_name`.

**Syntax:**

```esql
LOOKUP JOIN <lookup_index> ON <field_name>
```

If no rows match in the lookup index, the original row is retained, and `null` values are added for the new columns. If multiple rows match, `LOOKUP JOIN` adds one row per match, effectively duplicating the original row for each match.

**Example:**

```esql
FROM firewall_logs
| LOOKUP JOIN threat_list ON source.ip
| WHERE threat_level IS NOT NULL
| SORT timestamp
| KEEP source.ip, action, threat_type, threat_level
| LIMIT 10
```

This query joins `firewall_logs` with `threat_list` on `source.ip` to identify threats.

#### `LOOKUP JOIN` vs `ENRICH`

| Feature                 | `LOOKUP JOIN`                                   | `ENRICH`                                          |
| :---------------------- | :---------------------------------------------- | :------------------------------------------------ |
| Data Change Frequency   | Your enrichment data changes frequently         | Enrichment data doesn't change frequently         |
| Index-time Processing   | Avoid index-time processing                     | Accept index-time overhead                        |
| Multiple Matches        | SQL-like behavior (multiple rows per match)     | Multiple matches combined into multi-values       |
| Match Fields            | Match on any field in a lookup index            | Limited to predefined match fields                |
| Security                | Uses document or field level security           | No fine-grained security                          |
| Index Restriction       | Restrict users to specific lookup indices       | No restrictions                                   |
| Range/Spatial Matching  | Does not support range or spatial relations     | Supports range and spatial relations              |

#### Limitations

*   Lookup indices must have `index.mode: lookup`.
*   Join key and join field must have compatible data types.
*   Only equality matching is supported.
*   Only a single match field and a single index can be used (no wildcards, aliases, datemath, datastreams).
*   Cross-cluster search is unsupported.
*   Output order is not guaranteed; use `SORT` after `LOOKUP JOIN` if order is important.
*   Name collisions: New columns from the lookup index override existing ones. Use `RENAME` or `EVAL` before the join to prevent this.
*   Circuit breaking: Queries may circuit break if too many matching documents or very large documents are found in the lookup index.

## 4. ESQL Functions and Operators

ESQL provides a rich set of functions and operators for data manipulation and analysis.

### Functions Overview

Functions in ESQL are categorized by their purpose:

*   **Aggregate Functions**: Perform calculations on a set of values and return a single value (e.g., `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`).
*   **Grouping Functions**: Used to group data, often in conjunction with `STATS` (e.g., `BUCKET`).
*   **Conditional Functions and Expressions**: Allow for conditional logic (e.g., `CASE`, `IF`).
*   **Date and Time Functions**: Manipulate and extract information from date and time values (e.g., `DATE_TRUNC`, `DATE_DIFF`, `NOW`).
*   **IP Functions**: Work with IP addresses (e.g., `CIDR_MATCH`, `IP_PREFIX`).
*   **Math Functions**: Perform mathematical operations (e.g., `ABS`, `ROUND`, `LOG`).
*   **Search Functions**: Used for full-text search capabilities (e.g., `MATCH`, `KQL`, `MULTI_MATCH`).
*   **Spatial Functions**: Work with geographical data (e.g., `ST_CONTAINS`, `ST_DISTANCE`).
*   **String Functions**: Manipulate string values (e.g., `CONCAT`, `LENGTH`, `SUBSTRING`, `TO_UPPER`).
*   **Type Conversion Functions**: Convert values from one data type to another (e.g., `TO_INT`, `TO_STRING`, `TO_DATETIME`).
*   **Multi-value Functions**: Specifically designed to handle fields that contain multiple values (e.g., `MV_AVG`, `MV_COUNT`, `MV_MIN`).

### Operators Overview

Operators perform operations on one or more values.

*   **Binary Operators**: Operate on two operands (e.g., `+`, `-`, `*`, `/`, `==`, `!=`, `>`, `<`, `>=`, `<=`, `AND`, `OR`).
*   **Unary Operators**: Operate on a single operand (e.g., `NOT`, `-` for negation).
*   **`IN` Operator**: Checks if a value is present in a list of values.

    ```esql
    FROM logs
    | WHERE event_type IN ("login", "logout", "error")
    ```

## 5. ESQL Data Handling

ESQL manages various data types and special fields to provide comprehensive data analysis capabilities.

### Types and Fields

ESQL supports a range of data types, including numeric, string, boolean, date, IP, and version. Understanding how ESQL handles these types is crucial for accurate querying.

### Implicit Casting

Implicit casting allows ESQL to automatically convert string literals to the target data type in certain contexts (e.g., `date`, `date_period`, `time_duration`, `ip`, `version`). This simplifies queries by reducing the need for explicit type conversion functions.

**Example:**

Instead of:
```esql
FROM employees
| EVAL dd_ns1=date_diff("day", to_datetime("2023-12-02T11:00:00.00Z"), birth_date)
```

You can write:
```esql
FROM employees
| EVAL dd_ns1=date_diff("day", "2023-12-02T11:00:00.00Z", birth_date)
```

Implicit casting is supported for scalar functions, operators, and grouping functions for certain data types.

### Time Spans

Time spans represent intervals between two datetime values and are crucial for time-based analysis. ESQL supports two main types:

*   **`DATE_PERIOD`**: Specifies intervals in years, quarters, months, weeks, and days.
*   **`TIME_DURATION`**: Specifies intervals in hours, minutes, seconds, and milliseconds.

A time span requires an integer value and a temporal unit (e.g., `1 week`, `5 minutes`).

**Supported Temporal Units:**

| Temporal Units | Valid Abbreviations |
| :------------- | :------------------ |
| year           | y, yr, years        |
| quarter        | q, quarters         |
| month          | mo, months          |
| week           | w, weeks            |
| day            | d, days             |
| hour           | h, hours            |
| minute         | min, minutes        |
| second         | s, sec, seconds     |
| millisecond    | ms, milliseconds    |

Time spans are used with grouping functions (`BUCKET`), scalar functions (`DATE_TRUNC`), and arithmetic operators (`+`, `-`). You can convert strings to time spans using `TO_DATEPERIOD`, `TO_TIMEDURATION`, or cast operators (`::DATE_PERIOD`, `::TIME_DURATION`).

**Example with `BUCKET`:**

```esql
FROM employees
| WHERE hire_date >= "1985-01-01T00:00:00Z" AND hire_date < "1986-01-01T00:00:00Z"
| STATS hires_per_week = COUNT(*) BY week = BUCKET(hire_date, 1 week)
| SORT week
```

### Metadata Fields

ESQL can access Elasticsearch document metadata fields, which provide information about the document itself rather than its content. Supported metadata fields include:

*   **`_index`**: The index to which the document belongs (keyword type).
*   **`_id`**: The source document's ID (keyword type).
*   **`_version`**: The source document's version (long type).
*   **`_ignored`**: Ignored source document fields (keyword type).
*   **`_score`**: The final score assigned to each row matching a query (when enabled).

To access these fields, the `FROM` source command needs to be provided with a `METADATA` directive:

```esql
FROM index METADATA _index, _id
```

Once enabled, metadata fields behave like other index fields and can be used in processing commands. However, after an aggregation, a metadata field is no longer accessible unless it was used as a grouping field.

### Multivalued Fields

Multivalued fields are fields that can contain an array of values. ESQL can read from these fields, and they are returned as JSON arrays.

**Important Considerations:**

*   **Order**: The relative order of values in a multivalued field is undefined and should not be relied upon.
*   **Duplicates**: Some field types (like `keyword`) remove duplicate values on write, while others (like `long`) do not. ESQL reflects this behavior.
*   **`null` values**: `null` values in a list are generally not preserved at the storage layer.
*   **Functions**: Unless otherwise documented, functions applied directly to a multivalued field will return `null`. To work around this, convert the multivalued field to a single value using multi-value functions (e.g., `MV_AVG`, `MV_MIN`, `MV_SUM`) before applying other functions.

**Example of `MV_MIN` to convert to single value:**

```esql
FROM mv
| EVAL b=MV_MIN(b)
| EVAL b + 2, a + b
| LIMIT 4
```

## 6. ESQL Examples

Here are some practical examples demonstrating how to use ESQL for various tasks.

### Aggregating and Enriching Windows Event Logs

This example shows how to filter, aggregate, enrich, and format Windows event logs.

```esql
FROM logs-*
| WHERE event.code IS NOT NULL
| STATS event_code_count = COUNT(event.code) BY event.code,host.name
| ENRICH win_events ON event.code WITH event_description
| WHERE event_description IS NOT NULL and host.name IS NOT NULL
| RENAME event_description AS event.description
| SORT event_code_count DESC
| KEEP event_code_count,event.code,host.name,event.description
```

**Explanation:**
*   **`FROM logs-*`**: Queries logs from indices matching the pattern "logs-*".
*   **`WHERE event.code IS NOT NULL`**: Filters events where the `event.code` field is not null.
*   **`STATS event_code_count = COUNT(event.code) BY event.code,host.name`**: Aggregates the count of events by `event.code` and `host.name`.
*   **`ENRICH win_events ON event.code WITH event_description`**: Enriches the events with additional information from the `win_events` policy using `event.code` as the match field, and specifically adds the `event_description` field.
*   **`WHERE event_description IS NOT NULL and host.name IS NOT NULL`**: Filters out events where `event_description` or `host.name` is null.
*   **`RENAME event_description AS event.description`**: Renames `event_description` to `event.description` for clarity.
*   **`SORT event_code_count DESC`**: Sorts the result by `event_code_count` in descending order.
*   **`KEEP event_code_count,event.code,host.name,event.description`**: Keeps only the specified fields.

### Summing Outbound Traffic from a Process `curl.exe`

This query calculates the total outbound bytes for a specific process and converts it to kilobytes.

```esql
FROM logs-endpoint
| WHERE process.name == "curl.exe"
| STATS bytes = SUM(destination.bytes) BY destination.address
| EVAL kb =  bytes/1024
| SORT kb DESC
| LIMIT 10
| KEEP kb,destination.address
```

**Explanation:**
*   **`FROM logs-endpoint`**: Queries logs from the "logs-endpoint" source.
*   **`WHERE process.name == "curl.exe"`**: Filters events where the `process.name` field is "curl.exe".
*   **`STATS bytes = SUM(destination.bytes) BY destination.address`**: Calculates the sum of bytes sent to destination addresses.
*   **`EVAL kb = bytes/1024`**: Creates a new field `kb` by converting bytes to kilobytes.
*   **`SORT kb DESC`**: Sorts the results by `kb` in descending order.
*   **`LIMIT 10`**: Limits the output to the top 10 results.
*   **`KEEP kb,destination.address`**: Keeps only the `kb` and `destination.address` fields.

### Manipulating DNS Logs to Find a High Number of Unique DNS Queries per Registered Domain

This example demonstrates using `GROK` and `COUNT_DISTINCT` to analyze DNS query patterns.

```esql
FROM logs-*
| GROK dns.question.name "%{DATA}\\.%{GREEDYDATA:dns.question.registered_domain:string}"
| STATS unique_queries = COUNT_DISTINCT(dns.question.name) BY dns.question.registered_domain, process.name
| WHERE unique_queries > 10
| SORT unique_queries DESC
| RENAME unique_queries AS `Unique Queries`, dns.question.registered_domain AS `Registered Domain`, process.name AS `Process`
```

**Explanation:**
*   **`FROM logs-*`**: Queries logs from indices matching "logs-*".
*   **`GROK dns.question.name "%{DATA}\\.%{GREEDYDATA:dns.question.registered_domain:string}"`**: Uses `GROK` to extract the registered domain from `dns.question.name`.
*   **`STATS unique_queries = COUNT_DISTINCT(dns.question.name) BY dns.question.registered_domain, process.name`**: Calculates the count of unique DNS queries per registered domain and process name.
*   **`WHERE unique_queries > 10`**: Filters results where `unique_queries` are greater than 10.
*   **`SORT unique_queries DESC`**: Sorts the results by `unique_queries` in descending order.
*   **`RENAME ...`**: Renames fields for better readability in the output.

### Identifying High-Numbers of Outbound User Connections

This query identifies users with a high number of outbound connections, excluding private IP ranges, and enriches the data with LDAP information.

```esql
FROM logs-*
| WHERE NOT CIDR_MATCH(destination.ip, "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16")
| STATS destcount = COUNT(destination.ip) BY user.name, host.name
| ENRICH ldap_lookup_new ON user.name
| WHERE group.name IS NOT NULL
| EVAL follow_up = CASE(destcount >= 100, "true","false")
| SORT destcount DESC
| KEEP destcount, host.name, user.name, group.name, follow_up
```

**Explanation:**
*   **`FROM logs-*`**: Queries logs from indices matching "logs-*".
*   **`WHERE NOT CIDR_MATCH(...)`**: Filters out events where the destination IP address falls within specified private IP ranges.
*   **`STATS destcount = COUNT(destination.ip) BY user.name, host.name`**: Calculates the count of unique destination IPs by `user.name` and `host.name`.
*   **`ENRICH ldap_lookup_new ON user.name`**: Enriches the `user.name` field with LDAP group information using the `ldap_lookup_new` policy.
*   **`WHERE group.name IS NOT NULL`**: Filters out results where `group.name` is not null.
*   **`EVAL follow_up = CASE(...)`**: Uses a `CASE` statement to create a `follow_up` field, indicating if `destcount` is 100 or more.
*   **`SORT destcount DESC`**: Sorts the results by `destcount` in descending order.
*   **`KEEP ...`**: Keeps selected fields for the final output.
'''  # noqa: E501

def esql_query_tips() -> str:
    """Helpful tips for constructing Elasticsearch ESQL queries."""
    return QUERY_ESQL_TIPS

