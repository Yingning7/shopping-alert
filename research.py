from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


if __name__ == '__main__':
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto('https://zozo.jp/shop/mercuryduo/goods-sale/87837454/?did=142436883')
        html = page.content()
        browser.close()
    
    soup = BeautifulSoup(html, features='html.parser')
    details_div = soup.find('div', {'class': 'cartBlock clearfix', 'data-goods-skus': 'list'})
    print(details_div)

with open('page.html', 'w') as fp:
    fp.write(html)


