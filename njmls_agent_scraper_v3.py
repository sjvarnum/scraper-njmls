from bs4 import BeautifulSoup
import requests
# import pandas as pd
# import re


class Scraper(object):

    agent = (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299'
    )

    def get_municipalties(self):

        muni_url = ('http://www.njmls.com/listings/index.cfm')
        action = 'xhr.multiple_town_select_new'
        payload = {'action': action}

        self.r = requests.get(muni_url, params=payload,
                              headers={'User-Agent': Scraper.agent})
        self.c = self.r.content
        self.soup = BeautifulSoup(self.c, 'html.parser')

        municipalities = []
        for i in self.soup.find_all('input', {'class': 'multitown_checks'}):
            value = i.get('value')
            municipalities.append(value)
        print('this would be a list of munis')
        return municipalities

    def get_counties():
        pass


if __name__ == '__main__':
    muni = Scraper()
    muni.get_municipalties()
