import os
import re
import webbrowser

import requests
from bs4 import BeautifulSoup

paths = [
    'E:\Series\Comedie',
    'E:\Series\Autre'
]
web_url = 'https://www.couchtuner.rocks/tv-shows/'
web_url2 = 'http://www.couch-tuner.la/tv-lists/'
downloaded_list = []
series = []
urls = []
links = []
titles_paths = []
print('\t\tCheck For New Episodes')


def get_paths():
    """
    Get paths of all series in the provided main folders.
    """
    for path in paths:
        names = os.listdir(path)
        for name in names:
            file_name, file_ext = os.path.splitext(name)
            if file_ext == '' or file_ext.startswith('. '):
                titles_paths.append([name, path + '\\' + name])


def get_downloaded_list():
    """
    Get list of latest episode per series.
    """
    file = 'None'
    for title_path in titles_paths:
        # title = title_path[0]
        path = title_path[1]
        try:
            files = os.listdir(path)
            files.sort()
            file = files[-1]

            file_name, file_ext = os.path.splitext(file)

            if len(files) < 1:
                continue

            i = 1
            while file_ext == '' or (file_ext != '.avi' and file_ext != '.mkv' and file_ext != '.mp4'):
                if i < 0:
                    continue

                file = files[-i]
                file_name, file_ext = os.path.splitext(file)
                i += 1
        except:
            print('get_downloaded_list(): Path Error: ' + path + ' : ' + file_name)

        try:
            pattern = re.findall(r'\d+', file_name)

            if file_name.startswith(pattern[0]):
                season = pattern[1]
                episode = pattern[2]
            else:
                season = pattern[0]
                episode = pattern[1]

            number = ('S' + season + 'E' + episode).upper()
            index = file_name.upper().find(number)
            file_name = file_name[:index - 1].strip()  # .replace('.', ' ').strip()
            number = 'Season ' + str(int(season)) + ' Episode ' + str(int(episode))
            downloaded_list.append([file_name, number])

        except:
            print('get_downloaded_list(): File Error: ' + file)


def get_series_urls():
    """
    Get each serie episode list URL.
    """
    try:
        r = requests.get(web_url)
    except:
        try:
            r = requests.get(web_url2)
        except:
            print('\tConnexion error')
            return False

    soup = BeautifulSoup(r.text, 'html.parser')
    _as = soup.find_all('a')
    for _a in _as:
        text = _a.find_all(text=True)
        text = ' '.join(text)
        url = _a.get('href')

        for title_path in titles_paths:
            if text.upper().strip() == title_path[0].upper().strip() and [text, url] not in series:
                series.append([text, url])

    if len(series) < 1:
        print('\tNo new Releases.')
    return True


def get_episodes_urls():
    """
    Get the URLs for not downloaded episodes.
    """
    length = 0
    for serie in series:
        req = requests.get(serie[1])
        soup = BeautifulSoup(req.text, 'html.parser')
        _as = soup.find_all('a')
        print('\r\t' + serie[0] + ' ' * length, sep=' ', end='', flush=True)
        length = len(serie[0])

        for _a in _as:
            text = _a.find_all(text=True)
            text = ' '.join(text)
            url = _a.get('href')

            if serie[0].upper() in text.upper():
                number = text.strip()[text.find('Season'):]
                if len(number) > 1:
                    for episode in downloaded_list:
                        if episode[0].upper() in text.upper():
                            d = re.findall(r'\d+', episode[1])
                            a = re.findall(r'\d+', number)

                            if len(a) < 2:
                                a = (a[0], 0)

                            if len(d) < 2:
                                d = (d[0], 0)

                            se_downloaded = int(d[0])
                            ep_downloaded = int(d[1])
                            se_available = int(a[0])
                            ep_available = int(a[1])

                            if se_downloaded <= se_available and ep_downloaded < ep_available:
                                urls.append((text, url))

    if len(urls) < 1:
        print('\r', end='', flush=True)
        print('\tNothing to download.')
    else:
        print('\r', end='', flush=True)
        print('\tThere {2} {0} new episode{1}.'.format(
            len(urls),
            's' if len(urls) > 1 else '',
            'are' if len(urls) > 1 else 'is'))
        print('\tOpen each episode page to manually start download ...')


def launch_browser():
    """
    Launch browser for each episode.
    """
    for data in urls:
        text, url = data
        if input('\t\t' + text + ' Download ? y/n ') == 'y':
            req = requests.get(url)
            soup = BeautifulSoup(req.text, 'html.parser')
            _as = soup.find_all('a')

            for a in _as:
                link_text = a.find_all(text=True)
                link_text = ' '.join(link_text).strip()

                if len(link_text) > 0:
                    if link_text.strip().startswith(text.strip()):
                        link = a.get('href')
                        link = get_video_url(link)
                        links.append(link)

    if len(links) > 0:
        for link in links:
            webbrowser.open(link, new=2)


def get_video_url(page_url):
    """
    Get the video URL, to be launched.
    :param page_url: Video web page.
    :return video_url: Video file URL.
    """
    req = requests.get(page_url)
    soup = BeautifulSoup(req.text, 'html.parser')
    iframes = soup.find_all('iframe')

    for iframe in iframes:
        video_url = iframe.get('src')
        if 'openload' in video_url:
            return video_url

    return page_url


def main():
    print('\tGet latest downloaded episodes in local folders ...')
    get_paths()
    get_downloaded_list()

    print('\tGet new releases list from website ...')
    if get_series_urls():
        print('\tCheck if there are new episodes to download ...')
        get_episodes_urls()
        launch_browser()
    input('\tPress Enter to exit.')


if __name__ == "__main__":
    main()
