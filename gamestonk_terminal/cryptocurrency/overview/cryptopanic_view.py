"""Cryptopanic view"""
__docformat__ = "numpy"

import os
from typing import Optional

from tabulate import tabulate
from gamestonk_terminal.helper_funcs import export_data
from gamestonk_terminal.cryptocurrency.overview import cryptopanic_model
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.rich_config import console


def display_news(
    post_kind: str = "news",
    region: str = "en",
    filter_: Optional[str] = None,
    top: int = 25,
    sortby: str = "published_at",
    descend: bool = False,
    links: bool = False,
    export: str = "",
) -> None:
    """Display recent posts from CryptoPanic news aggregator platform. [Source: https://cryptopanic.com/]

    Parameters
    ----------
    top: int
        number of news to display
    post_kind: str
        Filter by category of news. Available values: news or media.
    filter_: Optional[str]
        Filter by kind of news. One from list: rising|hot|bullish|bearish|important|saved|lol
    region: str
        Filter news by regions. Available regions are: en (English), de (Deutsch), nl (Dutch), es (Español),
        fr (Français), it (Italiano), pt (Português), ru (Русский)
    sortby: str
        Key to sort by.
    descend: bool
        Sort in descending order.
    links: bool
        Show urls for news
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = cryptopanic_model.get_news(
        limit=top, post_kind=post_kind, filter_=filter_, region=region
    ).sort_values(by=sortby, ascending=descend)

    if not links:
        df.drop("link", axis=1, inplace=True)
    else:
        df = df[["title", "link"]]

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df.head(top),
                headers=df.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            ),
            "\n",
        )
    else:
        console.print(df.to_string, "\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "news",
        df,
    )
