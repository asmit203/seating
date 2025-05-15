#!/usr/bin/env python3
# filepath: /Users/asmitganguly/Developer/Github_Try/Mayank Sir/seating-arrangement-system/src/convert_to_excel.py

import pandas as pd
import os
import logging
import numpy as np
from collections import defaultdict
import re

# Setup logging
logging.basicConfig(
    filename="logs/conversion.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def ensure_directories():
    """Ensure all necessary directories exist"""
    os.makedirs("data/input", exist_ok=True)
    os.makedirs("data/output", exist_ok=True)
    os.makedirs("logs", exist_ok=True)


def convert_roll_name_mapping():
    """Convert roll name mapping from CSV to Excel"""
    try:
        logging.info("Converting roll-name mapping file")

        # Read the CSV file
        roll_name_df = pd.read_csv(
            "input_data_tt/in_roll_name_mapping-Table 1.csv",
            skiprows=0,
            encoding="utf-8",
        )

        # Clean column names
        roll_name_df.columns = [col.strip() for col in roll_name_df.columns]

        # Rename columns to match expected format
        roll_name_df = roll_name_df[["Roll", "Name"]].rename(
            columns={"Roll": "Roll Number"}
        )

        # Remove any empty rows
        roll_name_df = roll_name_df.dropna(subset=["Roll Number"])

        # Save to Excel
        roll_name_df.to_excel("data/input/in_roll_name_mapping.xlsx", index=False)
        logging.info(f"Converted roll-name mapping: {len(roll_name_df)} entries")

        return roll_name_df

    except Exception as e:
        logging.error(f"Error in roll-name conversion: {str(e)}")
        raise


def convert_classroom_data():
    """Convert room capacity data from CSV to Excel"""
    try:
        logging.info("Converting classroom data")

        # Read the CSV file
        rooms_df = pd.read_csv("input_data_tt/in_room_capacity-Table 1.csv", skiprows=0)

        # Clean column names
        rooms_df.columns = [col.strip() for col in rooms_df.columns]

        # Create new dataframe with required columns
        classrooms_df = pd.DataFrame(
            {"room_id": rooms_df["Room No."], "capacity": rooms_df["Exam Capacity"]}
        )

        # Remove any empty rows
        classrooms_df = classrooms_df.dropna(subset=["room_id"])

        # Save to Excel
        classrooms_df.to_excel("data/input/in_classrooms.xlsx", index=False)
        logging.info(f"Converted classroom data: {len(classrooms_df)} entries")

        return classrooms_df

    except Exception as e:
        logging.error(f"Error in classroom data conversion: {str(e)}")
        raise


def parse_timetable():
    """Parse timetable data to get exam schedule"""
    try:
        logging.info("Parsing timetable")

        # Read the CSV file - using custom delimiter because the file uses semicolons
        timetable_df = pd.read_csv(
            "input_data_tt/in_timetable-Table 1.csv", skiprows=0, delimiter=","
        )

        # Parse exam schedule
        exam_schedule = []

        for _, row in timetable_df.iterrows():
            date = row["Date"]
            day = row["Day"]

            # Skip if no date
            if pd.isna(date):
                continue

            # Process morning slot
            morning_courses = str(row["Morning"]).strip()
            if morning_courses != "nan" and morning_courses != "NO EXAM":
                # Split courses by semicolon and clean
                morning_list = re.split(r"[;,]", morning_courses)
                for course in morning_list:
                    course = course.strip()
                    if course:  # Skip empty strings
                        exam_schedule.append(
                            {
                                "date": date,
                                "day": day,
                                "slot": "Morning",
                                "course_id": course,
                            }
                        )

            # Process evening slot
            evening_courses = str(row["Evening"]).strip()
            if evening_courses != "nan" and evening_courses != "NO EXAM":
                # Split courses by semicolon and clean
                evening_list = re.split(r"[;,]", evening_courses)
                for course in evening_list:
                    course = course.strip()
                    if course:  # Skip empty strings
                        exam_schedule.append(
                            {
                                "date": date,
                                "day": day,
                                "slot": "Evening",
                                "course_id": course,
                            }
                        )

        return pd.DataFrame(exam_schedule)

    except Exception as e:
        logging.error(f"Error parsing timetable: {str(e)}")
        raise


def get_rolls_for_courses():
    """Get roll numbers for each course"""
    try:
        logging.info("Getting roll numbers for courses")

        # Read the CSV file
        course_roll_df = pd.read_csv(
            "input_data_tt/in_course_roll_mapping-Table 1.csv", skiprows=0
        )

        # Clean column names
        course_roll_df.columns = [col.strip() for col in course_roll_df.columns]

        # Group rolls by course
        course_rolls = defaultdict(list)

        for _, row in course_roll_df.iterrows():
            roll = str(row["rollno"]).strip()
            course = str(row["course_code"]).strip()

            if roll and course and pd.notna(roll) and pd.notna(course):
                course_rolls[course].append(roll)

        # Convert to dictionary with roll numbers as semicolon-separated string
        course_rolls_dict = {
            course: ";".join(rolls) for course, rolls in course_rolls.items()
        }

        return course_rolls_dict

    except Exception as e:
        logging.error(f"Error getting rolls for courses: {str(e)}")
        raise


def create_courses_excel():
    """Create the courses Excel file with enrollment data"""
    try:
        logging.info("Creating courses Excel file")

        # Get timetable data
        timetable_df = parse_timetable()

        # Get rolls for each course
        course_rolls_dict = get_rolls_for_courses()

        # Add enrollment information
        courses_data = []

        for _, exam in timetable_df.iterrows():
            course_id = exam["course_id"]

            # Get roll numbers for this course
            roll_numbers = course_rolls_dict.get(course_id, "")

            # Calculate enrollment count
            if roll_numbers:
                enrollment = len(roll_numbers.split(";"))
            else:
                enrollment = 0

            courses_data.append(
                {
                    "course_id": course_id,
                    "date": exam["date"],
                    "day": exam["day"],
                    "slot": exam["slot"],
                    "roll_numbers": roll_numbers,
                    "enrollment": enrollment,
                }
            )

        # Create DataFrame
        courses_df = pd.DataFrame(courses_data)

        # Save to Excel
        courses_df.to_excel("data/input/in_courses.xlsx", index=False)
        logging.info(f"Created courses Excel with {len(courses_df)} entries")

        return courses_df

    except Exception as e:
        logging.error(f"Error creating courses Excel: {str(e)}")
        raise


def main():
    """Main function to convert all files"""
    try:
        print("Starting conversion of CSV files to Excel...")
        ensure_directories()

        # Convert files
        roll_name_df = convert_roll_name_mapping()
        classrooms_df = convert_classroom_data()
        courses_df = create_courses_excel()

        print(f"Conversion complete:")
        print(f"  - Roll-name mapping: {len(roll_name_df)} entries")
        print(f"  - Classrooms: {len(classrooms_df)} entries")
        print(f"  - Courses: {len(courses_df)} entries")
        print("Excel files have been saved to the data/input directory.")

    except Exception as e:
        logging.error(f"Error in conversion process: {str(e)}")
        print(f"Error in conversion process: {str(e)}")


if __name__ == "__main__":
    main()
