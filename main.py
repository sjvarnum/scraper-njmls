from bs4 import BeautifulSoup
import requests
import pandas as pd
import re


class Scraper(object):

    agent = (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299'
    )

    def get_municipalties(self):

        muni_url = ('http://www.njmls.com/listings/index.cfm')
        action = 'xhr.multiple_town_select_new'
        url_params = {'action': action}

        self.r = requests.get(muni_url, params=url_params,
                              headers={'User-Agent': Scraper.agent})
        self.c = self.r.content
        self.soup = BeautifulSoup(self.c, 'html.parser')

        municipalities = []
        for i in self.soup.find_all('input', {'class': 'multitown_checks'}):
            value = i.get('value')
            my_dict = {}
            my_dict['City'] = value.split(', ')[0]
            my_dict['County'] = value.split(', ')[2]
            municipalities.append(my_dict)
        return municipalities


if __name__ == '__main__':
    scraper = Scraper()
    municipalties = scraper.get_municipalties()

    base_url = 'http://www.njmls.com/members/index.cfm?action=dsp.results'

    agent_list = []
    for item in municipalties:
        city = item['City']
        county = item['County']
        params = {'city': city, 'county': county}
        r = requests.get(base_url, params=params, headers={
                         'User-Agent': Scraper.agent})
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
    agent_df.to_csv('njmls_agents.csv', index=False)
