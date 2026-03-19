from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_documents(docs):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=120
    )

    chunks = splitter.split_documents(docs)

    print("Total chunks created:", len(chunks))

    return chunks