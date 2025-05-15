class Classroom:
    def __init__(self, room_number, capacity):
        self.room_number = room_number
        self.capacity = capacity
        self.enrolled_students = []

    def add_student(self, student):
        if self.is_full():
            raise ValueError("Cannot add student, classroom is full.")
        self.enrolled_students.append(student)

    def is_full(self):
        return len(self.enrolled_students) >= self.capacity

    def clear_classroom(self):
        self.enrolled_students = []

    def __str__(self):
        return f"Classroom {self.room_number} with capacity {self.capacity} and {len(self.enrolled_students)} enrolled students."