 : 0 - 26433: # ES|QL aggregation functions  The STATS command s
   : 1 - 29: # ES|QL aggregation functions
   : 2 - 53: The STATS command supports these aggregate functio
   : 3 - 202: - AVG - COUNT - COUNT_DISTINCT - MAX - MEDIAN - ME
   : 4 - 788: ## AVG  Syntax  Parameters  - number     - Express
     : 5 - 6: ## AVG
     : 6 - 6: Syntax
     : 7 - 10: Parameters
     : 8 - 57: - number     - Expression that outputs values to a
     : 9 - 11: Description
     : 10 - 31: The average of a numeric field.
     : 11 - 15: Supported types
     : 12 - 119: | number   | result   | |----------|----------| | 
     : 13 - 8: Examples
     : 14 - 42: ``` FROM employees | STATS AVG(height) ```
     : 15 - 74: |   AVG(height):double | |----------------------| 
     : 16 - 203: The expression can use inline functions. For examp
     : 17 - 88: ``` FROM employees | STATS avg_salary_change = ROU
     : 18 - 92: |   avg_salary_change:double | |------------------
   : 19 - 2347: ## COUNT  Syntax  Parameters  - field     - Expres
     : 20 - 8: ## COUNT
     : 21 - 6: Syntax
     : 22 - 10: Parameters
     : 23 - 116: - field     - Expression that outputs values to be
     : 24 - 11: Description
     : 25 - 49: Returns the total number (count) of input values.
     : 26 - 15: Supported types
     : 27 - 433: | field           | result   | |-----------------|
     : 28 - 8: Examples
     : 29 - 44: ``` FROM employees | STATS COUNT(height) ```
     : 30 - 74: |   COUNT(height):long | |----------------------| 
     : 31 - 52: To count the number of rows, use COUNT() or COUNT(
     : 32 - 82: ``` FROM employees | STATS count = COUNT(*) BY lan
     : 33 - 311: |   count:long | languages:integer   | |----------
     : 34 - 137: The expression can use inline functions. This exam
     : 35 - 90: ``` ROW words="foo;bar;baz;qux;quux;foo" | STATS w
     : 36 - 65: |   word_count:long | |-------------------| |     
     : 37 - 117: To count the number of times an expression returns
     : 38 - 46: ``` ROW n=1 | WHERE n < 0 | STATS COUNT(n) ```
     : 39 - 59: |   COUNT(n):long | |-----------------| |         
     : 40 - 319: To count the same stream of data based on two diff
     : 41 - 66: ``` ROW n=1 | STATS COUNT(n > 0 OR NULL), COUNT(n 
     : 42 - 185: |   COUNT(n > 0 OR NULL):long |   COUNT(n < 0 OR N
   : 43 - 5110: ## COUNT_DISTINCT  Syntax  Parameters  - field    
     : 44 - 17: ## COUNT_DISTINCT
     : 45 - 6: Syntax
     : 46 - 10: Parameters
     : 47 - 306: - field     - Column or literal for which to count
     : 48 - 11: Description
     : 49 - 50: Returns the approximate number of distinct values.
     : 50 - 15: Supported types
     : 51 - 1763: | field      | precision     | result   | |-------
     : 52 - 8: Examples
     : 53 - 67: ``` FROM hosts | STATS COUNT_DISTINCT(ip0), COUNT_
     : 54 - 179: |   COUNT_DISTINCT(ip0):long |   COUNT_DISTINCT(ip
     : 55 - 71: With the optional second parameter to configure th
     : 56 - 77: ``` FROM hosts | STATS COUNT_DISTINCT(ip0, 80000),
     : 57 - 209: |   COUNT_DISTINCT(ip0, 80000):long |   COUNT_DIST
     : 58 - 144: The expression can use inline functions. This exam
     : 59 - 108: ``` ROW words="foo;bar;baz;qux;quux;foo" | STATS d
     : 60 - 92: |   distinct_word_count:long | |------------------
     : 61 - 1943: ### Counts are approximate  Computing exact counts
       : 62 - 26: ### Counts are approximate
       : 63 - 299: Computing exact counts requires loading values int
       : 64 - 150: This COUNT_DISTINCT function is based on the Hyper
       : 65 - 257: - configurable precision, which decides on how to 
       : 66 - 96: For a precision threshold of c, the implementation
       : 67 - 78: The following chart shows how the error varies bef
       : 68 - 402: For all 3 thresholds, counts have been accurate up
       : 69 - 165: The HyperLogLog++ algorithm depends on the leading
       : 70 - 454: The COUNT_DISTINCT function takes an optional seco
   : 71 - 986: ## MAX  Syntax  Parameters  - field  Description  
     : 72 - 6: ## MAX
     : 73 - 6: Syntax
     : 74 - 10: Parameters
     : 75 - 7: - field
     : 76 - 11: Description
     : 77 - 29: The maximum value of a field.
     : 78 - 15: Supported types
     : 79 - 335: | field      | result     | |------------|--------
     : 80 - 8: Examples
     : 81 - 45: ``` FROM employees | STATS MAX(languages) ```
     : 82 - 86: |   MAX(languages):integer | |--------------------
     : 83 - 217: The expression can use inline functions. For examp
     : 84 - 81: ``` FROM employees | STATS max_avg_salary_change =
     : 85 - 104: |   max_avg_salary_change:double | |--------------
   : 86 - 1222: ## MEDIAN  Syntax  Parameters  - number     - Expr
     : 87 - 9: ## MEDIAN
     : 88 - 6: Syntax
     : 89 - 10: Parameters
     : 90 - 73: - number     - Expression that outputs values to c
     : 91 - 11: Description
     : 92 - 117: The value that is greater than half of all values 
     : 93 - 47: Like PERCENTILE, MEDIAN is usually approximate.
     : 94 - 15: Supported types
     : 95 - 119: | number   | result   | |----------|----------| | 
     : 96 - 8: Examples
     : 97 - 69: ``` FROM employees | STATS MEDIAN(salary), PERCENT
     : 98 - 185: |   MEDIAN(salary):double |   PERCENTILE(salary, 5
     : 99 - 219: The expression can use inline functions. For examp
     : 100 - 87: ``` FROM employees | STATS median_max_salary_chang
     : 101 - 113: |   median_max_salary_change:double | |-----------
     : 102 - 104: MEDIAN is also non-deterministic. This means you c
   : 103 - 1649: ## MEDIAN_ABSOLUTE_DEVIATION  Syntax  Parameters  
     : 104 - 28: ## MEDIAN_ABSOLUTE_DEVIATION
     : 105 - 6: Syntax
     : 106 - 10: Parameters
     : 107 - 8: - number
     : 108 - 11: Description
     : 109 - 455: Returns the median absolute deviation, a measure o
     : 110 - 66: Like PERCENTILE, MEDIAN_ABSOLUTE_DEVIATION is usua
     : 111 - 15: Supported types
     : 112 - 119: | number   | result   | |----------|----------| | 
     : 113 - 8: Examples
     : 114 - 80: ``` FROM employees | STATS MEDIAN(salary), MEDIAN_
     : 115 - 218: |   MEDIAN(salary):double |   MEDIAN_ABSOLUTE_DEVI
     : 116 - 257: The expression can use inline functions. For examp
     : 117 - 105: ``` FROM employees | STATS m_a_d_max_salary_change
     : 118 - 110: |   m_a_d_max_salary_change:double | |------------
     : 119 - 123: MEDIAN_ABSOLUTE_DEVIATION is also non-deterministi
   : 120 - 986: ## MIN  Syntax  Parameters  - field  Description  
     : 121 - 6: ## MIN
     : 122 - 6: Syntax
     : 123 - 10: Parameters
     : 124 - 7: - field
     : 125 - 11: Description
     : 126 - 29: The minimum value of a field.
     : 127 - 15: Supported types
     : 128 - 335: | field      | result     | |------------|--------
     : 129 - 8: Examples
     : 130 - 45: ``` FROM employees | STATS MIN(languages) ```
     : 131 - 86: |   MIN(languages):integer | |--------------------
     : 132 - 217: The expression can use inline functions. For examp
     : 133 - 81: ``` FROM employees | STATS min_avg_salary_change =
     : 134 - 104: |   min_avg_salary_change:double | |--------------
   : 135 - 3314: ## PERCENTILE  Syntax  Parameters  - number - perc
     : 136 - 13: ## PERCENTILE
     : 137 - 6: Syntax
     : 138 - 10: Parameters
     : 139 - 21: - number - percentile
     : 140 - 11: Description
     : 141 - 207: Returns the value at which a certain percentage of
     : 142 - 15: Supported types
     : 143 - 428: | number   | percentile   | result   | |----------
     : 144 - 8: Examples
     : 145 - 122: ``` FROM employees | STATS p0 = PERCENTILE(salary,
     : 146 - 137: |   p0:double |   p50:double |   p99:double | |---
     : 147 - 225: The expression can use inline functions. For examp
     : 148 - 92: ``` FROM employees | STATS p80_max_salary_change =
     : 149 - 104: |   p80_max_salary_change:double | |--------------
     : 150 - 1887: ### PERCENTILE is (usually) approximate  There are
       : 151 - 39: ### PERCENTILE is (usually) approximate
       : 152 - 233: There are many different algorithms to calculate p
       : 153 - 257: Clearly, the naive implementation does not scale —
       : 154 - 138: The algorithm used by the percentile metric is cal
       : 155 - 67: When using this metric, there are a few guidelines
       : 156 - 565: - Accuracy is proportional to q(1-q). This means t
       : 157 - 144: The following chart shows the relative error on a 
       : 158 - 320: It shows how precision is better for extreme perce
       : 159 - 108: PERCENTILE is also non-deterministic. This means y
   : 160 - 611: ## ST_CENTROID_AGG  Elastic Stack				 Technical Pr
     : 161 - 18: ## ST_CENTROID_AGG
     : 162 - 71: Elastic Stack				 Technical Preview    Serverless	
     : 163 - 6: Syntax
     : 164 - 10: Parameters
     : 165 - 7: - field
     : 166 - 11: Description
     : 167 - 77: Calculate the spatial centroid over a field with s
     : 168 - 15: Supported types
     : 169 - 151: | field           | result          | |-----------
     : 170 - 7: Example
     : 171 - 64: ``` FROM airports | STATS centroid=ST_CENTROID_AGG
     : 172 - 152: | centroid:geo_point                             |
   : 173 - 842: ## ST_EXTENT_AGG  Elastic Stack				 Technical Prev
     : 174 - 16: ## ST_EXTENT_AGG
     : 175 - 71: Elastic Stack				 Technical Preview    Serverless	
     : 176 - 6: Syntax
     : 177 - 10: Parameters
     : 178 - 7: - field
     : 179 - 11: Description
     : 180 - 113: Calculate the spatial extent over a field with geo
     : 181 - 15: Supported types
     : 182 - 227: | field           | result          | |-----------
     : 183 - 7: Example
     : 184 - 89: ``` FROM airports | WHERE country == "India" | STA
     : 185 - 248: | extent:geo_shape                                
   : 186 - 791: ## STD_DEV  Syntax  Parameters  - number  Descript
     : 187 - 10: ## STD_DEV
     : 188 - 6: Syntax
     : 189 - 10: Parameters
     : 190 - 8: - number
     : 191 - 11: Description
     : 192 - 53: The population standard deviation of a numeric fie
     : 193 - 15: Supported types
     : 194 - 119: | number   | result   | |----------|----------| | 
     : 195 - 8: Examples
     : 196 - 46: ``` FROM employees | STATS STD_DEV(height) ```
     : 197 - 86: |   STD_DEV(height):double | |--------------------
     : 198 - 208: The expression can use inline functions. For examp
     : 199 - 84: ``` FROM employees | STATS stddev_salary_change = 
     : 200 - 101: |   stddev_salary_change:double | |---------------
   : 201 - 724: ## SUM  Syntax  Parameters  - number  Description 
     : 202 - 6: ## SUM
     : 203 - 6: Syntax
     : 204 - 10: Parameters
     : 205 - 8: - number
     : 206 - 11: Description
     : 207 - 32: The sum of a numeric expression.
     : 208 - 15: Supported types
     : 209 - 119: | number   | result   | |----------|----------| | 
     : 210 - 8: Examples
     : 211 - 45: ``` FROM employees | STATS SUM(languages) ```
     : 212 - 77: |   SUM(languages):long | |-----------------------
     : 213 - 180: The expression can use inline functions. For examp
     : 214 - 80: ``` FROM employees | STATS total_salary_changes = 
     : 215 - 101: |   total_salary_changes:double | |---------------
   : 216 - 991: ## TOP  Syntax  Parameters  - field     - The fiel
     : 217 - 6: ## TOP
     : 218 - 6: Syntax
     : 219 - 10: Parameters
     : 220 - 182: - field     - The field to collect the top values 
     : 221 - 11: Description
     : 222 - 62: Collects the top values for a field. Includes repe
     : 223 - 15: Supported types
     : 224 - 429: | field   | limit   | order   | result   | |------
     : 225 - 7: Example
     : 226 - 94: ``` FROM employees | STATS top_salaries = TOP(sala
     : 227 - 149: | top_salaries:integer   |   top_salary:integer | 
   : 228 - 4701: ## VALUES  Elastic Stack				 Technical Preview    
     : 229 - 9: ## VALUES
     : 230 - 71: Elastic Stack				 Technical Preview    Serverless	
     : 231 - 6: Syntax
     : 232 - 10: Parameters
     : 233 - 7: - field
     : 234 - 11: Description
     : 235 - 150: Returns unique values as a multivalued field. The 
     : 236 - 15: Supported types
     : 237 - 607: | field           | result          | |-----------
     : 238 - 7: Example
     : 239 - 157: ``` FROM employees | EVAL first_letter = SUBSTRING
     : 240 - 3301: | first_name:keyword                              
     : 241 - 44: Use TOP if you need to keep repeated values.
     : 242 - 280: This can use a significant amount of memory and ES
   : 243 - 1053: ## WEIGHTED_AVG  Syntax  Parameters  - number     
     : 244 - 15: ## WEIGHTED_AVG
     : 245 - 6: Syntax
     : 246 - 10: Parameters
     : 247 - 64: - number     - A numeric value. - weight     - A n
     : 248 - 11: Description
     : 249 - 45: The weighted average of a numeric expression.
     : 250 - 15: Supported types
     : 251 - 384: | number   | weight   | result   | |----------|---
     : 252 - 7: Example
     : 253 - 149: ``` FROM employees | STATS w_avg = WEIGHTED_AVG(sa
     : 254 - 327: |   w_avg:double | languages:integer   | |--------