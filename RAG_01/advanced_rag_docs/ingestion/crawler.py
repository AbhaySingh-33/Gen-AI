from langchain_community.document_loaders import RecursiveUrlLoader
from bs4 import BeautifulSoup
from config.settings import DOCS_URL


def crawl_docs():

    loader = RecursiveUrlLoader(
        url=DOCS_URL,
        max_depth=5,
        extractor=lambda x: BeautifulSoup(x, "html.parser").text
    )

    docs = loader.load()

    print("Total pages scraped:", len(docs))

    return docs