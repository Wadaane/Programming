import os
import re
import webbrowser

import requests
from bs4 import BeautifulSoup

paths = [
    'E:\Series\Comedie',
    'E:\Series\Autre'
]
# web_url = 'https://www.couchtuner.onl/new-releases-2'
web_url = 'http://www.couch-tuner.la/tv-lists/'
downloaded_list = []
series = []
urls = []
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

            if len(files) == 1:
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


def get_series_list():
    """
    Get list of new releases.
    """
    try:
        r = requests.get(web_url)
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
            if text.upper().startswith(title_path[0].upper()) and [text, url] not in series:
                series.append([text, url])
                # print(text, url)
    if len(series) < 1:
        print('\tNo new Releases.')
    return True


def get_urls():
    """
    Get the URLs for not downloaded episodes.
    """
    for serie in series:
        req = requests.get(serie[1])
        soup = BeautifulSoup(req.text, 'html.parser')
        _as = soup.find_all('a')

        for _a in _as:
            text = _a.find_all(text=True)
            text = ' '.join(text)
            url = _a.get('href')

            if serie[0] in text:
                number = text.strip()[text.find('Season'):]
                if len(number) > 1:
                    for episode in downloaded_list:
                        if episode[0] in text:
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
                                # if input('\t\t' + text + ' Download ? y/n ') == 'y':
                                urls.append((text, url))

    if len(urls) < 1:
        print('\tNothing to download.')
    else:
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

                if len(link_text) > 0:
                    if text in link_text[0]:
                        link = a.get('href')
                        link = get_video_url(link)
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
    if get_series_list():
        # get_episodes_list()
        print('\tCheck if there is new episodes to download ...')
        get_urls()
        launch_browser()
    input('\tPress Enter to exit.')


if __name__ == "__main__":
    main()
