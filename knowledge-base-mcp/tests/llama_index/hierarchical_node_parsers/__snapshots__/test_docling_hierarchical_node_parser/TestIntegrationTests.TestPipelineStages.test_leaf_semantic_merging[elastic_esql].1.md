# ES|QL aggregation functions

The STATS command supports these aggregate functions:

- AVG
- COUNT
- COUNT_DISTINCT
- MAX
- MEDIAN
- MEDIAN_ABSOLUTE_DEVIATION
- MIN
- PERCENTILE
- [preview] ST_CENTROID_AGG
- [preview] ST_EXTENT_AGG
- STD_DEV
- SUM
- TOP
- [preview] VALUES
- WEIGHTED_AVG

## AVG

Syntax

Parameters

- number
    - Expression that outputs values to average.

Description

The average of a numeric field.

Supported types

| number   | result   |
|----------|----------|
| double   | double   |
| integer  | double   |
| long     | double   |

Examples

```
FROM employees
| STATS AVG(height)
```

|   AVG(height):double |
|----------------------|
|               1.7682 |

The expression can use inline functions. For example, to calculate the average over a multivalued column, first use MV_AVG to average the multiple values per row, and use the result with the AVG function

```
FROM employees
| STATS avg_salary_change = ROUND(AVG(MV_AVG(salary_change)), 10)
```

|   avg_salary_change:double |
|----------------------------|
|                    1.39045 |

## COUNT

Syntax

Parameters

- field
    - Expression that outputs values to be counted. If omitted, equivalent to COUNT(*) (the number of rows).

Description

Returns the total number (count) of input values.

Supported types

| field           | result   |
|-----------------|----------|
| boolean         | long     |
| cartesian_point | long     |
| date            | long     |
| double          | long     |
| geo_point       | long     |
| integer         | long     |
| ip              | long     |
| keyword         | long     |
| long            | long     |
| text            | long     |
| unsigned_long   | long     |
| version         | long     |

Examples

```
FROM employees
| STATS COUNT(height)
```

|   COUNT(height):long |
|----------------------|
|                  100 |

To count the number of rows, use COUNT() or COUNT(*)

```
FROM employees
| STATS count = COUNT(*) BY languages
| SORT languages DESC
```

|   count:long | languages:integer   |
|--------------|---------------------|
|           10 | null                |
|           21 | 5                   |
|           18 | 4                   |
|           17 | 3                   |
|           19 | 2                   |
|           15 | 1                   |

The expression can use inline functions. This example splits a string into multiple values using the SPLIT function and counts the values

```
ROW words="foo;bar;baz;qux;quux;foo"
| STATS word_count = COUNT(SPLIT(words, ";"))
```

|   word_count:long |
|-------------------|
|                 6 |

To count the number of times an expression returns TRUE use a WHERE command to remove rows that shouldn’t be included

```
ROW n=1
| WHERE n < 0
| STATS COUNT(n)
```

|   COUNT(n):long |
|-----------------|
|               0 |

To count the same stream of data based on two different expressions use the pattern COUNT(<expression> OR NULL). This builds on the three-valued logic (3VL) of the language: TRUE OR NULL is TRUE, but FALSE OR NULL is NULL, plus the way COUNT handles NULLs: COUNT(TRUE) and COUNT(FALSE) are both 1, but COUNT(NULL) is 0.

```
ROW n=1
| STATS COUNT(n > 0 OR NULL), COUNT(n < 0 OR NULL)
```

|   COUNT(n > 0 OR NULL):long |   COUNT(n < 0 OR NULL):long |
|-----------------------------|-----------------------------|
|                           1 |                           0 |

## COUNT_DISTINCT

Syntax

Parameters

- field
    - Column or literal for which to count the number of distinct values.
- precision
    - Precision threshold. Refer to AGG-COUNT-DISTINCT-APPROXIMATE. The maximum supported value is 40000. Thresholds above this number will have the same effect as a threshold of 40000. The default value is 3000.

Description

Returns the approximate number of distinct values.

Supported types

