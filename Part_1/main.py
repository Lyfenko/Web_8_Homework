import json
import re
import redis
from mongoengine import connect, Document, StringField, ListField, ReferenceField

connect(
    host="mongodb+srv://lyfenko:KBATYRj2@cluster0.au6w27m.mongodb.net/database_name?retryWrites=true&w=majority"
)

cache = redis.Redis(host="localhost", port=6379, db=0)


class Author(Document):
    fullname = StringField(required=True, unique=True)
    born_date = StringField()
    born_location = StringField()
    description = StringField()


class Quotes(Document):
    author = ReferenceField(Author)
    tags = ListField(StringField())
    quote = StringField(required=True)


with open("authors.json", "r") as f:
    authors_data = json.load(f)

for author_data in authors_data:
    author = Author(
        fullname=author_data["fullname"],
        born_date=author_data.get("born_date", ""),
        born_location=author_data.get("born_location", ""),
        description=author_data.get("description", ""),
    )
    author.save()


with open("quotes.json", "r") as f:
    quotes_data = json.load(f)

for quote_data in quotes_data:
    author = Author.objects.get(fullname=quote_data["author"])
    quote = Quotes(author=author, tags=quote_data["tags"], quote=quote_data["quote"])
    quote.save()


def search_quotes():
    while True:
        query = input("Enter a search command (name:, tag:, tags:, exit:exit): ")
        query_parts = query.split(":")
        if len(query_parts) != 2:
            print("Invalid query format.")
            continue
        command = query_parts[0].strip()
        value = query_parts[1].strip()
        if command == "exit":
            break
        elif command == "name":
            cache_key = f"name:{value}"
            cached_result = cache.get(cache_key)
            if cached_result:
                print(cached_result.decode("utf-8"))
            else:
                author_query = re.compile(value, re.IGNORECASE)
                authors = Author.objects(fullname=author_query)
                if authors:
                    author_quotes = Quotes.objects(author__in=authors)
                    result = [
                        f"{quote.author.fullname}: {quote.quote}"
                        for quote in author_quotes
                    ]
                    result_str = "\n".join(result)
                    print(result_str)
                    cache.set(cache_key, result_str)
                else:
                    print("No results found.")
        elif command == "tag":
            cache_key = f"tag:{value}"
            cached_result = cache.get(cache_key)
            if cached_result:
                print(cached_result.decode("utf-8"))
            else:
                tag_query = re.compile(value, re.IGNORECASE)
                quotes = Quotes.objects(tags=tag_query)
                if quotes:
                    result = [
                        f"{quote.author.fullname}: {quote.quote}" for quote in quotes
                    ]
                    result_str = "\n".join(result)
                    print(result_str)
                    cache.set(cache_key, result_str)
                else:
                    print("No results found.")
        elif command == "tags":
            tag_values = [v.strip() for v in value.split(",")]
            cache_key = f"tags:{value}"
            cached_result = cache.get(cache_key)
            if cached_result:
                print(cached_result.decode("utf-8"))
            else:
                tag_queries = [re.compile(v, re.IGNORECASE) for v in tag_values]
                quotes = Quotes.objects(tags__in=tag_queries)
                if quotes:
                    result = [f"{q.author.fullname}: {q.quote}" for q in quotes]
                    result_str = "\n".join(result)
                    print(result_str)
                    cache.set(cache_key, result_str)
                else:
                    print("No results found.")
        else:
            print("Invalid command.")


if __name__ == "__main__":
    search_quotes()
