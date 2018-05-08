from bs4 import BeautifulSoup
import requests
import pandas as pd
import re


def get_municipality():

    r = requests.get(
        'https://en.wikipedia.org/wiki/List_of_municipalities_in_New_Jersey'
    )

    c = r.content
    soup = BeautifulSoup(c, 'html.parser')

    municipalities = []
    table = soup.find('table', attrs={'class': 'wikitable sortable'})
    rows = table.find_all('tr')
    for row in rows[1:]:
        cols = row.find_all('td')
        cols = [element.text.strip() for element in cols]
        my_dict = {}
        my_dict['City'] = cols[1]
        my_dict['County'] = cols[2]
        municipalities.append(my_dict)
    return municipalities


def get_url_list():
    base_url = (
        'http://www.njmls.com/members/index.cfm?action=dsp.results&city='
    )
    url_list = []
    for item in get_municipality():
        city = item['City']
        county = item['County']
        url = f'{base_url}{city}'.replace(' ', '+')
        url = f'{url}&county={county}'
        url_list.append(url)
    return url_list


def get_agent_list():
    agent_list = []
    for url in get_url_list():
        r = requests.get(url)
        c = r.content
        soup = BeautifulSoup(c, 'html.parser')
        agents = soup.find_all('div', {'class': 'realtor-info'})

        for i in agents[:-1]:
            my_dict = {}
            try:
                my_dict['Name'] = i.find('strong').text
            except AttributeError:
                None
            try:
                my_dict['Title'] = i.find('div').contents[0].replace(
                    '\n', '').replace('\t', '')
            except AttributeError:
                None
            try:
                my_dict['Agency'] = i.find_all('strong')[1].text
            except AttributeError:
                None
            try:
                my_dict['Office Number'] = (i.find(
                    string=re.compile('Office Phone:'))
                    .replace('\n', '').replace('\t', '')
                    .split(' ')[2].replace('(', '')
                    .replace(')', '-') + i.find(
                    string=re.compile('Office Phone:'))
                    .replace('\n', '').replace('\t', '').split(' ')[-1])
            except AttributeError:
                None

            try:
                my_dict['Contact Number'] = (i.find(
                    string=re.compile('Contact Phone:'))
                    .replace('\n', '').replace('\t', '')
                    .split()[2].replace('(', '')
                    .replace(')', '-') + i.find(
                    string=re.compile('Contact Phone:'))
                    .replace('\n', '').replace('\t', '').split()[-1])
            except AttributeError:
                None

            try:
                my_dict['Email'] = (i.find('a', {'class': 'tips'})
                                    .get('href').split(':')[1].split('?')[0])
            except AttributeError:
                None
            agent_list.append(my_dict)
        return agent_list


df = pd.DataFrame(get_agent_list())
agent_df = df[['Name', 'Title', 'Agency', 'Office Number',
               'Contact Number', 'Email']].drop_duplicates()
agent_df.to_csv('njmls_agents_20180221.csv', index=False)
# municipalities_dict = get_municipality()
# print(municipalities_dict[:2])
# print(get_municipality()[:2])
# print(get_url_list()[:2])
# print(get_agent_list()[0])