| field      | precision     | result   |
|------------|---------------|----------|
| boolean    | integer       | long     |
| boolean    | long          | long     |
| boolean    | unsigned_long | long     |
| boolean    |               | long     |
| date       | integer       | long     |
| date       | long          | long     |
| date       | unsigned_long | long     |
| date       |               | long     |
| date_nanos | integer       | long     |
| date_nanos | long          | long     |
| date_nanos | unsigned_long | long     |
| date_nanos |               | long     |
| double     | integer       | long     |
| double     | long          | long     |
| double     | unsigned_long | long     |
| double     |               | long     |
| integer    | integer       | long     |
| integer    | long          | long     |
| integer    | unsigned_long | long     |
| integer    |               | long     |
| ip         | integer       | long     |
| ip         | long          | long     |
| ip         | unsigned_long | long     |
| ip         |               | long     |
| keyword    | integer       | long     |
| keyword    | long          | long     |
| keyword    | unsigned_long | long     |
| keyword    |               | long     |
| long       | integer       | long     |
| long       | long          | long     |
| long       | unsigned_long | long     |
| long       |               | long     |
| text       | integer       | long     |
| text       | long          | long     |
| text       | unsigned_long | long     |
| text       |               | long     |
| version    | integer       | long     |
| version    | long          | long     |
| version    | unsigned_long | long     |
| version    |               | long     |

Examples

```
FROM hosts
| STATS COUNT_DISTINCT(ip0), COUNT_DISTINCT(ip1)
```

|   COUNT_DISTINCT(ip0):long |   COUNT_DISTINCT(ip1):long |
|----------------------------|----------------------------|
|                          7 |                          8 |

With the optional second parameter to configure the precision threshold

```
FROM hosts
| STATS COUNT_DISTINCT(ip0, 80000), COUNT_DISTINCT(ip1, 5)
```

|   COUNT_DISTINCT(ip0, 80000):long |   COUNT_DISTINCT(ip1, 5):long |
|-----------------------------------|-------------------------------|
|                                 7 |                             9 |

The expression can use inline functions. This example splits a string into multiple values using the SPLIT function and counts the unique values

```
ROW words="foo;bar;baz;qux;quux;foo"
| STATS distinct_word_count = COUNT_DISTINCT(SPLIT(words, ";"))
```

|   distinct_word_count:long |
|----------------------------|
|                          5 |

### Counts are approximate

Computing exact counts requires loading values into a set and returning its
size. This doesn’t scale when working on high-cardinality sets and/or large
values as the required memory usage and the need to communicate those
per-shard sets between nodes would utilize too many resources of the cluster.

This COUNT_DISTINCT function is based on the
HyperLogLog++
algorithm, which counts based on the hashes of the values with some interesting
properties:

- configurable precision, which decides on how to trade memory for accuracy,
- excellent accuracy on low-cardinality sets,
- fixed memory usage: no matter if there are tens or billions of unique values, memory usage only depends on the configured precision.

For a precision threshold of c, the implementation that we are using requires about c * 8 bytes.

The following chart shows how the error varies before and after the threshold:

For all 3 thresholds, counts have been accurate up to the configured threshold. Although not guaranteed,
this is likely to be the case. Accuracy in practice depends on the dataset in question. In general,
most datasets show consistently good accuracy. Also note that even with a threshold as low as 100,
the error remains very low (1-6% as seen in the above graph) even when counting millions of items.

The HyperLogLog++ algorithm depends on the leading zeros of hashed values, the exact distributions of
hashes in a dataset can affect the accuracy of the cardinality.

The COUNT_DISTINCT function takes an optional second parameter to configure
the precision threshold. The precision_threshold options allows to trade memory
for accuracy, and defines a unique count below which counts are expected to be
close to accurate. Above this value, counts might become a bit more fuzzy. The
maximum supported value is 40000, thresholds above this number will have the
same effect as a threshold of 40000. The default value is 3000.

## MAX

Syntax

Parameters

- field

Description

The maximum value of a field.

Supported types

| field      | result     |
|------------|------------|
| boolean    | boolean    |
| date       | date       |
| date_nanos | date_nanos |
| double     | double     |
| integer    | integer    |
| ip         | ip         |
| keyword    | keyword    |
| long       | long       |
| text       | keyword    |
| version    | version    |

Examples

```
FROM employees
| STATS MAX(languages)
```

|   MAX(languages):integer |
|--------------------------|
|                        5 |

The expression can use inline functions. For example, to calculate the maximum over an average of a multivalued column, use MV_AVG to first average the multiple values per row, and use the result with the MAX function

```
FROM employees
| STATS max_avg_salary_change = MAX(MV_AVG(salary_change))
```

|   max_avg_salary_change:double |
|--------------------------------|
|                          13.75 |

## MEDIAN

Syntax

Parameters

- number
    - Expression that outputs values to calculate the median of.

Description

The value that is greater than half of all values and less than half of all values, also known as the 50% PERCENTILE.

Like PERCENTILE, MEDIAN is usually approximate.

Supported types

| number   | result   |
|----------|----------|
| double   | double   |
| integer  | double   |
| long     | double   |

Examples

