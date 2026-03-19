from collections import defaultdict


def reciprocal_rank_fusion(results, k=60):

    scores = defaultdict(float)
    doc_map = {}

    for docs in results:

        for rank, doc in enumerate(docs):

            key = doc.page_content

            scores[key] += 1 / (k + rank)
            doc_map[key] = doc

    sorted_docs = sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return [doc_map[key] for key, _ in sorted_docs]