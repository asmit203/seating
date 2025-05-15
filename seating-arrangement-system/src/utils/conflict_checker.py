import logging
import os
import pandas as pd
from collections import defaultdict


def check_conflicts(courses_df):
    """
    Check for scheduling conflicts among courses based on student roll numbers.

    Args:
        courses_df (DataFrame): A DataFrame containing course information with columns
                              'course_id', 'date', 'slot', and 'roll_numbers'.

    Returns:
        list: A list of conflict dictionaries containing details about each conflict.
    """
    conflicts = []

    try:
        # Group courses by date and slot
        grouped = courses_df.groupby(["date", "slot"])

        # Keep track of conflicts by student for reporting purposes
        conflict_count_by_student = defaultdict(int)

        for (date, slot), group in grouped:
            # Map to track which course each roll number is assigned to
            roll_number_map = {}

            for _, course in group.iterrows():
                course_id = course["course_id"]

                # Skip if roll_numbers is missing or not a string
                if pd.isna(course["roll_numbers"]) or not isinstance(
                    course["roll_numbers"], str
                ):
                    continue

                # Split the roll numbers by semicolon and check each one
                roll_numbers = course["roll_numbers"].strip().split(";")

                for roll_number in roll_numbers:
                    roll_number = roll_number.strip()
                    if not roll_number:  # Skip empty roll numbers
                        continue

                    if roll_number in roll_number_map:
                        # Conflict found - same student assigned to two courses in the same slot
                        conflict = {
                            "date": date,
                            "slot": slot,
                            "roll_number": roll_number,
                            "course1": course_id,
                            "course2": roll_number_map[roll_number],
                        }
                        conflicts.append(conflict)

                        # Update conflict count for this student
                        conflict_count_by_student[roll_number] += 1
                    else:
                        roll_number_map[roll_number] = course_id

        # Save conflict data to file
        if conflicts:
            save_conflict_data(conflicts, conflict_count_by_student)

        return conflicts

    except Exception as e:
        logging.error(f"Error checking conflicts: {str(e)}")
        return []


def save_conflict_data(conflicts, conflict_count_by_student):
    """
    Save conflict data to Excel files for further analysis.

    Args:
        conflicts (list): List of conflict dictionaries
        conflict_count_by_student (dict): Dictionary mapping roll numbers to conflict counts
    """
    try:
        # Create the output directory if it doesn't exist
        os.makedirs("data/output/conflicts", exist_ok=True)

        # Convert conflicts to DataFrame and save
        conflict_df = pd.DataFrame(conflicts)
        conflict_df.to_excel(
            "data/output/conflicts/conflicts_detailed.xlsx", index=False
        )

        # Create a summary by student
        student_conflicts = [
            {"roll_number": roll, "conflict_count": count}
            for roll, count in conflict_count_by_student.items()
        ]
        student_df = pd.DataFrame(student_conflicts).sort_values(
            by="conflict_count", ascending=False
        )
        student_df.to_excel(
            "data/output/conflicts/conflicts_by_student.xlsx", index=False
        )

        # Create a summary by date and slot
        slot_summary = (
            conflict_df.groupby(["date", "slot"])
            .size()
            .reset_index(name="conflict_count")
        )
        slot_summary.to_excel(
            "data/output/conflicts/conflicts_by_slot.xlsx", index=False
        )

        # Create a summary by course
        course_conflicts = defaultdict(int)
        for conflict in conflicts:
            course_conflicts[conflict["course1"]] += 1
            course_conflicts[conflict["course2"]] += 1

        course_df = pd.DataFrame(
            [
                {"course_id": course, "conflict_count": count}
                for course, count in course_conflicts.items()
            ]
        ).sort_values(by="conflict_count", ascending=False)

        course_df.to_excel(
            "data/output/conflicts/conflicts_by_course.xlsx", index=False
        )

    except Exception as e:
        logging.error(f"Error saving conflict data: {str(e)}")


def display_conflicts(conflicts):
    """
    Display the conflicts found in a readable format and provide recommendations.

    Args:
        conflicts (list): A list of conflict dictionaries containing
                        'date', 'slot', 'roll_number', 'course1', and 'course2'.
    """
    if not conflicts:
        print("\n✅ No conflicts found! All student assignments are valid.")
        return

    # Organize conflicts by date and slot for better display
    conflicts_by_slot = defaultdict(list)
    for conflict in conflicts:
        key = (conflict["date"], conflict["slot"])
        conflicts_by_slot[key].append(conflict)

    # Count conflicts by student
    student_conflicts = defaultdict(int)
    for conflict in conflicts:
        student_conflicts[conflict["roll_number"]] += 1

    # Get the top 5 students with the most conflicts
    top_students = sorted(student_conflicts.items(), key=lambda x: x[1], reverse=True)[
        :5
    ]

    print("\n⚠️ CONFLICTS DETECTED ⚠️")
    print(
        f"Found {len(conflicts)} conflicts affecting {len(student_conflicts)} students."
    )
    print("Detailed conflict reports saved to data/output/conflicts/ directory.")

    print("\nTop 5 students with most conflicts:")
    for roll, count in top_students:
        print(f"  • Student {roll}: {count} conflicts")

    print("\nConflicts by date and slot:")
    for (date, slot), slot_conflicts in conflicts_by_slot.items():
        print(f"  • Date: {date}, Slot: {slot} - {len(slot_conflicts)} conflicts")

    print("\nRecommendations:")
    print("  1. Review the detailed conflict reports in the output directory")
    print("  2. Consider rescheduling courses with the highest conflict rates")
    print("  3. Notify affected students about potential schedule conflicts")
    print(
        "\nTo view all conflicts in detail, check the generated Excel files in 'data/output/conflicts/'."
    )
