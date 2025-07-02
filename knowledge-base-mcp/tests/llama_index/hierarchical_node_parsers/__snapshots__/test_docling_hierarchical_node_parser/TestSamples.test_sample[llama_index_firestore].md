# Firestore Demo¶

This guide shows you how to directly use our DocumentStore abstraction backed by Google Firestore. By putting nodes in the docstore, this allows you to define multiple indices over the same underlying docstore, instead of duplicating data across indices.

If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.

In [ ]:

```
%pip install llama-index-storage-docstore-firestore
%pip install llama-index-storage-kvstore-firestore
%pip install llama-index-storage-index-store-firestore
%pip install llama-index-llms-openai
```

%pip install llama-index-storage-docstore-firestore
%pip install llama-index-storage-kvstore-firestore
%pip install llama-index-storage-index-store-firestore
%pip install llama-index-llms-openai

In [ ]:

```
!pip install llama-index
```

!pip install llama-index

In [ ]:

```
import nest_asyncio

nest_asyncio.apply()
```

import nest_asyncio

nest_asyncio.apply()

In [ ]:

```
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
```

import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

In [ ]:

```
from llama_index.core import SimpleDirectoryReader, StorageContext
from llama_index.core import VectorStoreIndex, SimpleKeywordTableIndex
from llama_index.core import SummaryIndex
from llama_index.core import ComposableGraph
from llama_index.llms.openai import OpenAI
from llama_index.core.response.notebook_utils import display_response
from llama_index.core import Settings
```

from llama_index.core import SimpleDirectoryReader, StorageContext
from llama_index.core import VectorStoreIndex, SimpleKeywordTableIndex
from llama_index.core import SummaryIndex
from llama_index.core import ComposableGraph
from llama_index.llms.openai import OpenAI
from llama_index.core.response.notebook_utils import display_response
from llama_index.core import Settings

#### Download Data¶

In [ ]:

```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
```

!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

#### Load Documents¶

In [ ]:

```
reader = SimpleDirectoryReader("./data/paul_graham/")
documents = reader.load_data()
```

reader = SimpleDirectoryReader("./data/paul_graham/")
documents = reader.load_data()

#### Parse into Nodes¶

In [ ]:

```
from llama_index.core.node_parser import SentenceSplitter

nodes = SentenceSplitter().get_nodes_from_documents(documents)
```

from llama_index.core.node_parser import SentenceSplitter

nodes = SentenceSplitter().get_nodes_from_documents(documents)

#### Add to Docstore¶

In [ ]:

```
from llama_index.storage.kvstore.firestore import FirestoreKVStore
from llama_index.storage.docstore.firestore import FirestoreDocumentStore
from llama_index.storage.index_store.firestore import FirestoreIndexStore
```

from llama_index.storage.kvstore.firestore import FirestoreKVStore
from llama_index.storage.docstore.firestore import FirestoreDocumentStore
from llama_index.storage.index_store.firestore import FirestoreIndexStore

In [ ]:

```
kvstore = FirestoreKVStore()

storage_context = StorageContext.from_defaults(
  docstore=FirestoreDocumentStore(kvstore),
  index_store=FirestoreIndexStore(kvstore),
)
```

kvstore = FirestoreKVStore()

storage_context = StorageContext.from_defaults(
  docstore=FirestoreDocumentStore(kvstore),
  index_store=FirestoreIndexStore(kvstore),
)

In [ ]:

```
storage_context.docstore.add_documents(nodes)
```

storage_context.docstore.add_documents(nodes)

#### Define Multiple Indexes¶

Each index uses the same underlying Node.

In [ ]:

```
summary_index = SummaryIndex(nodes, storage_context=storage_context)
```

summary_index = SummaryIndex(nodes, storage_context=storage_context)

In [ ]:

```
vector_index = VectorStoreIndex(nodes, storage_context=storage_context)
```

vector_index = VectorStoreIndex(nodes, storage_context=storage_context)

In [ ]:

```
keyword_table_index = SimpleKeywordTableIndex(
  nodes, storage_context=storage_context
)
```

keyword_table_index = SimpleKeywordTableIndex(
  nodes, storage_context=storage_context
)

In [ ]:

```
# NOTE: the docstore still has the same nodes
len(storage_context.docstore.docs)
```

# NOTE: the docstore still has the same nodes
len(storage_context.docstore.docs)

#### Test out saving and loading¶

In [ ]:

```
# NOTE: docstore and index_store is persisted in Firestore by default
# NOTE: here only need to persist simple vector store to disk
storage_context.persist()
```

# NOTE: docstore and index_store is persisted in Firestore by default
# NOTE: here only need to persist simple vector store to disk
storage_context.persist()

In [ ]:

```
# note down index IDs
list_id = summary_index.index_id
vector_id = vector_index.index_id
keyword_id = keyword_table_index.index_id
```

# note down index IDs
list_id = summary_index.index_id
vector_id = vector_index.index_id
keyword_id = keyword_table_index.index_id

In [ ]:

```
from llama_index.core import load_index_from_storage

kvstore = FirestoreKVStore()

# re-create storage context
storage_context = StorageContext.from_defaults(
  docstore=FirestoreDocumentStore(kvstore),
  index_store=FirestoreIndexStore(kvstore),
)

# load indices
summary_index = load_index_from_storage(
  storage_context=storage_context, index_id=list_id
)
vector_index = load_index_from_storage(
  storage_context=storage_context, vector_id=vector_id
)
keyword_table_index = load_index_from_storage(
  storage_context=storage_context, keyword_id=keyword_id
)
```

from llama_index.core import load_index_from_storage

kvstore = FirestoreKVStore()

# re-create storage context
storage_context = StorageContext.from_defaults(
  docstore=FirestoreDocumentStore(kvstore),
  index_store=FirestoreIndexStore(kvstore),
)

# load indices
summary_index = load_index_from_storage(
  storage_context=storage_context, index_id=list_id
)
vector_index = load_index_from_storage(
  storage_context=storage_context, vector_id=vector_id
)
keyword_table_index = load_index_from_storage(
  storage_context=storage_context, keyword_id=keyword_id
)

#### Test out some Queries¶

In [ ]:

```
chatgpt = OpenAI(temperature=0, model="gpt-3.5-turbo")
Settings.llm = chatgpt
Settings.chunk_size = 1024
```

chatgpt = OpenAI(temperature=0, model="gpt-3.5-turbo")
Settings.llm = chatgpt
Settings.chunk_size = 1024

In [ ]:

```
query_engine = summary_index.as_query_engine()
list_response = query_engine.query("What is a summary of this document?")
```

query_engine = summary_index.as_query_engine()
list_response = query_engine.query("What is a summary of this document?")

In [ ]:

```
display_response(list_response)
```

display_response(list_response)

In [ ]:

```
query_engine = vector_index.as_query_engine()
vector_response = query_engine.query("What did the author do growing up?")
```

query_engine = vector_index.as_query_engine()
vector_response = query_engine.query("What did the author do growing up?")

In [ ]:

```
display_response(vector_response)
```

display_response(vector_response)

In [ ]:

```
query_engine = keyword_table_index.as_query_engine()
keyword_response = query_engine.query(
  "What did the author do after his time at YC?"
)
```

query_engine = keyword_table_index.as_query_engine()
keyword_response = query_engine.query(
  "What did the author do after his time at YC?"
)

In [ ]:

```
display_response(keyword_response)
```

display_response(keyword_response)

Dynamo DB Docstore Demo

MongoDB Demo