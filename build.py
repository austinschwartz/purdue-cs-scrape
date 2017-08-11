#!/bin/env python3

import requests
import sys
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from collections import OrderedDict
from db import DB

def HEADERS():
    return {'User-Agent': UserAgent().random}

SOUPPARSER = "html5lib"
SECTIONS = {}

class Year:
    def __init__(self, url):
        self.url = url
        self.course_list = self.get_courses(url)

    def get_courses(self, url):
        response = requests.get(url, headers=HEADERS())
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
        return Course.get_sections(self, "..", self.time)

    @staticmethod
    def get_sections(time_url, term = "N/A"):
        response = requests.get(time_url, headers=HEADERS())
        soup = BeautifulSoup(response.text, SOUPPARSER)
        table = soup.find_all('table', class_='datadisplaytable')[0]
        headers = table.find_all('th', class_='ddlabel')
        bodies = soup.select('div.pagebodydiv > table.datadisplaytable > tbody > tr > td.dddefault') # Selectors are the bomb
        sections = []
        for i in range(len(headers)):
            sections.append(Section(headers[i], bodies[i]))
        if len(sections) == 0:
            print(term + ": no sections, oops")
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
        self.term = body.find("span").next_sibling.strip()
        self.type = meeting_times[0].text
        self.time = meeting_times[1].text
        self.days = meeting_times[2].text
        self.where = meeting_times[3].text
        self.date_range = meeting_times[4].text
        self.schedule_type = meeting_times[5].text
        self.instructors = meeting_times[6].text
        if self.crn not in SECTIONS:
            SECTIONS[self.crn] = self

    def __str__(self):
        return "{}\t{} - {} {} {} {}".format(self.term, self.crn, self.number, self.title, self.where, self.time)

class Detailed:
    # https://selfservice.mypurdue.purdue.edu/prod/bwckschd.p_disp_detail_sched?term_in=201810&crn_in=14352
    def __init__(self, url):
        response = requests.get(url, headers=HEADERS())
        soup = BeautifulSoup(response.text, SOUPPARSER)
        error = soup.find('span', class_='errortext')
        if error and error.text=='No detailed class information found':
            return
        print("crn exists")
        table = soup.find_all('table', class_='datadisplaytable')[0]
        header = table('th', class_='ddlabel')
        bodies = soup.select('div.pagebodydiv > table.datadisplaytable > tbody > tr > td.dddefault') # Selectors are the bomb
        sp = header[0].text.split(' - ')
        self.title = sp[0]
        self.crn = sp[1]
        self.number = sp[2]

        tr = bodies[0].find('table', class_='datadisplaytable').find_all('tr')[1].find_all('td')
        print(tr[0].text)

class CRN:
    def __init__(self, term, crn):
        url = "https://selfservice.mypurdue.purdue.edu/prod/bwckschd.p_disp_detail_sched?term_in=" + term + "&crn_in=" + str(crn)
        response = requests.get(url, headers=HEADERS())
        soup = BeautifulSoup(response.text, SOUPPARSER)
        tables = soup.find_all('table', class_='datadisplaytable')
        if len(tables) > 0:
            table = tables[0]
            self.broke = False
        else:
            self.broke = True
            return
        headers = table.find_all('th', class_='ddlabel')
        header = headers[0].text
        sp = header.split(' - ')
        self.title = sp[0]
        self.crn = sp[1]
        self.number = sp[2]
        self.section = sp[3]
        bodies = soup.find_all('td', class_='dddefault')
        self.term = bodies[0].text.split('\n')[1].split(': ')[1].rstrip()
        self.seats_capacity  = bodies[1].text
        self.seats_actual    = bodies[2].text
        self.seats_remaining = bodies[3].text
        self.waitlist_capacity  = bodies[4].text
        self.waitlist_actual    = bodies[5].text
        self.waitlist_remaining = bodies[6].text

    def __str__(self):
        if not self.broke:
            return "{}\t{} - {} {} {} {}".format(self.term, self.crn, self.number, self.title, self.seats_capacity, self.seats_actual)
        else:
            return "no section"
 
    
def convert_term(year, semester):
    if semester == "fall":
        return str(int(year) + 1) + "10"
    else:
        return str(year) + "20"

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("args should be user followed by pass")
        sys.exit(1)
    user = sys.argv[1]
    password = sys.argv[2]
    db = DB(user, password)
    
    #Detailed("https://selfservice.mypurdue.purdue.edu/prod/bwckschd.p_disp_detail_sched?term_in=201810&crn_in=14352")

    for semester in ["spring", "fall"]:
        for year in range(2008, 2019):
            term = convert_term(year, semester)
            crn = CRN(term, "10715")
            print(crn)

    #db.create()

    #url = "https://selfservice.mypurdue.purdue.edu/prod/bzwsrch.p_search_schedule?subject=CS"
    #url = "https://selfservice.mypurdue.purdue.edu/prod/bzwsrch.p_search_schedule?subject=CS&cnbr=15900"
    #courses = Course.get_sections(url)
    #print(courses)

    #for semester in ["spring", "fall"]:
        #for year in range(2008, 2019):
            #term = convert_term(year, semester)
            #Course.get_sections(url + "&term=" + term, term=term)

    #for k in SECTIONS:
        #if SECTIONS[k].where != "TBA":
            #db.insert(SECTIONS[k])

    #db.print_rows()


