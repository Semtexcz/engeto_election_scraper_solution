import csv
import sys
from pathlib import Path
from typing import Dict, List
from urllib.parse import urlparse, parse_qs

import click
import requests
from bs4 import BeautifulSoup
from bs4.element import ResultSet
from loguru import logger

logger.remove()  # Odstraní výchozí konfiguraci loggeru
logger.add(sys.stdout, level="INFO")  # Přidá handler pro konzoli s úrovní INFO


def fetch_webpage(url: str) -> str:
    """
    Stáhne obsah webové stránky.

    :param url: URL stránky, kterou chceme zpracovat.
    :return: HTML obsah stránky.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        click.echo(f"Chyba při stahování stránky: {e}", err=True)
        raise


def extract_town_code_from_url(url: str) -> str:
    """
    Extrahuje kód obce z URL.

    :param url: URL obsahující parametry obce.
    :return: Kód obce.
    """
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    return query_params["xobec"][0]


def extract_town_name(soup: BeautifulSoup) -> str:
    """
    Získá název města ze stránky.

    :param soup: BeautifulSoup objekt reprezentující HTML stránku.
    :return: Název města.
    """
    return soup.select_one("#publikace > h3:nth-child(4)").text.split(":")[1].strip()


def extract_integer(soup: BeautifulSoup, selector: str) -> int:
    """
    Extrahuje celé číslo z prvku vybraného pomocí CSS selektoru.

    :param soup: BeautifulSoup objekt reprezentující HTML stránku.
    :param selector: CSS selektor prvku obsahujícího požadované číslo.
    :return: Extrahované číslo jako int.
    """
    text = soup.select_one(selector).text
    text = ''.join(char for char in text if char.isnumeric())
    return int(text)


def extract_voters(soup: BeautifulSoup) -> int:
    """
    Získá počet registrovaných voličů.

    :param soup: BeautifulSoup objekt reprezentující HTML stránku.
    :return: Počet registrovaných voličů.
    """
    selector = "table tr:nth-child(3) td:nth-child(4)"
    return extract_integer(soup, selector)


def extract_envelopes_count(soup: BeautifulSoup) -> int:
    """
    Získá počet odevzdaných obálek.

    :param soup: BeautifulSoup objekt reprezentující HTML stránku.
    :return: Počet odevzdaných obálek.
    """
    selector = "table > tr:nth-child(3) > td:nth-child(5)"
    return extract_integer(soup, selector)


def extract_valid_votes(soup: BeautifulSoup) -> int:
    """
    Získá počet platných hlasů.

    :param soup: BeautifulSoup objekt reprezentující HTML stránku.
    :return: Počet platných hlasů.
    """
    selector = "table > tr:nth-child(3) > td:nth-child(8)"
    return extract_integer(soup, selector)


def extract_party(soup: BeautifulSoup) -> str:
    """
    Extrahuje název strany.

    :param soup: BeautifulSoup objekt reprezentující řádek tabulky.
    :return: Název strany.
    """
    return soup.select_one("td:nth-child(2)").text


def extract_parties_votes(soup: BeautifulSoup) -> Dict[str, int]:
    """
    Získá počet hlasů pro jednotlivé strany.

    :param soup: BeautifulSoup objekt reprezentující HTML stránku.
    :return: Slovník s názvy stran jako klíči a počty hlasů jako hodnotami.
    """
    parties = soup.select("#inner tr")
    return {extract_party(party): extract_integer(party, "td:nth-child(3)") for party in parties if is_party_row(party)}


def is_party_row(row: BeautifulSoup) -> bool:
    """
    Určuje, zda řádek tabulky reprezentuje stranu.

    :param row: BeautifulSoup objekt reprezentující řádek tabulky.
    :return: True, pokud řádek reprezentuje stranu, jinak False.
    """
    one = row.select_one("td")
    if not one or "hidden_td" in one.get("class"):
        return False
    return len(row.select("td")) == 5


def parse_election_data(html_content: str) -> Dict[str, any]:
    """
    Analyzuje HTML obsah stránky a extrahuje požadovaná data.

    :param html_content: HTML obsah stránky.
    :return: Slovník obsahující data o volbách.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    data = {
        "town_name": extract_town_name(soup),
        "registered_voters": extract_voters(soup),
        "envelopes_count": extract_envelopes_count(soup),
        "valid_votes": extract_valid_votes(soup),
    }
    data.update(extract_parties_votes(soup))
    return data


def parse_towns_url(html_content: str) -> List[str]:
    """
    Extrahuje URL jednotlivých obcí z HTML stránky.

    :param html_content: HTML obsah stránky.
    :return: Seznam URL obcí.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    towns: ResultSet = soup.select("td.cislo")
    return [town.a.get("href") for town in towns]


def save_to_csv(data: List[Dict[str, any]], output_path: str) -> None:
    """
    Uloží data do CSV souboru.

    :param data: Seznam dat, která mají být uložena.
    :param output_path: Cesta k výstupnímu CSV souboru.
    """
    try:
        # Validace cesty
        output_file = Path(output_path)
        if not output_file.parent.exists():
            click.echo(f"Chyba: Výstupní složka '{output_file.parent}' neexistuje.", err=True)
            return

        # Uložení dat do CSV
        with output_file.open(mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        click.echo(f"Data byla úspěšně uložena do: {output_file}")
    except Exception as e:
        click.echo(f"Chyba při ukládání do CSV: {e}", err=True)
        raise


def get_data_for_town(town_url: str) -> Dict[str, any]:
    """
    Získá data o volbách pro konkrétní obec.

    :param town_url: URL obce.
    :return: Slovník obsahující data o obci.
    """
    logger.info(f"Zpracovávám data pro {town_url}")
    html_content = fetch_webpage(town_url)
    data = parse_election_data(html_content)
    town_code = extract_town_code_from_url(town_url)
    data.update({"town_code": town_code})
    logger.debug(data)
    return data


def main(url, output_path):
    urls = parse_towns_url(fetch_webpage(url))
    data = []
    for town_url in urls:
        try:
            town_url = f"https://www.volby.cz/pls/ps2017nss/{town_url}"
            data.append(get_data_for_town(town_url))
        except Exception as e:
            logger.error(f"Chyba při zpracování dat: {e}")
            continue
    save_to_csv(data, output_path)


if __name__ == '__main__':
    main("https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103", "output.csv")
    # get_data_for_town("https://www.volby.cz/pls/ps2017nss/ps311?xjazyk=CZ&xkraj=12&xobec=590185&xvyber=7103")
