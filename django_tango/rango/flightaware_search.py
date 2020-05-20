# apikey = "AIzaSyBmhK8bY--C0JvQY-2TTraYY7MZctIOKMk"
# https://flightaware.com/live/flight/N848UP/history
import json
import urllib.parse
import urllib.request
import os


def read_flightaware_key():

    flightaware_api_key = None

    try:
        with open("search.key", "r") as f:
            flightaware_api_key = f.readline().strip()
    except:
        raise IOError("search.key file not found")

    return flightaware_api_key


def run_query(search_terms):

    flightaware_api_key = read_flightaware_key()

    if not flightaware_api_key:
        raise KeyError("Flightaware key not found")

    root_url = "https://www.googleapis.com/customsearch/v1?"

    # cseID = "006766164342167206996:ycrqsfyn7gx"
    cseID = "006766164342167206996:osoigujjicr"
    query_string = urllib.parse.quote(search_terms)

    search_url = ("{root_url}key={key}&cx={searchID}&q={query}").format(
        root_url=root_url, key=flightaware_api_key, searchID=cseID, query=query_string
    )

    results = []

    try:
        response = urllib.request.urlopen(search_url).read().decode("utf-8")
        json_response = json.loads(response)

        for post in json_response["items"]:
            results.append(
                {
                    "title": post["title"],
                    "link": post["link"],
                    "summary": post["snippet"][:400],
                }
            )
    except:
        print("Error when querying the Flightaware API")

    return results


if __name__ == "__main__":
    airplane_posts = run_query("N849UP")
    for post in airplane_posts:
        print(post["title"])
        print(post["summary"])
        print(" ")
