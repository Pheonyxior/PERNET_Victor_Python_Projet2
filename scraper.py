import requests as rq
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin
import shutil
import os

site_to_scrape = 'http://books.toscrape.com/index.html'
site_prefix = 'http://books.toscrape.com/'
output_dir = 'C:/PERNET_Victor_Python_Projet2/'


def get_book_data(url, category):
    page = rq.get(url)
    page.encoding = 'utf-8'
    soup = BeautifulSoup(page.text, 'html.parser', from_encoding= 'utf-8')
    
    title = soup.find('h1').text
    thumbnail = urljoin(site_prefix, soup.find('img')['src']) 
    print(title)
    
    # handles saving the book covers
    cover_dir = output_dir + 'covers/'
    if not os.path.exists(cover_dir):
        os.makedirs(cover_dir)
    category_dir = cover_dir + category + '/'
    if not os.path.exists(category_dir):
        os.makedirs(category_dir)
    
    response = rq.get(thumbnail, stream=True)

    file_name = thumbnail
    file_name = os.path.basename(file_name)

    with open(os.path.join(category_dir, file_name), 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)

    del response
    
    trs = soup.find_all('tr')
    for tr in trs:
        th = tr.find('th').text
        td = tr.find('td').text
        if th == 'UPC':
            upc = td
        elif th == 'Price (excl. tax)':
            #td = td[1: len(th)] Uncomment to remove £ sign
            price_exc = td
        elif th == 'Price (incl. tax)':
            #td = td[1: len(th)] Uncomment to remove £ sign
            price_inc = td
        elif th == 'Availability':
            num_available = td
    
    description = soup.find('meta', attrs = {'name': 'description'}).get('content').strip()
    
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
            'image_url': thumbnail
        }
    return book_data


def get_books_from_page(url, soup):
    pods = soup.find_all('article', attrs = {'class': 'product_pod'})
    book_urls = []
    for pod in pods:
        href = pod.find('a')['href']
        if href.startswith('../'):
            href = urljoin(url, href)
        book_urls.append(href)
    return book_urls


def get_books_from_category(url, category):
    book_datas = []
    
    current_url = url
    page = rq.get(current_url)
    soup = BeautifulSoup(page.text, 'html.parser')
    next = soup.find('li', class_ = 'next')
    suf = 'index.html'
    
    # Loops as long as a next button for the next page is found
    while next:
        print(category)
        for url in get_books_from_page(current_url, soup):
            book_datas.append(get_book_data(url, category))
        print('\n')

        href = next.find('a')['href']
        current_url = current_url.replace(suf, href)
        page = rq.get(current_url)
        soup = BeautifulSoup(page.text, 'html.parser')
        suf = href
        next = soup.find('li', class_ = 'next')

    # Executes at least once for the page where no next is found, meaning the last one.
    print(category)
    for url in get_books_from_page(current_url, soup):
        book_datas.append(get_book_data(url, category))

    return book_datas


if __name__ == "__main__":

    all_books_datas = []

    page = rq.get(site_to_scrape)
    soup = BeautifulSoup(page.text, 'html.parser')

    sides = soup.find('div', attrs= {'class': 'side_categories'})
    categories = sides.find_all('a')

    # To get only books from a single category /!\ this will overwrite existing csv and images at default extract location
    all_books_datas.extend(get_books_from_category(
            'http://books.toscrape.com/catalogue/category/books/philosophy_7/index.html', 'Philosophy'))

    # we use len to start from index 1 and skip the "Books" category at index 0
    # for i in range(1, len(categories)):
    #     category = categories[i]

    #     url = site_prefix + category['href']
    #     name = category.text.strip()
    #     all_books_datas.extend(get_books_from_category(url, name))

    print("book amount : ", len(all_books_datas))

    with open(os.path.join(output_dir, "Book Datas.csv"), mode="w",newline= '', encoding= 'utf-8') as csv_file:

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
        writer = csv.DictWriter(csv_file, fieldnames= fieldnames, delimiter=';')
        writer.writerow(data)

        writer.writerows(all_books_datas)
