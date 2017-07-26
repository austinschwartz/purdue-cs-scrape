import unittest
from build import Year, Course, Section

class ParseTests(unittest.TestCase):
    def setUp(self):
        self.year = Year("https://www.cs.purdue.edu/academic-programs/courses/2008_fall_courses.html")
        course = list(filter(lambda course: course.number == "CS 18000", self.year.course_list))[0]
        self.assertEqual(course.title, "Problem Solving And Object-Oriented Programming")
        self.sections = course.get_sections()

    def test_course(self):
        course = self.year.course_list[0]
        self.assertEqual(course.number, "CS 11000")
        self.assertEqual(course.title, "Introduction To Computers")

    def test_sections(self):
        self.assertEqual(self.sections[0].crn, "34295")
        self.assertEqual(self.sections[1].crn, "34299")

if __name__ == '__main__':
    unittest.main()
