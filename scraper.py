import requests as rq
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin

category_url = 'http://books.toscrape.com/catalogue/category/books/young-adult_21/index.html' #'http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'
category_url2 = 'http://books.toscrape.com/catalogue/category/books/classics_6/index.html'
catalogue_url = 'http://books.toscrape.com/catalogue/'

def get_book_data(url, category):
    page = rq.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')

    title = soup.find('title').text
    thumbnail = soup.find('img')
    
    trs = soup.find_all('tr')
    for tr in trs:
        th = tr.find('th').text
        td = tr.find('td').text
        if th == 'UPC':
            #print("Found UPC")
            upc = td
            #print(upc)
        elif th == 'Price (excl. tax)':
            price_exc = td
        elif th == 'Price (incl. tax)':
            price_inc = td
        elif th == 'Availability':
            num_available = td
    
    description = soup.find('meta', attrs = {'name': 'description'}).get('content')
    review_rating = soup.find_all('p')[2]
    if review_rating.has_attr('class'):
        review_rating = review_rating['class'][1]
    
    book_data = {
            'product_page_url': url, 
            'upc': upc, 
            'title': title, 
            'price_including_tax': price_inc, 
            'price_excluding_tax': price_exc,
            'number_available': num_available,
            'product_description': description, 
            'category': category,
            'review_rating': review_rating,
            'image_url': thumbnail['src']
        }
    #print(book_data)
    return book_data

def get_books_from_page(url, soup):
    ### Variables locals ???
    pods = soup.find_all('article', attrs = {'class': 'product_pod'})
    book_urls = []
    for pod in pods:
        href = pod.find('a')['href']
        if href.startswith('../'):
            href = urljoin(url, href)
        book_urls.append(href)
    return book_urls


if __name__ == "__main__":
    book_datas = []

    current_url = category_url2
    page = rq.get(current_url)
    soup = BeautifulSoup(page.text, 'html.parser')
    next = soup.find('li', class_ = 'next')
    suf = 'index.html'
    
    while next:
        print(current_url)
        for url in get_books_from_page(current_url, soup):
            book_datas.append(get_book_data(url, "Young Adult"))
        
        href = next.find('a')['href']
        current_url = current_url.replace(suf, href)
        page = rq.get(current_url)
        soup = BeautifulSoup(page.text, 'html.parser')
        suf = href
        next = soup.find('li', class_ = 'next')
        
    print(current_url)
    for url in get_books_from_page(current_url, soup):
            book_datas.append(get_book_data(url, "Young Adult"))

    with open("test.csv", mode="w",newline='', encoding= 'utf-8') as csv_file:
        # csv_file = open("test.csv", mode="w",newline='')
        csv_file.write('sep=,\n')

        data = {
            'product_page_url': 'product_page_url', 
            'upc': 'upc', 
            'title': 'title', 
            'price_including_tax': 'price_including_tax', 
            'price_excluding_tax': 'price_excluding_tax',
            'number_available': 'number_available',
            'product_description': 'product_description', 
            'category': 'category',
            'review_rating': 'review_rating',
            'image_url': 'image_url'
        }

        fieldnames = data.keys()
        writer = csv.DictWriter(csv_file, fieldnames= fieldnames)
        writer.writerow(data)

        writer.writerows(book_datas)
