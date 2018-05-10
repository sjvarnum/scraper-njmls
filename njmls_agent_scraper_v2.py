""" This version gets the list of municipalities from NJMLS web site """


from bs4 import BeautifulSoup
import requests
import pandas as pd
import re


agent = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299'
)

muni_url = ("""http://www.njmls.com/listings/index.cfm?action=
            xhr.multiple_town_select_new#tab1""")

r = requests.get(muni_url, headers={'User-Agent': agent})
c = r.content
soup = BeautifulSoup(c, 'html.parser')


municipalities = []
for i in soup.find_all('input', {'class': 'multitown_checks'}):
    value = i.get('value')
    municipalities.append(value)

county_list = []
for i in municipalities:
    my_dict = {}
    my_dict['City'] = i.split(', ')[0]
    my_dict['County'] = i.split(', ')[2]
    county_list.append(my_dict)


base_url = 'http://www.njmls.com/members/index.cfm?action=dsp.results'

agent_list = []
for item in county_list:
    city = item['City']
    county = item['County']
    params = {'city': city, 'county': county}
    r = requests.get(base_url, params=params, headers={'User-Agent': agent})
    c = r.content
    soup = BeautifulSoup(c, 'html.parser')
    agents = soup.find_all('div', {'class': 'realtor-info'})

    for i in agents[:-1]:
        my_dict = {}
        try:
            my_dict['City'] = city
        except (AttributeError, IndexError):
            None
        try:
            my_dict['County'] = county
        except (AttributeError, IndexError):
            None
        try:
            my_dict['Name'] = i.find('strong').text
        except (AttributeError, IndexError):
            None
        try:
            my_dict['Title'] = i.find('div').contents[0].replace(
                '\n', '').replace('\t', '')
        except (AttributeError, IndexError):
            None
        try:
            my_dict['Agency'] = i.find_all('strong')[1].text
        except (AttributeError, IndexError):
            None
        try:
            my_dict['Office Number'] = (i.find(
                string=re.compile('Office Phone:'))
                .replace('\n', '').replace('\t', '')
                .split(' ')[2].replace('(', '')
                .replace(')', '-') + i.find(
                string=re.compile('Office Phone:'))
                .replace('\n', '').replace('\t', '').split(' ')[-1])
        except (AttributeError, IndexError):
            None

        try:
            my_dict['Contact Number'] = (i.find(
                string=re.compile('Contact Phone:'))
                .replace('\n', '').replace('\t', '')
                .split()[2].replace('(', '')
                .replace(')', '-') + i.find(
                string=re.compile('Contact Phone:'))
                .replace('\n', '').replace('\t', '').split()[-1])
        except (AttributeError, IndexError):
            None

        try:
            my_dict['Email'] = (i.find('a', {'class': 'tips'})
                                .get('href').split(':')[1].split('?')[0])
        except (AttributeError, IndexError):
            None
        agent_list.append(my_dict)

df = pd.DataFrame(agent_list)
agent_df = (df[['Name', 'Title', 'Agency', 'Office Number',
                'Contact Number', 'Email']]
            .drop_duplicates()
            .sort_values('Name'))
agent_df.to_csv('njmls_agents_20180509.csv', index=False)
