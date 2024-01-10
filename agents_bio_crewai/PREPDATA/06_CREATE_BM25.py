
from langchain.document_loaders import DirectoryLoader
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

loader = DirectoryLoader('./', glob="./genomes_txt/*.text", loader_cls=TextLoader)

documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    separators = ["\n"],
    keep_separator = False,
    strip_whitespace=True,   ### DOES NOT SEEM TO WORK
    chunk_size = 0,    # just splits on lines (separators)
    chunk_overlap  = 0,
    length_function = len,
    is_separator_regex = False,
    add_start_index = True,
)
docs = text_splitter.split_documents(documents)
bmtexts = [ doc.page_content for doc in docs ]
# print(bmtexts[0])

with open("genomes.bm25","w") as f:
    for line in bmtexts:
        print(line.strip(), file=f)

# prove we can find relevant docs
from langchain.retrievers import BM25Retriever, EnsembleRetriever
bm25_retriever = BM25Retriever.from_texts(bmtexts)
bm25_retriever.k = 3
query = "What is the name of the genome with ID 83332.12 ?"
docs = bm25_retriever.get_relevant_documents(query, k=4)  # k=8 is default
docs_page_content = " ".join([d.page_content for d in docs])
print("DOCS")
print(docs_page_content)
