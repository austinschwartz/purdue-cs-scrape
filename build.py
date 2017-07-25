#!/bin/env python3

import requests
from bs4 import BeautifulSoup

class Year:
    def __init__(self, url):
        self.url = url
        self.course_list = self.get_courses(url)

    def get_courses(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html5lib")
        tables = soup.find_all('table', class_='table-striped')
        return list(map(lambda tr: Course(tr), tables[0].find_all('tr')[1:])) + list(map(lambda tr: Course(tr), tables[1].find_all('tr')[1:])) 

    def __str__(self):
        return "\n".join(map(str, self.course_list))

class Course:
    def __init__(self, tr):
        td = tr.find_all('td')
        self.number = td[0].text
        self.url = td[0].a['href']
        self.title = td[1].text
        self.instructors = self.parse_instructors(td[2].find('instructors'))
        self.time = td[3].a['href']

    @staticmethod
    def parse_instructors(instructors):
        return instructors

    def __str__(self):
        return "{}\t{}".format(self.number, self.title)

class Section:
    def __init__(self):
        pass # TODO

    def __str__(self):
        return "" # TODO

test1 = "https://www.cs.purdue.edu/academic-programs/courses/2008_fall_courses.html"
time_test1 = "https://selfservice.mypurdue.purdue.edu/prod/bzwsrch.p_search_schedule?term=200910&subject=CS&cnbr=25100&schd_type=LEC"

y = Year(test1)

print(y)


