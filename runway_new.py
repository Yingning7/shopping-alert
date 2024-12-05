from bs4 import BeautifulSoup
import requests


def fetch_html(item_id: str) -> str:
    url = f'https://runway-webstore.com/ap/item/i/m/{item_id}'
    resp = requests.get(url)
    if resp.status_code != 200:
        raise RuntimeError(f'Error when fetching HTML from {url} for Item ID: {item_id}.')
    html = resp.text
    return html


def extract_data(html: str) -> list[dict[str, int | float | str]]:
    soup = BeautifulSoup(html, features='html.parser')
    name = soup.find('h1',{'class', 'item_detail_productname'}).text.strip()
    brand = soup.find('p', {'class', 'item_detail_brandname'}).text.strip()
    if soup.find('p', {'class', 'proper'}):
        original_price = soup.find('p', {'class', 'proper'}).text.replace(',', '').replace('円(税込)', '').strip()
        current_price = original_price
    else:
        original_price = soup.find('del').text.replace(',', '').replace('円(税込)', '').strip()
        current_price = soup.find('span', {'class', 'sale_price'}).text.replace(',', '').replace('円(税込)', '').strip()
    currency = 'JPY'
    detail_ul = soup.find('ul', {'class': 'shopping_area_ul_01'})
    color_lis = detail_ul.find_all('li', recursive=False)
    data = []
    for color_li in color_lis:
        color = color_li.div.dl.dd.text.strip()
        spec_lis = color_li.find('div', {'class': 'choose_item'}).find('ul', {'class': 'shopping_area_ul_02'}).find_all('li', recursive=False)
        for spec_li in spec_lis:
            size = spec_li.dt.text.strip()
            status = spec_li.dd.text.strip()
        data.append(
            {
                'name': name,
                'brand': brand,
                'original_price': original_price,
                'current_price': current_price,
                'currency': currency,
                'color': color,
                'size': size,
                'status': status
            }
        )
    return data
