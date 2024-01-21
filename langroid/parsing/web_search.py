"""
Utilities for web search.

NOTE: Using Google Search requires setting the GOOGLE_API_KEY and GOOGLE_CSE_ID
environment variables in your `.env` file, as explained in the
[README](https://github.com/langroid/langroid#gear-installation-and-setup).
"""

import json
import os
from typing import Dict, List

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from googleapiclient.discovery import Resource, build
from requests.models import Response


class WebSearchResult:
    """
    Class representing a Web Search result, containing the title, link,
    summary and full content of the result.
    """

    def __init__(
        self,
        title: str,
        link: str,
        max_content_length: int = 3500,
        max_summary_length: int = 300,
    ):
        """
        Args:
            title (str): The title of the search result.
            link (str): The link to the search result.
            max_content_length (int): The maximum length of the full content.
            max_summary_length (int): The maximum length of the summary.
        """
        self.title = title
        self.link = link
        self.max_content_length = max_content_length
        self.max_summary_length = max_summary_length
        self.full_content = self.get_full_content()
        self.summary = self.get_summary()

    def get_summary(self) -> str:
        return self.full_content[: self.max_summary_length]

    def get_full_content(self) -> str:
        response: Response = requests.get(self.link)
        soup: BeautifulSoup = BeautifulSoup(response.text, "lxml")
        text = " ".join(soup.stripped_strings)
        return text[: self.max_content_length]

    def __str__(self) -> str:
        return f"Title: {self.title}\nLink: {self.link}\nSummary: {self.summary}"

    def to_dict(self) -> Dict[str, str]:
        return {
            "title": self.title,
            "link": self.link,
            "summary": self.summary,
            "full_content": self.full_content,
        }


def google_search(query: str, num_results: int = 5) -> List[WebSearchResult]:
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    cse_id = os.getenv("GOOGLE_CSE_ID")
    service: Resource = build("customsearch", "v1", developerKey=api_key)
    raw_results = (
        service.cse().list(q=query, cx=cse_id, num=num_results).execute()["items"]
    )

    return [
        WebSearchResult(result["title"], result["link"], 3500, 300)
        for result in raw_results
    ]


def metaphor_search(query: str, num_results: int = 5) -> List[WebSearchResult]:
    """
    Method that makes a POST to request to Metaphor API that queries
    the top num_results links that matches the query. Returns a list
    of WebSearchResult objects.

    Args:
        query (str): The query body that users wants to make.
        num_results (int): Number of top matching results that we want
            to grab
    """

    load_dotenv()

    url = "https://api.metaphor.systems/search"
    api_key = os.getenv("METAPHOR_API_KEY")
    if not api_key:
        raise ValueError(
            """
            METAPHOR_API_KEY is not set. 
            Please set the METAPHOR_API_KEY environment variable.
            """
        )

    payload = {
        "query": query,
        "numResults": num_results,
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "x-api-key": api_key,
    }

    response = requests.post(url, json=payload, headers=headers)
    raw_results = json.loads(response.text)["results"]

    return [
        WebSearchResult(result["title"], result["url"], 3500, 300)
        for result in raw_results
    ]
