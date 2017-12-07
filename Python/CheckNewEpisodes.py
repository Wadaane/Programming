import os
import re
import webbrowser

import requests
from bs4 import BeautifulSoup
from sys import exit

paths = [
    'E:\Series\Comedie',
    'E:\Series\Autre'
]
downloaded_list = []
series = []
urls = []
titles_paths = []


# Get paths of all series in the provided main folders.
def get_paths():
    for path in paths:
        names = os.listdir(path)
        for name in names:
            file_name, file_ext = os.path.splitext(name)
            if file_ext == '':
                titles_paths.append([name, path + '\\' + name])
    

# Get list of latest episodes we already have.
def get_downloaded_list():
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
            season = pattern[0]
            episode = pattern[1]
            number = ('S' + season + 'E' + episode).upper()
            index = file_name.upper().find(number)
            file_name = file_name[:index].replace('.', ' ').strip()
            number = 'Season ' + str(int(season)) + ' Episode ' + str(int(episode))
            downloaded_list.append([file_name, number])
        except:
            print('get_downloaded_list(): File Error: ' + file)


# Get list of new releases.
def get_series_list():
    try:
        r = requests.get('https://www.couchtuner.onl/new-releases-2')
    except:
        print('get_series_list(): Connexion error')

    soup = BeautifulSoup(r.text, 'html.parser')
    div = soup.find('div', attrs={'class': 'entry-content'})
    lis = div.find_all('li')

    for li in lis:
        date, title, spec = li.find_all(text=True)
        url = li.a.get('href')

        for title_path in titles_paths:
            if title.upper().startswith(title_path[0].upper()):
                series.append([date, title, url])

    if len(series) < 1:
        print('No new Releases.')


# Get the URLs for not downloaded episodes.
def get_urls():
    for serie in series:
        title = serie[1]
        number = title.strip()[title.find('Season'):]
        for episode in downloaded_list:
            if episode[0].upper() in title.upper():
                ep_downloaded = int(''.join(re.findall(r'\d+', episode[1])))
                ep_available = int(''.join(re.findall(r'\d+', number)))
                if ep_downloaded < ep_available:
                    if input(serie[0] + ' ' + serie[1] + ' Download ? y/n ') == 'y':
                        urls.append(serie[2])

    if len(urls) < 1:
        print('Nothing to download.')


# Launch browser for each episode.
def launch_browser():
    for url in urls:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        link = soup.find('div', attrs={'class': 'postSDiv'}).a.get('href')
        webbrowser.open(link, new=2)


def main():
    get_paths()
    get_downloaded_list()
    get_series_list()
    get_urls()
    launch_browser()
    print('Press Ctrl-Z to exit.')
    while True:
        pass

if __name__ == "__main__":
    main()
