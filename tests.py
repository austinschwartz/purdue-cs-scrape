import unittest
from build import Year, Course, Section

class ParseTests(unittest.TestCase):
    def setUp(self):
        self.year = Year("https://www.cs.purdue.edu/academic-programs/courses/2008_fall_courses.html")
        self.course1 = self.year.course_list[0]

    def test_course(self):
        self.assertEqual(self.course1.number, "CS 11000")
        self.assertEqual(self.course1.title, "Introduction To Computers")

if __name__ == '__main__':
    unittest.main()
