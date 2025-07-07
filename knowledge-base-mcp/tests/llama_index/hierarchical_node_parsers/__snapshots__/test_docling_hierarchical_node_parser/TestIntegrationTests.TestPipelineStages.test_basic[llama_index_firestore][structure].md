 : 0 - 7886: # Firestore Demo¶  This guide shows you how to dir
   : 1 - 16: # Firestore Demo
   : 2 - 254: This guide shows you how to directly use our Docum
   : 3 - 89: If you're opening this Notebook on colab, you will
   : 4 - 7: In [ ]:
   : 5 - 202: ``` %pip install llama-index-storage-docstore-fire
   : 6 - 194: %pip install llama-index-storage-docstore-firestor
   : 7 - 7: In [ ]:
   : 8 - 32: ``` !pip install llama-index ```
   : 9 - 24: !pip install llama-index
   : 10 - 7: In [ ]:
   : 11 - 49: ``` import nest_asyncio  nest_asyncio.apply() ```
   : 12 - 41: import nest_asyncio  nest_asyncio.apply()
   : 13 - 7: In [ ]:
   : 14 - 166: ``` import logging import sys  logging.basicConfig
   : 15 - 158: import logging import sys  logging.basicConfig(str
   : 16 - 7: In [ ]:
   : 17 - 383: ``` from llama_index.core import SimpleDirectoryRe
   : 18 - 375: from llama_index.core import SimpleDirectoryReader
   : 19 - 5831: #### Download Data¶  In [ ]:  ``` !mkdir -p 'data/