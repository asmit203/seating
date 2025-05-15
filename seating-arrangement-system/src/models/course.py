class Course:
    def __init__(self, code, capacity):
        self.code = code
        self.capacity = capacity
        self.enrolled_students = []

    def enroll_student(self, student_roll):
        if len(self.enrolled_students) < self.capacity:
            self.enrolled_students.append(student_roll)
        else:
            raise ValueError("Cannot enroll student, course capacity reached.")

    def get_enrollment_count(self):
        return len(self.enrolled_students)

    def is_full(self):
        return self.get_enrollment_count() >= self.capacity

    def __str__(self):
        return f"Course(code={self.code}, capacity={self.capacity}, enrolled_students={self.enrolled_students})"