```
FROM employees
| STATS MEDIAN(salary), PERCENTILE(salary, 50)
```

|   MEDIAN(salary):double |   PERCENTILE(salary, 50):double |
|-------------------------|---------------------------------|
|                   47003 |                           47003 |

The expression can use inline functions. For example, to calculate the median of the maximum values of a multivalued column, first use MV_MAX to get the maximum value per row, and use the result with the MEDIAN function

```
FROM employees
| STATS median_max_salary_change = MEDIAN(MV_MAX(salary_change))
```

|   median_max_salary_change:double |
|-----------------------------------|
|                              7.69 |

MEDIAN is also non-deterministic.
This means you can get slightly different results using the same data.

## MEDIAN_ABSOLUTE_DEVIATION

Syntax

Parameters

- number

Description

Returns the median absolute deviation, a measure of variability. It is a robust statistic, meaning that it is useful for describing data that may have outliers, or may not be normally distributed. For such data it can be more descriptive than standard deviation.  It is calculated as the median of each data point’s deviation from the median of the entire sample. That is, for a random variable X, the median absolute deviation is median(|median(X) - X|).

Like PERCENTILE, MEDIAN_ABSOLUTE_DEVIATION is usually approximate.

Supported types

| number   | result   |
|----------|----------|
| double   | double   |
| integer  | double   |
| long     | double   |

Examples

```
FROM employees
| STATS MEDIAN(salary), MEDIAN_ABSOLUTE_DEVIATION(salary)
```

|   MEDIAN(salary):double |   MEDIAN_ABSOLUTE_DEVIATION(salary):double |
|-------------------------|--------------------------------------------|
|                   47003 |                                    10096.5 |

The expression can use inline functions. For example, to calculate the median absolute deviation of the maximum values of a multivalued column, first use MV_MAX to get the maximum value per row, and use the result with the MEDIAN_ABSOLUTE_DEVIATION function

```
FROM employees
| STATS m_a_d_max_salary_change = MEDIAN_ABSOLUTE_DEVIATION(MV_MAX(salary_change))
```

|   m_a_d_max_salary_change:double |
|----------------------------------|
|                             5.69 |

MEDIAN_ABSOLUTE_DEVIATION is also non-deterministic.
This means you can get slightly different results using the same data.

## MIN

Syntax

Parameters

- field

Description

The minimum value of a field.

Supported types

| field      | result     |
|------------|------------|
| boolean    | boolean    |
| date       | date       |
| date_nanos | date_nanos |
| double     | double     |
| integer    | integer    |
| ip         | ip         |
| keyword    | keyword    |
| long       | long       |
| text       | keyword    |
| version    | version    |

Examples

```
FROM employees
| STATS MIN(languages)
```

|   MIN(languages):integer |
|--------------------------|
|                        1 |

The expression can use inline functions. For example, to calculate the minimum over an average of a multivalued column, use MV_AVG to first average the multiple values per row, and use the result with the MIN function

```
FROM employees
| STATS min_avg_salary_change = MIN(MV_AVG(salary_change))
```

|   min_avg_salary_change:double |
|--------------------------------|
|                          -8.46 |

## PERCENTILE

Syntax

Parameters

- number
- percentile

Description

Returns the value at which a certain percentage of observed values occur. For example, the 95th percentile is the value which is greater than 95% of the observed values and the 50th percentile is the MEDIAN.

Supported types

| number   | percentile   | result   |
|----------|--------------|----------|
| double   | double       | double   |
| double   | integer      | double   |
| double   | long         | double   |
| integer  | double       | double   |
| integer  | integer      | double   |
| integer  | long         | double   |
| long     | double       | double   |
| long     | integer      | double   |
| long     | long         | double   |

Examples

```
FROM employees
| STATS p0 = PERCENTILE(salary,  0)
 , p50 = PERCENTILE(salary, 50)
 , p99 = PERCENTILE(salary, 99)
```

|   p0:double |   p50:double |   p99:double |
|-------------|--------------|--------------|
|       25324 |        47003 |      74970.3 |

The expression can use inline functions. For example, to calculate a percentile of the maximum values of a multivalued column, first use MV_MAX to get the maximum value per row, and use the result with the PERCENTILE function

```
FROM employees
| STATS p80_max_salary_change = PERCENTILE(MV_MAX(salary_change), 80)
```

|   p80_max_salary_change:double |
|--------------------------------|
|                         12.132 |

### PERCENTILE is (usually) approximate

There are many different algorithms to calculate percentiles. The naive implementation simply stores all the values in a sorted array. To find the 50th percentile, you simply find the value that is at my_array[count(my_array) * 0.5].

