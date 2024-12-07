import click

from main import (
    fetch_webpage,
    parse_towns_url,
    get_data_for_town,
    save_to_csv,
)


@click.group()
def cli():
    """
    CLI nástroj pro zpracování volebních dat.
    """
    pass


@cli.command()
@click.argument("url", type=str)
@click.argument("output_path", type=click.Path(writable=True))
def fetch_data(url: str, output_path: str):
    """
    Stáhne volební data z URL a uloží je do souboru CSV.

    \b
    URL: Odkaz na stránku s volebními výsledky.
    OUTPUT_PATH: Cesta k výstupnímu CSV souboru.
    """
    click.echo(f"Stahuji data z: {url}")
    try:
        html_content = fetch_webpage(url)
        town_urls = parse_towns_url(html_content)
        data = []

        for town_url in town_urls:
            full_url = f"https://www.volby.cz/pls/ps2017nss/{town_url}"
            try:
                click.echo(f"Zpracovávám: {full_url}")
                town_data = get_data_for_town(full_url)
                data.append(town_data)
            except Exception as e:
                click.echo(f"Chyba při zpracování URL {full_url}: {e}", err=True)

        if data:
            save_to_csv(data, output_path)
            click.echo(f"Data byla uložena do {output_path}")
        else:
            click.echo("Nebyla nalezena žádná data k uložení.", err=True)

    except Exception as e:
        click.echo(f"Nastala chyba: {e}", err=True)


@cli.command()
@click.argument("url", type=str)
def list_towns(url: str):
    """
    Vypíše seznam URL jednotlivých obcí ze zadané stránky.

    \b
    URL: Odkaz na stránku s volebními výsledky.
    """
    click.echo(f"Stahuji seznam obcí z: {url}")
    try:
        html_content = fetch_webpage(url)
        town_urls = parse_towns_url(html_content)
        click.echo("Seznam obcí:")
        for town_url in town_urls:
            click.echo(f"https://www.volby.cz/pls/ps2017nss/{town_url}")
    except Exception as e:
        click.echo(f"Nastala chyba: {e}", err=True)


if __name__ == "__main__":
    cli()
