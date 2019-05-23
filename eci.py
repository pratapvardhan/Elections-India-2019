import os
import requests
from bs4 import BeautifulSoup
import pandas as pd


folder = os.path.dirname(os.path.abspath(__file__))


def eci(soup, st_code, const_code):
    data = soup.find_all('table')[8].find_all('table')[1]
    state, constituency = data.find('th').text.strip().split('-', 1)
    result = []
    for tr in data.find_all('tr')[3:-1]:
        cells = [td.text.strip() for td in tr.find_all('td')]
        if len(cells) == 8:
            cells.pop(4)
        cells += [state, constituency, st_code, const_code]
        result.append(cells)
    return result


codes = pd.read_csv(os.path.join(folder, 'codes.csv'))
ua = (
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/34.0.1847.116 Safari/537.36')
session = requests.Session()
result = []
for _, code in codes.iterrows():
    st_code = code['ST_CODE']
    for const in range(1, code['PC_CODE'] + 1):
        url = (
            'https://results.eci.gov.in/pc/en/constituencywise'
            '/Constituencywise{}{}.htm?ac={}'.format(st_code, const, const))
        response = session.get(url, headers={'User-Agent': ua})
        print(st_code, const, response.status_code, url)
        if response.status_code == 404:
            continue
        soup = BeautifulSoup(response.text, 'html.parser')
        result += eci(soup, st_code, const)

cols = [
    'OSN', 'Candidate', 'Party', 'EVM Votes', 'Postal Votes', 'Total Votes',
    '%', 'State', 'Constituency', 'ST_CODE', 'PC_CODE']
df = pd.DataFrame(result, columns=cols)
df.to_csv(os.path.join(folder, 'eci-2019.csv'), index=False, encoding='utf-8')