Clearly, the naive implementation does not scale — the sorted array grows linearly with the number of values in your dataset. To calculate percentiles across potentially billions of values in an Elasticsearch cluster, approximate percentiles are calculated.

The algorithm used by the percentile metric is called TDigest (introduced by Ted Dunning in Computing Accurate Quantiles using T-Digests).

When using this metric, there are a few guidelines to keep in mind:

- Accuracy is proportional to q(1-q). This means that extreme percentiles (e.g. 99%) are more accurate than less extreme percentiles, such as the median
- For small sets of values, percentiles are highly accurate (and potentially 100% accurate if the data is small enough).
- As the quantity of values in a bucket grows, the algorithm begins to approximate the percentiles. It is effectively trading accuracy for memory savings. The exact level of inaccuracy is difficult to generalize, since it depends on your data distribution and volume of data being aggregated

The following chart shows the relative error on a uniform distribution depending on the number of collected values and the requested percentile:

It shows how precision is better for extreme percentiles. The reason why error diminishes for large number of values is that the law of large numbers makes the distribution of values more and more uniform and the t-digest tree can do a better job at summarizing it. It would not be the case on more skewed distributions.

PERCENTILE is also non-deterministic.
This means you can get slightly different results using the same data.

## ST_CENTROID_AGG

Elastic Stack				
Technical Preview



Serverless				
Technical Preview

Syntax

Parameters

- field

Description

Calculate the spatial centroid over a field with spatial point geometry type.

Supported types

| field           | result          |
|-----------------|-----------------|
| cartesian_point | cartesian_point |
| geo_point       | geo_point       |

Example

```
FROM airports
| STATS centroid=ST_CENTROID_AGG(location)
```

| centroid:geo_point                             |
|------------------------------------------------|
| POINT(-0.030548143003023033 24.37553649504829) |

## ST_EXTENT_AGG

Elastic Stack				
Technical Preview



Serverless				
Technical Preview

Syntax

Parameters

- field

Description

Calculate the spatial extent over a field with geometry type. Returns a bounding box for all values of the field.

Supported types

| field           | result          |
|-----------------|-----------------|
| cartesian_point | cartesian_shape |
| cartesian_shape | cartesian_shape |
| geo_point       | geo_shape       |
| geo_shape       | geo_shape       |

Example

```
FROM airports
| WHERE country == "India"
| STATS extent = ST_EXTENT_AGG(location)
```

| extent:geo_shape                                                               |
|--------------------------------------------------------------------------------|
| BBOX (70.77995480038226, 91.5882289968431, 33.9830909203738, 8.47650992218405) |

## STD_DEV

Syntax

Parameters

- number

Description

The population standard deviation of a numeric field.

Supported types

| number   | result   |
|----------|----------|
| double   | double   |
| integer  | double   |
| long     | double   |

Examples

```
FROM employees
| STATS STD_DEV(height)
```

|   STD_DEV(height):double |
|--------------------------|
|                  0.20637 |

The expression can use inline functions. For example, to calculate the population standard deviation of each employee’s maximum salary changes, first use MV_MAX on each row, and then use STD_DEV on the result

```
FROM employees
| STATS stddev_salary_change = STD_DEV(MV_MAX(salary_change))
```

|   stddev_salary_change:double |
|-------------------------------|
|                       6.87583 |

## SUM

Syntax

Parameters

- number

Description

The sum of a numeric expression.

Supported types

| number   | result   |
|----------|----------|
| double   | double   |
| integer  | long     |
| long     | long     |

Examples

```
FROM employees
| STATS SUM(languages)
```

|   SUM(languages):long |
|-----------------------|
|                   281 |

The expression can use inline functions. For example, to calculate the sum of each employee’s maximum salary changes, apply the MV_MAX function to each row and then sum the results

```
FROM employees
| STATS total_salary_changes = SUM(MV_MAX(salary_change))
```

|   total_salary_changes:double |
|-------------------------------|
|                        446.75 |

## TOP

Syntax

Parameters

- field
    - The field to collect the top values for.
- limit
    - The maximum number of values to collect.
- order
    - The order to calculate the top values. Either asc or desc.

Description

Collects the top values for a field. Includes repeated values.

Supported types

| field   | limit   | order   | result   |
|---------|---------|---------|----------|
| boolean | integer | keyword | boolean  |
| date    | integer | keyword | date     |
| double  | integer | keyword | double   |
| integer | integer | keyword | integer  |
| ip      | integer | keyword | ip       |
| keyword | integer | keyword | keyword  |
| long    | integer | keyword | long     |
| text    | integer | keyword | keyword  |

