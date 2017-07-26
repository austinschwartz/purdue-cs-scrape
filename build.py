#!/bin/env python3

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

HEADERS = {'User-Agent': UserAgent().random}

SOUPPARSER = "html5lib"

class Year:
    def __init__(self, url):
        self.url = url
        self.course_list = self.get_courses(url)

    def get_courses(self, url):
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, SOUPPARSER)
        tables = soup.find_all('table', class_='table-striped')
        return list(map(lambda tr: Course(tr), tables[0].find_all('tr')[1:])) + list(map(lambda tr: Course(tr), tables[1].find_all('tr')[1:])) 

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
        response = requests.get(self.time, headers=HEADERS)
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
        header_split = header.text.split(' - ')
        self.title = header_split[0]
        self.crn = header_split[1]
        self.number = header_split[1]
        # TODO

    def __str__(self):
        return "" # TODO


class DetailedClass:
    # example: https://selfservice.mypurdue.purdue.edu/prod/bwckschd.p_disp_detail_sched?term_in=200910&crn_in=34295
    def __init__(self, url):
        pass # TODO

    def __str__(self):
        return "" #TODO

if __name__ == '__main__':
    year = Year("https://www.cs.purdue.edu/academic-programs/courses/2008_fall_courses.html")
    course = list(filter(lambda course: course.number == "CS 18000", year.course_list))[0]
    sections = course.get_sections()
