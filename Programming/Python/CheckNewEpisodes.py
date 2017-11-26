import requests
import webbrowser  
from bs4 import BeautifulSoup  

r = requests.get('https://www.couchtuner.onl/new-releases-2')

soup = BeautifulSoup(r.text, 'html.parser')  
div = soup.find('div', attrs={'class':'entry-content'})
lis = div.find_all('li')
series = []  

for li in lis:  
    date, title, spec = li.find_all(text=True)
    url = li.a.get('href')
    if title.startswith('Young Sheldon')\
    or title.startswith('Brooklyn Nine')\
    or title.startswith('Mr. Robot')\
    or title.startswith('Scandal')\
    or title.startswith('The Walking Dead')\
    or title.startswith('Man with a Plan')\
    or title.startswith('Brooklyn Nine'):
        series.append(((date+title), url))

urls = []
for serie in series:
    if input(serie[0] + ' Download ? y/n ') == 'y':
        urls.append(serie[1])

for url in urls:
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')  
    link = soup.find('div', attrs={'class':'postSDiv'}).a.get('href')
    webbrowser.open(link, new=2)
        
