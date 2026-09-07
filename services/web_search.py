from ddgs import DDGS


def search_web(
    query: str
):

    try:

        with DDGS() as ddgs:

            results = list(
                ddgs.text(
                    query,
                    max_results=3
                )
            )

    except Exception as exc:

        return (
            "Web search failed: "
            f"{str(exc)}"
        )

    if not results:

        return (
            "No results found."
        )

    text = ""

    for result in results:

        text += (
            "\n"
            f"Title: "
            f"{result.get('title', '')}\n"
            f"Body: "
            f"{result.get('body', '')}\n"
            f"URL: "
            f"{result.get('href', '')}\n"
        )

    return text
