# My simple document

This is a simple document.

## My simple document has sub-headings

Here is the content of the sub-headings.

## Here is sub-heading number two

Here is a table:
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Row 1    | Row 1    | Row 1    |
| Row 2    | Row 2    | Row 2    |
| Row 3    | Row 3    | Row 3    |

Here is a list:
- Item 1
- Item 2
- Item 3

## Code block sub-heading

```
print("Hello, world!")
```

Here is a code block with a language

```python
print("Hello, world!")
```

Here is a large code block

```python
import numpy as np
import pandas as pd
import time

def __main__():
    start_time = time.time()
    for i in range(1000000):
        np.random.rand()
    end_time = time.time()
    print(f"Time taken: {end_time - start_time} seconds")

if __name__ == "__main__":
    __main__()
```