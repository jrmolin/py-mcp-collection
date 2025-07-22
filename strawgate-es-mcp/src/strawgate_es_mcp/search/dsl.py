import json
from collections.abc import Awaitable, Callable
from typing import Any

from elasticsearch import AsyncElasticsearch

QUERY_DSL_TIPS = """
# Query DSL Guide for Agents

This guide provides a comprehensive overview of Elasticsearch's Query Domain Specific Language (DSL), designed to help agents construct effective and efficient queries for various search tasks.

## 1. Introduction to Query DSL

Elasticsearch's Query DSL is a powerful, JSON-based language used to define search queries. It functions as an Abstract Syntax Tree (AST) of queries, composed of two primary types of clauses:

*   **Leaf Query Clauses**: These clauses look for a specific value in a particular field. Examples include `match`, `term`, or `range` queries. They can be used independently.
*   **Compound Query Clauses**: These clauses wrap other leaf or compound queries to combine multiple queries logically (e.g., `bool`, `dis_max`) or to alter their behavior (e.g., `constant_score`).

Query clauses behave differently depending on whether they are used in a **query context** or a **filter context**.

## 2. Query Context vs. Filter Context

Understanding the distinction between query and filter contexts is crucial for optimizing search performance and relevance.

*   **Query Context**: In this context, a query clause determines *how well* a document matches the query. It calculates a **relevance score** (`_score`) for each matching document. Query context is typically used when you want to influence the ranking of search results.
    *   **Characteristics**: Calculates relevance scores, not cached by default, consumes more CPU.
    *   **Use Cases**: Full-text search, queries where result order matters.
    *   **Example**: A `match` query in the main `query` block.

*   **Filter Context**: In this context, a query clause answers a binary "yes" or "no" question: "Does this document match this query clause?" It does **not** calculate a relevance score. Filters are highly efficient and are automatically cached by Elasticsearch, making them ideal for frequently used criteria.
    *   **Characteristics**: No relevance score calculation, automatically cached, faster execution, resource-efficient.
    *   **Use Cases**: Filtering structured data (numbers, dates, booleans, keywords), implementing "must have" or "must not have" conditions.
    *   **Example**: A `term` or `range` query within a `bool` query's `filter` or `must_not` clauses.

**Example of Query and Filter Contexts:**

```json
GET /_search
{
  "query": {
    "bool": {
      "must": [
        { "match": { "title":   "Search"        }},  // Query context: affects score
        { "match": { "content": "Elasticsearch" }}  // Query context: affects score
      ],
      "filter": [
        { "term":  { "status": "published" }},     // Filter context: no score, cached
        { "range": { "publish_date": { "gte": "2015-01-01" }}} // Filter context: no score, cached
      ]
    }
  }
}
```

## 3. Query Types

Elasticsearch offers a rich set of query types, categorized by their primary function.

### 3.1. Full-Text Queries

These queries are designed for searching analyzed text fields, such as the body of an email or an article. The query string is processed using the same analyzer applied to the field during indexing.

*   **`match` query**: The standard query for full-text search, supporting fuzzy matching, phrases, and proximity.
    ```json
    { "match": { "message": "this is a test" } }
    ```
*   **`multi_match` query**: Performs a `match` query across multiple fields.
    ```json
    { "multi_match": { "query": "Will Smith", "fields": ["first_name", "last_name"] } }
    ```
    *   **Types**: `best_fields` (default, best score from any field), `most_fields` (combines scores from all fields), `cross_fields` (term-centric, good for structured names), `phrase`, `phrase_prefix`, `bool_prefix`.
*   **`combined_fields` query**: Searches multiple text fields as if they were one combined field, with principled scoring. Requires fields to have the same analyzer.
    ```json
    { "combined_fields": { "query": "database systems", "fields": ["title", "abstract", "body"] } }
    ```
*   **`query_string` query**: Supports a compact Lucene query string syntax for complex queries with operators (AND, OR, NOT), wildcards, and multi-field search. Strict syntax, throws errors on invalid input.
    ```json
    { "query_string": { "query": "(new york city) OR (big apple)", "default_field": "content" } }
    ```
*   **`simple_query_string` query**: A simpler, more robust version of `query_string` suitable for direct user input. Ignores invalid syntax.
    ```json
    { "simple_query_string": { "query": "\"fried eggs\" +(eggplant | potato) -frittata", "fields": ["title^5", "body"] } }
    ```
*   **`intervals` query**: Offers fine-grained control over the ordering and proximity of matching terms.
    ```json
    { "intervals": { "my_text": { "all_of": { "ordered": true, "intervals": [{ "match": { "query": "my favorite food" } }, { "match": { "query": "cold porridge" } }] } } } }
    ```
*   **`match_phrase` query**: Matches exact phrases or word proximity.
    ```json
    { "match_phrase": { "message": "this is a test" } }
    ```
*   **`match_phrase_prefix` query**: Like `match_phrase`, but the last word is treated as a prefix for wildcard search.
    ```json
    { "match_phrase_prefix": { "message": "quick brown f" } }
    ```
*   **`match_bool_prefix` query**: Analyzes input and constructs a `bool` query where each term (except the last) is a `term` query, and the last is a `prefix` query.
    ```json
    { "match_bool_prefix": { "message": "quick brown f" } }
    ```

### 3.2. Term-Level Queries

These queries are used for finding documents based on precise values in structured data (e.g., numbers, dates, keywords). They do not analyze search terms.

*   **`term` query**: Returns documents containing an **exact** term. Avoid for `text` fields.
    ```json
    { "term": { "user.id": "kimchy" } }
    ```
*   **`terms` query**: Returns documents containing one or more **exact** terms from a list.
    ```json
    { "terms": { "user.id": ["kimchy", "elkbee"] } }
    ```
*   **`terms_set` query**: Similar to `terms`, but allows specifying a minimum number of matching terms required.
    ```json
    { "terms_set": { "programming_languages": { "terms": ["c++", "java", "php"], "minimum_should_match_field": "required_matches" } } }
    ```
*   **`exists` query**: Returns documents where a field contains any indexed value (is not null or empty array).
    ```json
    { "exists": { "field": "user" } }
    ```
*   **`prefix` query**: Returns documents where a field contains terms starting with a specific prefix.
    ```json
    { "prefix": { "user.id": "ki" } }
    ```
*   **`wildcard` query**: Returns documents where a field contains terms matching a wildcard pattern (`?` for single char, `*` for zero or more chars).
    ```json
    { "wildcard": { "user.id": "ki*y" } }
    ```
*   **`regexp` query**: Returns documents where a field contains terms matching a regular expression.
    ```json
    { "regexp": { "user.id": "k.*y" } }
    ```
*   **`fuzzy` query**: Returns documents with terms similar to the search term, based on Levenshtein edit distance.
    ```json
    { "fuzzy": { "user.id": { "value": "ki", "fuzziness": "AUTO" } } }
    ```
*   **`ids` query**: Returns documents based on their `_id` field.
    ```json
    { "ids": { "values": ["1", "4", "100"] } }
    ```
*   **`range` query**: Returns documents where a field's value falls within a specified range (`gt`, `gte`, `lt`, `lte`).
    ```json
    { "range": { "age": { "gte": 10, "lte": 20 } } }
    ```

### 3.3. Compound Queries

These queries combine other queries to form more complex logical conditions or modify their behavior.

*   **`bool` query**: The most common compound query, combining multiple clauses with `must`, `should`, `must_not`, or `filter`.
    *   `must`: Clauses must match, contribute to score. (Logical AND)
    *   `should`: Clauses should match, contribute to score. (Logical OR)
    *   `filter`: Clauses must match, do not contribute to score, are cached. (Logical AND, filter context)
    *   `must_not`: Clauses must not match, do not contribute to score, are cached. (Logical NOT, filter context)
    ```json
    {
      "bool": {
        "must": { "term": { "user.id": "kimchy" } },
        "filter": { "term": { "tags": "production" } },
        "must_not": { "range": { "age": { "gte": 10, "lte": 20 } } },
        "should": [ { "term": { "tags": "env1" } }, { "term": { "tags": "deployed" } } ]
      }
    }
    ```
*   **`boosting` query**: Returns documents matching a `positive` query, but reduces the score of documents that also match a `negative` query.
    ```json
    { "boosting": { "positive": { "term": { "text": "apple" } }, "negative": { "term": { "text": "pie" } }, "negative_boost": 0.5 } }
    ```
*   **`constant_score` query**: Wraps another query and executes it in filter context, assigning a constant `_score` to all matching documents.
    ```json
    { "constant_score": { "filter": { "term": { "user.id": "kimchy" } }, "boost": 1.2 } }
    ```
*   **`dis_max` query**: Accepts multiple queries and returns documents matching any of them, using the highest score from any matching clause.
    ```json
    { "dis_max": { "queries": [{ "term": { "title": "Quick pets" } }, { "term": { "body": "Quick pets" } }], "tie_breaker": 0.7 } }
    ```
*   **`function_score` query**: Modifies the scores returned by the main query using various functions (e.g., `script_score`, `random_score`, `field_value_factor`, decay functions).
    ```json
    { "function_score": { "query": { "match_all": {} }, "random_score": {}, "boost_mode": "multiply" } }
    ```

### 3.4. Joining Queries

These queries handle relationships between documents, particularly in parent-child or nested document structures.

*   **`nested` query**: Searches nested field objects as if they were separate documents. Returns the root parent document if a nested object matches.
    ```json
    { "nested": { "path": "obj1", "query": { "bool": { "must": [{ "match": { "obj1.name": "blue" } }] } } } }
    ```
*   **`has_child` query**: Returns parent documents whose child documents match a provided query. Can be slow.
    ```json
    { "has_child": { "type": "child", "query": { "match_all": {} } } }
    ```
*   **`has_parent` query**: Returns child documents whose parent document matches a provided query. Can be slow.
    ```json
    { "has_parent": { "parent_type": "parent", "query": { "term": { "tag": "Elasticsearch" } } } }
    ```
*   **`parent_id` query**: Returns child documents joined to a specific parent document by ID.
    ```json
    { "parent_id": { "type": "my-child", "id": "1" } }
    ```

### 3.5. Geo Queries

These queries are used for searching geographical data, including `geo_point` (lat/lon pairs) and `geo_shape` (points, lines, polygons).

*   **`geo_bounding_box` query**: Finds documents with geo values intersecting a specified rectangle.
    ```json
    { "geo_bounding_box": { "pin.location": { "top_left": { "lat": 40.73, "lon": -74.1 }, "bottom_right": { "lat": 40.01, "lon": -71.12 } } } }
    ```
*   **`geo_distance` query**: Finds documents with geo values within a given distance of a central point.
    ```json
    { "geo_distance": { "distance": "200km", "pin.location": { "lat": 40, "lon": -70 } } }
    ```
*   **`geo_grid` query**: Finds documents with geo values intersecting a grid cell (geohash, geotile, geohex).
    ```json
    { "geo_grid": { "location": { "geohash": "u0" } } }
    ```
*   **`geo_polygon` query**: Finds documents with geo values intersecting a specified polygon. (Deprecated, use `geo_shape` instead).
    ```json
    { "geo_polygon": { "person.location": { "points": [{ "lat": 40, "lon": -70 }, { "lat": 30, "lon": -80 }] } } }
    ```
*   **`geo_shape` query**: Filters documents based on their geo_shape or geo_point field's relationship to a query shape (intersects, disjoint, within, contains).
    ```json
    { "geo_shape": { "location": { "shape": { "type": "envelope", "coordinates": [[13.0, 53.0], [14.0, 52.0]] }, "relation": "within" } } }
    ```

### 3.6. Shape Queries

These queries work with arbitrary two-dimensional geometries (non-geospatial), using `point` (x/y pairs) and `shape` fields.

*   **`shape` query**: Finds documents with shapes or points that intersect, are contained by, are within, or do not intersect with the specified shape.
    ```json
    { "shape": { "geometry": { "shape": { "type": "envelope", "coordinates": [[1355.0, 5355.0], [1400.0, 5200.0]] }, "relation": "within" } } }
    ```

### 3.7. Span Queries

Low-level positional queries providing expert control over the order and proximity of terms. Cannot be mixed with non-span queries (except `span_multi`).

*   **`span_containing` query**: Returns matches which enclose another span query.
*   **`span_field_masking` query**: Allows span queries to participate in composite single-field span queries by "lying" about their search field. Useful for multi-fields with different analyzers.
*   **`span_first` query**: Matches spans near the beginning of a field.
*   **`span_multi` query**: Wraps a multi-term query (`term`, `range`, `prefix`, `wildcard`, `regexp`, `fuzzy`) as a span query.
*   **`span_near` query**: Matches spans which are near one another, with configurable `slop` and `in_order` requirements.
*   **`span_not` query**: Removes matches which overlap with another span query or are within a token distance before/after.
*   **`span_or` query**: Matches the union of its span clauses.
*   **`span_term` query**: The equivalent of the `term` query but for use within other span queries.
*   **`span_within` query**: Returns matches which are enclosed inside another span query.

### 3.8. Vector Queries

Specialized queries for efficient semantic search on vector fields.

*   **`knn` query**: Finds the *k* nearest vectors to a query vector in `dense_vector` fields, based on a similarity metric.
    ```json
    { "knn": { "field": "image-vector", "query_vector": [-5, 9, -12], "k": 10 } }
    ```
*   **`sparse_vector` query**: Searches `sparse_vector` fields using token-weight pairs, either from an NLP model or precalculated. This is the recommended query for sparse vector search.
    ```json
    { "sparse_vector": { "field": "ml.tokens", "inference_id": "my-elser-model", "query": "How is the weather in Jamaica?" } }
    ```
*   **`semantic` query**: Performs semantic search on `semantic_text` fields.
    ```json
    { "semantic": { "field": "inference_field", "query": "Best surfing places" } }
    ```
*   **Deprecated Vector Queries**: `text_expansion` and `weighted_tokens` are deprecated. Use `sparse_vector` instead.

### 3.9. Specialized Queries

This group contains queries that don't fit neatly into other categories.

*   **`distance_feature` query**: Boosts relevance scores of documents closer to a provided `origin` date or point. Efficiently skips non-competitive hits.
    ```json
    { "distance_feature": { "field": "production_date", "pivot": "7d", "origin": "now" } }
    ```
*   **`more_like_this` query (`mlt`)**: Finds documents similar to a given text, document, or collection of documents by extracting representative terms.
    ```json
    { "more_like_this": { "fields": ["title", "description"], "like": "Once upon a time", "min_term_freq": 1, "max_query_terms": 12 } }
    ```
*   **`percolate` query**: Matches queries stored in an index against a provided document. Useful for "reverse search" (finding which queries match a new document).
    ```json
    { "percolate": { "field": "query", "document": { "message": "A new bonsai tree in the office" } } }
    ```
*   **`rank_feature` query**: Boosts relevance scores based on the numeric value of a `rank_feature` or `rank_features` field. Efficiently skips non-competitive hits.
    ```json
    { "rank_feature": { "field": "pagerank", "saturation": { "pivot": 8 } } }
    ```
*   **`script` query**: Filters documents based on a provided script that returns a boolean value. Typically used in a filter context.
    ```json
    { "script": { "script": "doc['amount'].value < 10" } }
    ```
*   **`script_score` query**: Uses a script to provide a custom score for returned documents. Useful for complex scoring logic.
    ```json
    { "script_score": { "query": { "match": { "message": "elasticsearch" } }, "script": { "source": "doc['my-int'].value / 10" } }
    ```
*   **`wrapper` query**: Accepts any other query as a base64 encoded string. Primarily for Spring Data Elasticsearch.
    ```json
    { "wrapper": { "query": "eyJ0ZXJtIiA6IHsgInVzZXIuaWQiIDogImtpbWNoeSIgfX0=" } }
    ```
*   **`pinned` query**: Promotes selected documents (by ID) to rank higher than those matching an "organic" query.
    ```json
    { "pinned": { "ids": ["1", "4", "100"], "organic": { "match": { "description": "iphone" } } } }
    ```
*   **`rule` query**: Applies query rules (pre-defined in Elasticsearch) to the query before returning results, allowing for dynamic promotion or exclusion of documents.
    ```json
    { "rule": { "match_criteria": { "user_query": "pugs" }, "ruleset_ids": ["my-ruleset"], "organic": { "match": { "description": "puggles" } } } }
    ```

## 4. Common Parameters and Concepts

Several parameters and concepts are common across multiple Query DSL queries.

*   **`boost`**: A floating-point number (default `1.0`) used to increase or decrease the relevance score of a query. Values between 0 and 1 decrease, values greater than 1 increase.
*   **`analyzer`**: (Optional, string) Specifies the analyzer to use for text analysis in full-text queries. Defaults to the field's mapped analyzer or the index's default.
*   **`fuzziness`**: (Optional, string) Defines the maximum edit distance allowed for fuzzy matching (e.g., `AUTO`, `0`, `1`, `2`).
*   **`minimum_should_match`**: (Optional, string) Controls the number or percentage of `should` clauses that must match in a `bool` query or other queries that support it.
    *   **Values**: Integer (`3`), negative integer (`-2`), percentage (`75%`), negative percentage (`-25%`), combinations (`3<90%`).
*   **`rewrite`**: (Optional, string) Determines how multi-term queries (e.g., `prefix`, `wildcard`, `fuzzy`, `regexp`) are rewritten internally by Lucene. Affects scoring and performance.
    *   **Common values**: `constant_score_blended` (default), `constant_score`, `scoring_boolean`, `top_terms_N`.
*   **`slop`**: (Optional, integer) Maximum number of positions allowed between matching tokens in phrase or proximity queries.
*   **`zero_terms_query`**: (Optional, string) Defines behavior when an analyzer removes all tokens from a query (e.g., due to stop words). `none` (default) returns no documents; `all` returns all documents (like `match_all`).
*   **`case_insensitive`**: (Optional, Boolean) For some term-level queries, allows case-insensitive matching. Defaults to `false`.
*   **`ignore_unmapped`**: (Optional, Boolean) If `true`, ignores unmapped fields and returns no documents instead of an error. Useful for querying multiple indices with different mappings. Defaults to `false`.
*   **`time_zone`**: (Optional, string) For date-related queries, converts date values in the query string to UTC using a specified UTC offset or IANA time zone ID.
*   **`_name` (Named Queries)**: (Optional, string) Assigns a name to a query clause. If a named query matches, the response includes a `matched_queries` property for each hit, indicating which named queries matched.
*   **Expensive Queries (`search.allow_expensive_queries`)**: Certain queries (e.g., `script`, `fuzzy`, `regexp`, `prefix`, `wildcard`, `joining` queries) can be resource-intensive. The `search.allow_expensive_queries` setting (default `true`) can be set to `false` to prevent their execution.

## 5. Best Practices and Considerations

*   **Query vs. Filter Context**: Always use filter context for "must have" or "must not have" conditions that don't require scoring. This improves performance and leverages caching.
*   **Full-Text vs. Term-Level**: Use full-text queries (`match`, `multi_match`) for analyzed text fields. Use term-level queries (`term`, `terms`) for exact matches on structured data (keywords, numbers, dates). Avoid `term` on `text` fields.
*   **Wildcards and Regex**: Use sparingly, especially leading wildcards (`*term`). They can be very resource-intensive. Consider alternatives like `n-gram` tokenizers or `index_prefixes` mapping.
*   **Joining Queries**: `has_child` and `has_parent` queries can be slow due to joins. Use them judiciously.
*   **Scripting**: `script` and `script_score` queries can impact performance. Use predefined functions where possible, and consider `rank_feature` or `distance_feature` for boosting based on static fields or proximity.
*   **Deprecations**: Pay attention to deprecated queries (e.g., `geo_polygon`, `text_expansion`, `weighted_tokens`). Migrate to recommended alternatives (`geo_shape`, `sparse_vector`) to ensure future compatibility and leverage new features.
*   **`minimum_should_match`**: Use this parameter to fine-tune the relevance of `should` clauses, ensuring a minimum level of matching for documents to be considered relevant.
*   **Query Complexity**: While Query DSL is powerful, overly complex or deeply nested queries can lead to performance issues. Strive for simplicity and flatten queries where possible.
*   **Testing**: Always test your queries thoroughly, especially complex ones, to understand their behavior and performance characteristics. Use the `_explain` API to understand how scores are calculated.

This guide provides a foundation for constructing effective Query DSL queries. Refer to the specific documentation for each query type for detailed parameters and advanced usage.
"""  # noqa: E501


def search_dsl_tips() -> str:
    """Helpful tips for constructing Elasticsearch Query DSL queries."""
    return QUERY_DSL_TIPS

def search_str_fn_factory(es: AsyncElasticsearch) -> Callable[[str], Awaitable[dict[str, Any]]]:
    """Create a tool function that constructs Elasticsearch Query DSL queries."""

    async def search_str(query: str) -> dict[str, Any]:
        """Construct an Elasticsearch Query DSL query from stringified json.

        It is recommended to use the `dsl_query_tips` tool to understand how to construct Elasticsearch Query DSL queries."""
        response = await es.search(body=json.loads(query))  # pyright: ignore[reportAny]
        return response.raw

    return search_str
