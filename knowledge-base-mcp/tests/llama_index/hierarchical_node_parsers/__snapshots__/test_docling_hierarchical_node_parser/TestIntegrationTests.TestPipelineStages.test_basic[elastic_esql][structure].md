 : 0 - 222096: ## The Search AI Company  Build tailored experienc
 : 1 - 26960: # ES|QL aggregation functions  The STATS command s
   : 2 - 29: # ES|QL aggregation functions
   : 3 - 53: The STATS command supports these aggregate functio
   : 4 - 202: - AVG - COUNT - COUNT_DISTINCT - MAX - MEDIAN - ME
   : 5 - 789: ## AVG  Syntax  Parameters  ``` number ```  Expres
     : 6 - 6: ## AVG
     : 7 - 6: Syntax
     : 8 - 10: Parameters
     : 9 - 14: ``` number ```
     : 10 - 42: Expression that outputs values to average.
     : 11 - 11: Description
     : 12 - 31: The average of a numeric field.
     : 13 - 15: Supported types
     : 14 - 119: | number   | result   | |----------|----------| | 
     : 15 - 8: Examples
     : 16 - 42: ``` FROM employees | STATS AVG(height) ```
     : 17 - 74: |   AVG(height):double | |----------------------| 
     : 18 - 203: The expression can use inline functions. For examp
     : 19 - 88: ``` FROM employees | STATS avg_salary_change = ROU
     : 20 - 92: |   avg_salary_change:double | |------------------
   : 21 - 2348: ## COUNT  Syntax  Parameters  ``` field ```  Expre
     : 22 - 8: ## COUNT
     : 23 - 6: Syntax
     : 24 - 10: Parameters
     : 25 - 13: ``` field ```
     : 26 - 102: Expression that outputs values to be counted. If o
     : 27 - 11: Description
     : 28 - 49: Returns the total number (count) of input values.
     : 29 - 15: Supported types
     : 30 - 433: | field           | result   | |-----------------|
     : 31 - 8: Examples
     : 32 - 44: ``` FROM employees | STATS COUNT(height) ```
     : 33 - 74: |   COUNT(height):long | |----------------------| 
     : 34 - 52: To count the number of rows, use COUNT() or COUNT(
     : 35 - 82: ``` FROM employees | STATS count = COUNT(*) BY lan
     : 36 - 311: |   count:long | languages:integer   | |----------
     : 37 - 137: The expression can use inline functions. This exam
     : 38 - 90: ``` ROW words="foo;bar;baz;qux;quux;foo" | STATS w
     : 39 - 65: |   word_count:long | |-------------------| |     
     : 40 - 117: To count the number of times an expression returns
     : 41 - 46: ``` ROW n=1 | WHERE n < 0 | STATS COUNT(n) ```
     : 42 - 59: |   COUNT(n):long | |-----------------| |         
     : 43 - 319: To count the same stream of data based on two diff
     : 44 - 66: ``` ROW n=1 | STATS COUNT(n > 0 OR NULL), COUNT(n 
     : 45 - 185: |   COUNT(n > 0 OR NULL):long |   COUNT(n < 0 OR N
   : 46 - 5044: ## COUNT_DISTINCT  Syntax  Parameters  ``` field `
     : 47 - 17: ## COUNT_DISTINCT
     : 48 - 6: Syntax
     : 49 - 10: Parameters
     : 50 - 13: ``` field ```
     : 51 - 17: ``` precision ```
     : 52 - 206: Precision threshold. Refer to AGG-COUNT-DISTINCT-A
     : 53 - 11: Description
     : 54 - 50: Returns the approximate number of distinct values.
     : 55 - 15: Supported types
     : 56 - 1763: | field      | precision     | result   | |-------
     : 57 - 8: Examples
     : 58 - 67: ``` FROM hosts | STATS COUNT_DISTINCT(ip0), COUNT_
     : 59 - 179: |   COUNT_DISTINCT(ip0):long |   COUNT_DISTINCT(ip
     : 60 - 71: With the optional second parameter to configure th
     : 61 - 77: ``` FROM hosts | STATS COUNT_DISTINCT(ip0, 80000),
     : 62 - 209: |   COUNT_DISTINCT(ip0, 80000):long |   COUNT_DIST
     : 63 - 144: The expression can use inline functions. This exam
     : 64 - 108: ``` ROW words="foo;bar;baz;qux;quux;foo" | STATS d
     : 65 - 92: |   distinct_word_count:long | |------------------
     : 66 - 1943: ### Counts are approximate  Computing exact counts
       : 67 - 26: ### Counts are approximate
       : 68 - 299: Computing exact counts requires loading values int
       : 69 - 150: This COUNT_DISTINCT function is based on the Hyper
       : 70 - 257: - configurable precision, which decides on how to 
       : 71 - 96: For a precision threshold of c, the implementation
       : 72 - 78: The following chart shows how the error varies bef
       : 73 - 402: For all 3 thresholds, counts have been accurate up
       : 74 - 165: The HyperLogLog++ algorithm depends on the leading
       : 75 - 454: The COUNT_DISTINCT function takes an optional seco
   : 76 - 992: ## MAX  Syntax  Parameters  ``` field ```  Descrip
     : 77 - 6: ## MAX
     : 78 - 6: Syntax
     : 79 - 10: Parameters
     : 80 - 13: ``` field ```
     : 81 - 11: Description
     : 82 - 29: The maximum value of a field.
     : 83 - 15: Supported types
     : 84 - 335: | field      | result     | |------------|--------
     : 85 - 8: Examples
     : 86 - 45: ``` FROM employees | STATS MAX(languages) ```
     : 87 - 86: |   MAX(languages):integer | |--------------------
     : 88 - 217: The expression can use inline functions. For examp
     : 89 - 81: ``` FROM employees | STATS max_avg_salary_change =
     : 90 - 104: |   max_avg_salary_change:double | |--------------
   : 91 - 1223: ## MEDIAN  Syntax  Parameters  ``` number ```  Exp
     : 92 - 9: ## MEDIAN
     : 93 - 6: Syntax
     : 94 - 10: Parameters
     : 95 - 14: ``` number ```
     : 96 - 58: Expression that outputs values to calculate the me
     : 97 - 11: Description
     : 98 - 117: The value that is greater than half of all values 
     : 99 - 47: Like PERCENTILE, MEDIAN is usually approximate.
     : 100 - 15: Supported types
     : 101 - 119: | number   | result   | |----------|----------| | 
     : 102 - 8: Examples
     : 103 - 69: ``` FROM employees | STATS MEDIAN(salary), PERCENT
     : 104 - 185: |   MEDIAN(salary):double |   PERCENTILE(salary, 5
     : 105 - 219: The expression can use inline functions. For examp
     : 106 - 87: ``` FROM employees | STATS median_max_salary_chang
     : 107 - 113: |   median_max_salary_change:double | |-----------
     : 108 - 104: MEDIAN is also non-deterministic. This means you c
   : 109 - 1655: ## MEDIAN_ABSOLUTE_DEVIATION  Syntax  Parameters  
     : 110 - 28: ## MEDIAN_ABSOLUTE_DEVIATION
     : 111 - 6: Syntax
     : 112 - 10: Parameters
     : 113 - 14: ``` number ```
     : 114 - 11: Description
     : 115 - 455: Returns the median absolute deviation, a measure o
     : 116 - 66: Like PERCENTILE, MEDIAN_ABSOLUTE_DEVIATION is usua
     : 117 - 15: Supported types
     : 118 - 119: | number   | result   | |----------|----------| | 
     : 119 - 8: Examples
     : 120 - 80: ``` FROM employees | STATS MEDIAN(salary), MEDIAN_
     : 121 - 218: |   MEDIAN(salary):double |   MEDIAN_ABSOLUTE_DEVI
     : 122 - 257: The expression can use inline functions. For examp
     : 123 - 105: ``` FROM employees | STATS m_a_d_max_salary_change
     : 124 - 110: |   m_a_d_max_salary_change:double | |------------
     : 125 - 123: MEDIAN_ABSOLUTE_DEVIATION is also non-deterministi
   : 126 - 992: ## MIN  Syntax  Parameters  ``` field ```  Descrip
     : 127 - 6: ## MIN
     : 128 - 6: Syntax
     : 129 - 10: Parameters
     : 130 - 13: ``` field ```
     : 131 - 11: Description
     : 132 - 29: The minimum value of a field.
     : 133 - 15: Supported types
     : 134 - 335: | field      | result     | |------------|--------
     : 135 - 8: Examples
     : 136 - 45: ``` FROM employees | STATS MIN(languages) ```
     : 137 - 86: |   MIN(languages):integer | |--------------------
     : 138 - 217: The expression can use inline functions. For examp
     : 139 - 81: ``` FROM employees | STATS min_avg_salary_change =
     : 140 - 104: |   min_avg_salary_change:double | |--------------
   : 141 - 3327: ## PERCENTILE  Syntax  Parameters  ``` number ``` 
     : 142 - 13: ## PERCENTILE
     : 143 - 6: Syntax
     : 144 - 10: Parameters
     : 145 - 14: ``` number ```
     : 146 - 18: ``` percentile ```
     : 147 - 11: Description
     : 148 - 207: Returns the value at which a certain percentage of
     : 149 - 15: Supported types
     : 150 - 428: | number   | percentile   | result   | |----------
     : 151 - 8: Examples
     : 152 - 122: ``` FROM employees | STATS p0 = PERCENTILE(salary,
     : 153 - 137: |   p0:double |   p50:double |   p99:double | |---
     : 154 - 225: The expression can use inline functions. For examp
     : 155 - 92: ``` FROM employees | STATS p80_max_salary_change =
     : 156 - 104: |   p80_max_salary_change:double | |--------------
     : 157 - 1887: ### PERCENTILE is (usually) approximate  There are
       : 158 - 39: ### PERCENTILE is (usually) approximate
       : 159 - 233: There are many different algorithms to calculate p
       : 160 - 257: Clearly, the naive implementation does not scale —
       : 161 - 138: The algorithm used by the percentile metric is cal
       : 162 - 67: When using this metric, there are a few guidelines
       : 163 - 565: - Accuracy is proportional to q(1-q). This means t
       : 164 - 144: The following chart shows the relative error on a 
       : 165 - 320: It shows how precision is better for extreme perce
       : 166 - 108: PERCENTILE is also non-deterministic. This means y
   : 167 - 617: ## ST_CENTROID_AGG  Elastic Stack				 Technical Pr
     : 168 - 18: ## ST_CENTROID_AGG
     : 169 - 71: Elastic Stack				 Technical Preview    Serverless	
     : 170 - 6: Syntax
     : 171 - 10: Parameters
     : 172 - 13: ``` field ```
     : 173 - 11: Description
     : 174 - 77: Calculate the spatial centroid over a field with s
     : 175 - 15: Supported types
     : 176 - 151: | field           | result          | |-----------
     : 177 - 7: Example
     : 178 - 64: ``` FROM airports | STATS centroid=ST_CENTROID_AGG
     : 179 - 152: | centroid:geo_point                             |
   : 180 - 848: ## ST_EXTENT_AGG  Elastic Stack				 Technical Prev
     : 181 - 16: ## ST_EXTENT_AGG
     : 182 - 71: Elastic Stack				 Technical Preview    Serverless	
     : 183 - 6: Syntax
     : 184 - 10: Parameters
     : 185 - 13: ``` field ```
     : 186 - 11: Description
     : 187 - 113: Calculate the spatial extent over a field with geo
     : 188 - 15: Supported types
     : 189 - 227: | field           | result          | |-----------
     : 190 - 7: Example
     : 191 - 89: ``` FROM airports | WHERE country == "India" | STA
     : 192 - 248: | extent:geo_shape                                
   : 193 - 797: ## STD_DEV  Syntax  Parameters  ``` number ```  De
     : 194 - 10: ## STD_DEV
     : 195 - 6: Syntax
     : 196 - 10: Parameters
     : 197 - 14: ``` number ```
     : 198 - 11: Description
     : 199 - 53: The population standard deviation of a numeric fie
     : 200 - 15: Supported types
     : 201 - 119: | number   | result   | |----------|----------| | 
     : 202 - 8: Examples
     : 203 - 46: ``` FROM employees | STATS STD_DEV(height) ```
     : 204 - 86: |   STD_DEV(height):double | |--------------------
     : 205 - 208: The expression can use inline functions. For examp
     : 206 - 84: ``` FROM employees | STATS stddev_salary_change = 
     : 207 - 101: |   stddev_salary_change:double | |---------------
   : 208 - 730: ## SUM  Syntax  Parameters  ``` number ```  Descri
     : 209 - 6: ## SUM
     : 210 - 6: Syntax
     : 211 - 10: Parameters
     : 212 - 14: ``` number ```
     : 213 - 11: Description
     : 214 - 32: The sum of a numeric expression.
     : 215 - 15: Supported types
     : 216 - 119: | number   | result   | |----------|----------| | 
     : 217 - 8: Examples
     : 218 - 45: ``` FROM employees | STATS SUM(languages) ```
     : 219 - 77: |   SUM(languages):long | |-----------------------
     : 220 - 180: The expression can use inline functions. For examp
     : 221 - 80: ``` FROM employees | STATS total_salary_changes = 
     : 222 - 101: |   total_salary_changes:double | |---------------
   : 223 - 912: ## TOP  Syntax  Parameters  ``` field ```  ``` lim
     : 224 - 6: ## TOP
     : 225 - 6: Syntax
     : 226 - 10: Parameters
     : 227 - 13: ``` field ```
     : 228 - 13: ``` limit ```
     : 229 - 13: ``` order ```
     : 230 - 58: The order to calculate the top values. Either asc 
     : 231 - 11: Description
     : 232 - 62: Collects the top values for a field. Includes repe
     : 233 - 15: Supported types
     : 234 - 429: | field   | limit   | order   | result   | |------
     : 235 - 7: Example
     : 236 - 94: ``` FROM employees | STATS top_salaries = TOP(sala
     : 237 - 149: | top_salaries:integer   |   top_salary:integer | 
   : 238 - 4707: ## VALUES  Elastic Stack				 Technical Preview    
     : 239 - 9: ## VALUES
     : 240 - 71: Elastic Stack				 Technical Preview    Serverless	
     : 241 - 6: Syntax
     : 242 - 10: Parameters
     : 243 - 13: ``` field ```
     : 244 - 11: Description
     : 245 - 150: Returns unique values as a multivalued field. The 
     : 246 - 15: Supported types
     : 247 - 607: | field           | result          | |-----------
     : 248 - 7: Example
     : 249 - 157: ``` FROM employees | EVAL first_letter = SUBSTRING
     : 250 - 3301: | first_name:keyword                              
     : 251 - 44: Use TOP if you need to keep repeated values.
     : 252 - 280: This can use a significant amount of memory and ES
   : 253 - 1661: ## WEIGHTED_AVG  Syntax  Parameters  ``` number ``
     : 254 - 15: ## WEIGHTED_AVG
     : 255 - 6: Syntax
     : 256 - 10: Parameters
     : 257 - 14: ``` number ```
     : 258 - 14: ``` weight ```
     : 259 - 17: A numeric weight.
     : 260 - 11: Description
     : 261 - 45: The weighted average of a numeric expression.
     : 262 - 15: Supported types
     : 263 - 384: | number   | weight   | result   | |----------|---
     : 264 - 7: Example
     : 265 - 149: ``` FROM employees | STATS w_avg = WEIGHTED_AVG(sa
     : 266 - 327: |   w_avg:double | languages:integer   | |--------
     : 267 - 8: Previous
     : 268 - 23: Functions and operators
     : 269 - 4: Next
     : 270 - 18: Grouping functions
     : 271 - 47: - Trademarks - Terms of Use - Privacy - Sitemap
     : 272 - 46: © 2025 Elasticsearch B.V. All Rights Reserved.
     : 273 - 272: Elasticsearch is a trademark of Elasticsearch B.V.
     : 274 - 189: Welcome to the docs for the latest Elastic product