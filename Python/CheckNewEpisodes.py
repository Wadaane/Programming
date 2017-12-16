import os
import re
import webbrowser

import requests
from bs4 import BeautifulSoup

paths = [
    'E:\Series\Comedie',
    'E:\Series\Autre'
]
web_url = 'https://www.couchtuner.onl/new-releases-2'
downloaded_list = []
series = []
urls = []
titles_paths = []
print('\t\tCheck For New Episodes')


# Get paths of all series in the provided main folders.
def get_paths():
    for path in paths:
        names = os.listdir(path)
        for name in names:
            file_name, file_ext = os.path.splitext(name)
            if file_ext == '' or file_ext.startswith('. '):
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
            file_name = file_name[:index - 1].strip()  # .replace('.', ' ').strip()
            number = 'Season ' + str(int(season)) + ' Episode ' + str(int(episode))
            downloaded_list.append([file_name, number])
        except:
            print('get_downloaded_list(): File Error: ' + file)


# Get list of new releases.
def get_series_list():
    try:
        r = requests.get(web_url)
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
    # print(*series, sep='\n')
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
                    if input('\t\t' + serie[0] + ' ' + serie[1] + ' Download ? y/n ') == 'y':
                        urls.append(serie[2])

    if len(urls) < 1:
        print('\tNothing to download.')
    else:
        print('\tOpen each episode page to manually start download ...')


def get_video_url(page_url):
    r = requests.get(page_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    div = soup.find('div', attrs={'class': 'postTabs_divs postTabs_curr_div'})
    iframe = div.find('iframe')
    video_url = iframe.get('src')
    return video_url


# Launch browser for each episode.
def launch_browser():
    for url in urls:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        link = soup.find('div', attrs={'class': 'postSDiv'}).a.get('href')
        link = get_video_url(link)
        webbrowser.open(link, new=2)


def main():
    print('\tGet latest downloaded episodes in local folders ...')
    get_paths()
    get_downloaded_list()
    print('\tGet new releases list from website ...')
    get_series_list()
    print('\tCheck if there is new episodes to download ...')
    get_urls()
    launch_browser()
    input('\tPress Enter to exit.')


if __name__ == "__main__":
    main()
