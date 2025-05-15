import unittest
from src.utils.conflict_checker import check_conflicts

class TestConflictChecker(unittest.TestCase):

    def setUp(self):
        self.course1 = {
            'code': 'CS249',
            'students': {1, 2, 3, 4, 5}
        }
        self.course2 = {
            'code': 'CH426',
            'students': {6, 7, 8, 9, 10}
        }
        self.course3 = {
            'code': 'MM304',
            'students': {3, 4, 11, 12, 13}
        }

    def test_no_conflict(self):
        courses = [self.course1, self.course2]
        result = check_conflicts(courses)
        self.assertEqual(result, [])

    def test_with_conflict(self):
        courses = [self.course1, self.course3]
        result = check_conflicts(courses)
        self.assertEqual(result, [('CS249', 3), ('CS249', 4)])

    def test_multiple_conflicts(self):
        course4 = {
            'code': 'CB308',
            'students': {4, 5, 14, 15}
        }
        courses = [self.course1, self.course3, course4]
        result = check_conflicts(courses)
        self.assertEqual(result, [('CS249', 4), ('MM304', 4), ('MM304', 5)])

if __name__ == '__main__':
    unittest.main()