from ingestion.classifier import classify_chunk


def route_query(query):

    class Dummy:
        page_content = query

    topic = classify_chunk(Dummy())

    return topic