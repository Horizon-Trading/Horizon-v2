from .fetch import fetch_news
from .process import process_news


def main():
    articles = fetch_news()

    for article in articles:
        process_news(article)


if __name__ == "__main__":
    main()
