from bs4 import BeautifulSoup
import requests
import operator


def find_paths(content):
    result = set()
    for item in content:
        path = item['href']
        if operator.contains(path, "http") or operator.contains(path, "?"):
            continue
        result.add(path)
    return result


def print_item(items):
    for item in items:
        print(item)


if __name__ == '__main__':
    url = 'https://auspost.com.au/'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    paths = find_paths(soup.find_all('a'))
    paths.update(find_paths(soup.find_all('link')))
    print_item(sorted(paths))
