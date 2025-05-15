class Student:
    def __init__(self, roll_number, name="Unknown Name"):
        self.roll_number = roll_number
        self.name = name

    def __repr__(self):
        return f"Student(roll_number={self.roll_number}, name={self.name})"