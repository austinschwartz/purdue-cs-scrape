#!/bin/env python3

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from collections import OrderedDict

HEADERS = {'User-Agent': UserAgent().random}

SOUPPARSER = "html5lib"
SECTIONS = {}

class Year:
    def __init__(self, url):
        self.url = url
        self.course_list = self.get_courses(url)

    def get_courses(self, url):
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, SOUPPARSER)
        tables = soup.find_all('table', class_='table-striped')
        return list(map(lambda tr: Course(tr), tables[0].find_all('tr')[1:])) + \
                list(map(lambda tr: Course(tr), tables[1].find_all('tr')[1:])) 

    def __str__(self):
        return "\n".join(map(str, self.course_list))

class Course:
    def __init__(self, tr):
        td = tr.find_all('td')
        self.number = td[0].text
        self.url = td[0].a['href'] # TODO follow link and store description
        self.title = td[1].text
        self.instructors = self.parse_instructors(td[2].find('instructors'))
        self.time = td[3].a['href']

    def get_sections(self):
        return Course.get_sections(self, self.time)

    @staticmethod
    def get_sections(time_url):
        response = requests.get(time_url, headers=HEADERS)
        soup = BeautifulSoup(response.text, SOUPPARSER)
        table = soup.find_all('table', class_='datadisplaytable')[0]
        headers = table.find_all('th', class_='ddlabel')
        bodies = soup.select('div.pagebodydiv > table.datadisplaytable > tbody > tr > td.dddefault') # Selectors are the bomb
        sections = []
        for i in range(len(headers)):
            sections.append(Section(headers[i], bodies[i]))
        return sections

    @staticmethod
    def parse_instructors(instructors):
        # TODO actually parse list later if needed
        return instructors

    def __str__(self):
        return "{}\t{}".format(self.number, self.title)

class Section:
    def __init__(self, header, body):
        global sections
        header_split = header.text.split(' - ')
        self.title = header_split[0]
        self.crn = header_split[1]
        self.number = header_split[2]
        self.link = "https://selfservice.mypurdue.purdue.edu/" + header.find('a')['href']
        meeting_times = body.find_all('td')
        # TODO term?
        self.type = meeting_times[0].text
        self.time = meeting_times[1].text
        self.days = meeting_times[2].text
        self.where = meeting_times[3].text
        self.date_range = meeting_times[4].text
        self.lecture_type = meeting_times[5].text
        self.instructors = meeting_times[6].text
        if self.crn not in SECTIONS:
            SECTIONS[self.crn] = self

    def __str__(self):
        return "{} {} {} {} {}".format(self.crn, self.number, self.title, self.where, self.time) # TODO add term


class DetailedClass:
    # example: https://selfservice.mypurdue.purdue.edu/prod/bwckschd.p_disp_detail_sched?term_in=200910&crn_in=34295
    def __init__(self, url):
        pass # TODO

    def __str__(self):
        return "" #TODO

if __name__ == '__main__':
    url = "https://selfservice.mypurdue.purdue.edu/prod/bzwsrch.p_search_schedule?subject=CS"
    Course.get_sections(url)

    for k in SECTIONS:
        if SECTIONS[k].where != "TBA":
            print(SECTIONS[k])
