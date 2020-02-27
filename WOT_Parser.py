import string
import requests
import pandas as pd
from bs4 import BeautifulSoup

def give_sex(url, sex):
    "Return url for category (e.g. Sex)"
    return url[:-6] + sex

def get_html(url):
    "Return html file as text"
    r = requests.get(url)
    return r.text

def get_alphabet():
    """
    Return List of Uppercase
    latters (ENG alphabet)
    """
    return list(string.ascii_uppercase)
    
def get_all_charcters_urls(lat_url):
    """
    Return list of characters
    URLs for a latter
    """
    html = get_html(lat_url)
    base_url = lat_url.split('/wiki/')[0] # 'https://wot.fandom.com'
    soup = BeautifulSoup(html, 'html.parser')
    chars = soup.find('ul', class_="category-page__members-for-char")\
                .find_all('a', class_="category-page__member-link")
    return [base_url + a.get('href') for a in chars]

def give_values(name, soup):
    """
    Return values from
    character summary table
    """
    div_class = "pi-data-value pi-font"
    return [name] + [feature.text.replace('\xa0', ':') for feature in
                             soup.find_all('div', class_=div_class)]

def give_features(soup):
    """
    Return features from
    character summary table
    """
    h3_class = "pi-data-label pi-secondary-font"
    return ['Name'] + [feature.text for feature in
                 soup.find_all('h3', class_=h3_class)]

def parse_char_page(url):
    """
    Parse one character
    page and return pandas dataframe
    """
    html = get_html(url)
    soup = BeautifulSoup(html, 'html.parser')
    try:
        h2_class = "pi-item pi-item-spacing pi-title"
        name = soup.find('h2', class_=h2_class).next
    except:
        name = url.split('/')[-1]
        return pd.DataFrame({'Name':name},index=[0])
    values = give_values(name, soup)
    features = give_features(soup)
    return pd.DataFrame({f'{key}':value for key, value in zip(features, values)}, index=[0])

def parse_category(sex_url):
    """
    Parse one category value and
    return pandas dataframe
    with all characters
    """
    df = pd.DataFrame()
    for latter in get_alphabet():
        lat_url = sex_url + f'?from={latter}'
        urls = get_all_charcters_urls(lat_url)
        for url in urls:
            df = df.append(parse_char_page(url), sort=False)
            print(df.Name.values[-1])
    return df

if __name__=='__main__':
    url = 'https://wot.fandom.com/wiki/Category:People'
    categories = [give_sex(url, gender) for gender in ['Women', 'Men']]
    df = parse_category(categories[0])\
        .append(parse_category(categories[1]))
    df.to_csv('~/Desktop/WOT.tsv', sep='\t',index=False)
