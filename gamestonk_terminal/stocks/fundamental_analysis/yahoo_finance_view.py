""" Yahoo Finance View """
__docformat__ = "numpy"

import os
import webbrowser
import matplotlib.pyplot as plt
import pandas as pd
from tabulate import tabulate

from gamestonk_terminal.stocks.fundamental_analysis import yahoo_finance_model
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import export_data, plot_autoscale
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.rich_config import console


def open_headquarters_map(ticker: str):
    """Headquarters location of the company
    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    """
    webbrowser.open(yahoo_finance_model.get_hq(ticker))
    console.print("")


def open_web(ticker: str):
    """Website of the company
    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    """
    webbrowser.open(yahoo_finance_model.get_website(ticker))
    console.print("")


def display_info(ticker: str):
    """Yahoo Finance ticker info
    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    """
    summary = ""
    df_info = yahoo_finance_model.get_info(ticker)
    if "Long business summary" in df_info.index:
        summary = df_info.loc["Long business summary"].values[0]
        df_info = df_info.drop(index=["Long business summary"])

    if gtff.USE_TABULATE_DF:
        console.print(
            tabulate(df_info, headers=[], showindex=True, tablefmt="fancy_grid")
        )

    else:
        console.print(df_info.to_string(header=False))

    if summary:
        console.print("Business Summary:")
        console.print(summary)

    console.print("")


def display_shareholders(ticker: str):
    """Yahoo Finance ticker shareholders
    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    """
    (
        df_major_holders,
        df_institutional_shareholders,
        df_mutualfund_shareholders,
    ) = yahoo_finance_model.get_shareholders(ticker)

    dfs = [df_major_holders, df_institutional_shareholders, df_mutualfund_shareholders]
    titles = ["Major Holders:\n", "Institutuinal Holders:\n", "Mutual Fund Holders:\n"]
    console.print("")
    for df, title in zip(dfs, titles):
        console.print(title)
        if gtff.USE_TABULATE_DF:
            console.print(
                tabulate(df, headers=df.columns, tablefmt="fancy_grid", showindex=False)
            )
        else:
            console.print(df.to_string(index=False))
        console.print("")


def display_sustainability(ticker: str):
    """Yahoo Finance ticker sustainability
    Parameters
    ----------
    other_args : List[str]
        argparse other args
    ticker : str
        Fundamental analysis ticker symbol
    """

    df_sustainability = yahoo_finance_model.get_sustainability(ticker)

    if df_sustainability.empty:
        console.print("No sustainability data found.", "\n")
        return

    if gtff.USE_TABULATE_DF:
        console.print(
            tabulate(
                df_sustainability,
                headers=[],
                tablefmt="fancy_grid",
                showindex=True,
            )
        )
    else:
        console.print(df_sustainability.to_string(index=True))
    console.print("")


def display_calendar_earnings(ticker: str):
    """Yahoo Finance ticker calendar earnings
    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    """
    df_calendar = yahoo_finance_model.get_calendar_earnings(ticker).T
    if df_calendar.empty:
        console.print("No calendar events found.\n")
        return
    if gtff.USE_TABULATE_DF:
        console.print(
            tabulate(
                df_calendar,
                showindex=False,
                headers=df_calendar.columns,
                tablefmt="fancy_grid",
            )
        )
    else:
        console.print(df_calendar.to_string(index=False))
    console.print("")


def display_dividends(
    ticker: str, limit: int = 12, plot: bool = False, export: str = ""
):
    """Display historical dividends
    Parameters
    ----------
    ticker: str
        Stock ticker
    limit: int
        Number to show
    plot: bool
        Plots hitsorical data
    export: str
        Format to export data
    """
    div_history = yahoo_finance_model.get_dividends(ticker)
    if div_history.empty:
        console.print("No dividends found.\n")
        return
    div_history["Dif"] = div_history.diff()
    div_history = div_history[::-1]
    if plot:
        fig, ax = plt.subplots(
            figsize=plot_autoscale(), constrained_layout=False, dpi=PLOT_DPI
        )
        ax.plot(
            div_history.index,
            div_history["Dividends"],
            ls="-",
            linewidth=0.75,
            marker=".",
            markersize=4,
            mfc="k",
            mec="k",
            c="k",
            alpha=1,
        )
        ax.set_xlabel("Date")
        ax.set_ylabel("Amount ($)")
        ax.set_title(f"Dividend History for {ticker}")
        ax.set_xlim(div_history.index[-1], div_history.index[0])
        if gtff.USE_ION:
            plt.ion()
        fig.tight_layout()
        plt.show()
    else:
        div_history.index = pd.to_datetime(div_history.index, format="%Y%m%d").strftime(
            "%Y-%m-%d"
        )
        if gtff.USE_TABULATE_DF:
            console.print(
                tabulate(
                    div_history.head(limit),
                    tablefmt="fancy_grid",
                    headers=["Amount Paid ($)", "Change"],
                    floatfmt=".2f",
                )
            )
        else:
            console.print(div_history.to_string())
    console.print("")
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "divs", div_history)