Example

```
FROM employees
| STATS top_salaries = TOP(salary, 3, "desc"), top_salary = MAX(salary)
```

| top_salaries:integer   |   top_salary:integer |
|------------------------|----------------------|
| [74999, 74970, 74572]  |                74999 |

## VALUES

Elastic Stack				
Technical Preview



Serverless				
Technical Preview

Syntax

Parameters

- field

Description

Returns unique values as a multivalued field. The order of the returned values isn’t guaranteed. If you need the values returned in order use MV_SORT.

Supported types

| field           | result          |
|-----------------|-----------------|
| boolean         | boolean         |
| cartesian_point | cartesian_point |
| cartesian_shape | cartesian_shape |
| date            | date            |
| date_nanos      | date_nanos      |
| double          | double          |
| geo_point       | geo_point       |
| geo_shape       | geo_shape       |
| integer         | integer         |
| ip              | ip              |
| keyword         | keyword         |
| long            | long            |
| text            | keyword         |
| version         | version         |

Example

```
FROM employees
| EVAL first_letter = SUBSTRING(first_name, 0, 1)
| STATS first_name = MV_SORT(VALUES(first_name)) BY first_letter
| SORT first_letter
```

| first_name:keyword                                                                                | first_letter:keyword   |
|---------------------------------------------------------------------------------------------------|------------------------|
| [Alejandro, Amabile, Anneke, Anoosh, Arumugam]                                                    | A                      |
| [Basil, Berhard, Berni, Bezalel, Bojan, Breannda, Brendon]                                        | B                      |
| [Charlene, Chirstian, Claudi, Cristinel]                                                          | C                      |
| [Danel, Divier, Domenick, Duangkaew]                                                              | D                      |
| [Ebbe, Eberhardt, Erez]                                                                           | E                      |
| Florian                                                                                           | F                      |
| [Gao, Georgi, Georgy, Gino, Guoxiang]                                                             | G                      |
| [Heping, Hidefumi, Hilari, Hironobu, Hironoby, Hisao]                                             | H                      |
| [Jayson, Jungsoon]                                                                                | J                      |
| [Kazuhide, Kazuhito, Kendra, Kenroku, Kshitij, Kwee, Kyoichi]                                     | K                      |
| [Lillian, Lucien]                                                                                 | L                      |
| [Magy, Margareta, Mary, Mayuko, Mayumi, Mingsen, Mokhtar, Mona, Moss]                             | M                      |
| Otmar                                                                                             | O                      |
| [Parto, Parviz, Patricio, Prasadram, Premal]                                                      | P                      |
| [Ramzi, Remzi, Reuven]                                                                            | R                      |
| [Sailaja, Saniya, Sanjiv, Satosi, Shahaf, Shir, Somnath, Sreekrishna, Sudharsan, Sumant, Suzette] | S                      |
| [Tse, Tuval, Tzvetan]                                                                             | T                      |
| [Udi, Uri]                                                                                        | U                      |
| [Valdiodio, Valter, Vishv]                                                                        | V                      |
| Weiyi                                                                                             | W                      |
| Xinglin                                                                                           | X                      |
| [Yinghua, Yishay, Yongqiao]                                                                       | Y                      |
| [Zhongwei, Zvonko]                                                                                | Z                      |
| null                                                                                              | null                   |

Use TOP
if you need to keep repeated values.

This can use a significant amount of memory and ES|QL doesn’t yet
grow aggregations beyond memory. So this aggregation will work until
it is used to collect more values than can fit into memory. Once it
collects too many values it will fail the query with
a Circuit Breaker Error.

## WEIGHTED_AVG

Syntax

Parameters

- number
    - A numeric value.
- weight
    - A numeric weight.

Description

The weighted average of a numeric expression.

Supported types

| number   | weight   | result   |
|----------|----------|----------|
| double   | double   | double   |
| double   | integer  | double   |
| double   | long     | double   |
| integer  | double   | double   |
| integer  | integer  | double   |
| integer  | long     | double   |
| long     | double   | double   |
| long     | integer  | double   |
| long     | long     | double   |

Example

```
FROM employees
| STATS w_avg = WEIGHTED_AVG(salary, height) BY languages
| EVAL w_avg = ROUND(w_avg)
| KEEP w_avg, languages
| SORT languages
```

|   w_avg:double | languages:integer   |
|----------------|---------------------|
|          51464 | 1                   |
|          48477 | 2                   |
|          52379 | 3                   |
|          47990 | 4                   |
|          42119 | 5                   |
|          52142 | null                |