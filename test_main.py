import pytest
from bs4 import BeautifulSoup
from requests.exceptions import RequestException, ConnectionError

from main import fetch_webpage, parse_towns_url, extract_town_name, extract_voters


class TestFetchWebpage:
    def test_fetch_webpage_success(self, mocker):
        """
        Testuje, zda funkce správně vrací HTML obsah při úspěšném požadavku.
        """
        url = "http://example.com"
        expected_content = "<html><body><h1>Test</h1></body></html>"

        mock_get = mocker.patch("requests.get", autospec=True)
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.text = expected_content
        mock_get.return_value = mock_response

        result = fetch_webpage(url)
        assert result == expected_content
        mock_get.assert_called_once_with(url)

    def test_fetch_webpage_http_error(self, mocker):
        """
        Testuje, zda funkce správně zpracuje chybu HTTP (např. 404).
        """
        url = "http://example.com"

        mock_get = mocker.patch("requests.get", autospec=True)
        mock_response = mocker.Mock()
        mock_response.raise_for_status.side_effect = RequestException("404 Error")
        mock_get.return_value = mock_response

        with pytest.raises(RequestException):
            fetch_webpage(url)
        mock_get.assert_called_once_with(url)

    def test_fetch_webpage_connection_error(self, mocker):
        """
        Testuje, zda funkce správně zpracuje chybu při připojení.
        """
        url = "http://example.com"

        mock_get = mocker.patch("requests.get", side_effect=ConnectionError)

        with pytest.raises(RequestException):
            fetch_webpage(url)
        mock_get.assert_called_once_with(url)

    def test_fetch_webpage_invalid_url(self, mocker):
        """
        Testuje, zda funkce zpracuje chybu při špatném URL formátu.
        """
        url = "invalid_url"

        mock_get = mocker.patch("requests.get", side_effect=RequestException)

        with pytest.raises(RequestException):
            fetch_webpage(url)
        mock_get.assert_called_once_with(url)


class TestParseTownsUrl:
    def test_parse_towns_url(self):
        """
        Testuje, zda funkce správně extrahuje URL měst.
        """
        html_content = """
        <html>
            <body>
                <table>
                    <tr>
                        <td class="cislo"><a href="url1">Město 1</a></td>
                        <td class="cislo"><a href="url2">Město 2</a></td>
                    </tr>
                </table>
            </body>
        </html>
        """
        expected_urls = ["url1", "url2"]

        result = parse_towns_url(html_content)
        assert result == expected_urls


class TestParseWebpage:
    def test_parse_webpage(self):
        """
        Testuje, zda funkce správně extrahuje data z HTML obsahu.
        """
        html_content = """
        <html>
            <body>
                <div class="example">Data 1</div>
                <div class="example">Data 2</div>
            </body>
        </html>
        """
        # expected_data = ["Data 1", "Data 2"]
        #
        # result = parse_webpage(html_content)
        # assert result == expected_data


class TestExtractTownName:
    def test_extract_town_name_valid_html(self):
        # Testovací HTML obsahující požadovanou strukturu
        html = '''
        <div id="publikace">
            <h3>Item 1</h3>
            <h3>Item 2</h3>
            <h3>Item 3</h3>
            <h3>Název města: Praha</h3>
        </div>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        result = extract_town_name(soup)
        assert result == "Praha"

    def test_extract_town_name_missing_element(self):
        # Testovací HTML, kde chybí požadovaný element
        html = '''
        <div id="publikace">
            <h3>Item 1</h3>
            <h3>Item 2</h3>
            <h3>Item 3</h3>
        </div>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        with pytest.raises(AttributeError):
            extract_town_name(soup)

    def test_extract_town_name_empty_string(self):
        # Testovací HTML s prázdným obsahem
        html = '''
        <div id="publikace">
            <h3>Item 1</h3>
            <h3>Item 2</h3>
            <h3>Item 3</h3>
            <h3>Název města: </h3>
        </div>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        result = extract_town_name(soup)
        assert result == ""  # Očekáváme prázdný string

class TestExtractVoters:
    def test_extract_voters_valid_html(self):
        # Testovací HTML obsahující požadovanou strukturu
        html = '''
        <table id="ps311_t1">
            <tbody>
                <tr>
                    <td>1</td>
                    <td>Item 1</td>
                    <td>100</td>
                    <td>150</td>
                </tr>
                <tr>
                    <td>2</td>
                    <td>Item 2</td>
                    <td>200</td>
                    <td>250</td>
                </tr>
                <tr>
                    <td>3</td>
                    <td>Item 3</td>
                    <td>300</td>
                    <td>350</td>
                </tr>
            </tbody>
        </table>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        result = extract_voters(soup)
        assert result == 350

    def test_extract_voters_missing_element(self):
        # Testovací HTML, kde chybí požadovaný element
        html = '''
        <table id="ps311_t1">
            <tbody>
                <tr>
                    <td>1</td>
                    <td>Item 1</td>
                    <td>100</td>
                </tr>
            </tbody>
        </table>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        with pytest.raises(AttributeError):
            extract_voters(soup)

    # def test_extract_voters_invalid_value(self):
    #     # Testovací HTML s neplatným obsahem v cílové buňce
    #     html = '''
    #     <table id="ps311_t1">
    #         <tbody>
    #             <tr>
    #                 <td>1</td>
    #                 <td>Item 1</td>
    #                 <td>100</td>
    #                 <td>abc</td>
    #             </tr>
    #         </tbody>
    #     </table>
    #     '''
    #     soup = BeautifulSoup(html, 'html.parser')
    #     with pytest.raises(ValueError):
    #         extract_voters(soup)

    def test_extract_voters_empty_html(self):
        # Prázdné HTML bez tabulky
        html = '''
        <div>
            <p>Žádná data</p>
        </div>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        with pytest.raises(AttributeError):
            extract_voters(soup)