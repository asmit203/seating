import unittest
from src.utils.classroom_allocator import allocate_classrooms
from src.models.course import Course
from src.models.classroom import Classroom

class TestClassroomAllocator(unittest.TestCase):

    def setUp(self):
        self.classrooms = [
            Classroom(room_number="101", capacity=50),
            Classroom(room_number="102", capacity=30),
            Classroom(room_number="103", capacity=40)
        ]
        self.courses = [
            Course(course_code="CS249", capacity=45, enrolled_students=[1, 2, 3, 4, 5]),
            Course(course_code="CH426", capacity=25, enrolled_students=[6, 7, 8, 9, 10]),
            Course(course_code="MM304", capacity=35, enrolled_students=[11, 12, 13, 14, 15])
        ]

    def test_allocate_classrooms_success(self):
        allocation = allocate_classrooms(self.courses, self.classrooms)
        self.assertEqual(len(allocation), 3)
        self.assertEqual(allocation["CS249"], "101")
        self.assertEqual(allocation["CH426"], "102")
        self.assertEqual(allocation["MM304"], "103")

    def test_allocate_classrooms_exceed_capacity(self):
        self.courses.append(Course(course_code="PH422", capacity=60, enrolled_students=[16, 17, 18, 19, 20]))
        allocation = allocate_classrooms(self.courses, self.classrooms)
        self.assertNotIn("PH422", allocation)

    def test_allocate_classrooms_no_available_rooms(self):
        self.classrooms = []
        allocation = allocate_classrooms(self.courses, self.classrooms)
        self.assertEqual(allocation, {})

if __name__ == '__main__':
    unittest.main()