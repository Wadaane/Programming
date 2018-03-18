import webbrowser

import requests
from bs4 import BeautifulSoup


def get_web_page(web_url):
    try:
        r = requests.get(web_url)
    except:
        print('\tConnexion error')
        return None

    soup = BeautifulSoup(r.text, 'html.parser')

    return soup


def get_urls(web_page, tag, att, pattern):
    urls = []
    _tags = web_page.findAll(tag, {att: pattern})
    print(_tags)
    for _tag in _tags:
        url = _tag.get('href')
        urls.append(url)

    return urls


def open_links(urls):
    for link in urls:
        webbrowser.open(link, new=2)


def get_video_url(page_url):
    # """
    # Get the video URL, to be launched.
    # :param page_url: Video web page.
    # :return video_url: Video file URL.
    # """
    # req = requests.get(page_url)
    # soup = BeautifulSoup(req.text, 'html.parser')
    # iframes = soup.find_all('iframe')
    #
    # for iframe in iframes:
    #     video_url = iframe.get('src')
    #     if 'openload' in video_url:
    #         return video_url
    #
    # return page_url
    pass


def main():
    url = input('Please Enter URL: ')
    tag = input('Please Enter the TAG: ')
    att = input('Please Enter the Attribute: ')
    pattern = input('Please Enter the Pattern: ')

    # print(url, tag, att, pattern)

    page = get_web_page(url)
    if page is not None:
        urls = get_urls(page, tag, att, pattern)
        open_links(urls)
    else:
        print('page is None')


if __name__ == "__main__":
    main()
