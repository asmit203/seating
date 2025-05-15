import pandas as pd
import logging
import os
from collections import defaultdict


def allocate_classrooms(courses_df, classrooms_df, buffer, density):
    """
    Allocate classrooms to courses based on enrollment and room capacity.

    Parameters:
    - courses_df: DataFrame containing course information
    - classrooms_df: DataFrame containing classroom information
    - buffer: Integer representing buffer space in each classroom
    - density: String 'sparse' or 'dense' to determine seating density

    Returns:
    - DataFrame with seating arrangement information
    """
    try:
        # Create a copy of the DataFrames to avoid modifying the originals
        courses = courses_df.copy().sort_values(by="enrollment", ascending=False)
        classrooms = classrooms_df.copy().sort_values(by="capacity", ascending=False)

        # Dictionary to store allocation results
        allocations = []

        # Dictionary to track remaining capacity in each classroom
        remaining_capacity = dict(zip(classrooms["room_id"], classrooms["capacity"]))

        # Track already assigned buildings for each course to minimize movement
        course_buildings = {}

        # Track all allocated students to check for conflicts
        allocated_students = set()

        for _, course in courses.iterrows():
            course_id = course["course_id"]
            enrollment = course["enrollment"]
            date = course["date"]
            slot = course["slot"]

            # Handle roll_numbers which could be NaN or string
            roll_numbers_str = course.get("roll_numbers", "")
            if pd.isna(roll_numbers_str):
                students = set()
            else:
                students = set(
                    roll_numbers_str.split(";")
                    if isinstance(roll_numbers_str, str)
                    else []
                )

            # Check for conflicts (students already allocated to the same slot)
            conflicts = students.intersection(allocated_students)
            if conflicts:
                logging.error(f"Conflict detected for course {course_id}: {conflicts}")
                print(f"Conflict detected for course {course_id}: {conflicts}")
                continue

            # Calculate effective capacity based on buffer and density
            effective_capacity = {}
            for room_id, capacity in remaining_capacity.items():
                effective_cap = capacity - buffer
                if density == "sparse":
                    effective_cap = effective_cap // 2
                effective_capacity[room_id] = effective_cap

            # Try to allocate to rooms in the same building if previously assigned
            allocated = False
            current_building = course_buildings.get(course_id)

            if current_building:
                # First try rooms in the same building
                same_building_rooms = [
                    r
                    for r in effective_capacity.keys()
                    if r.startswith(current_building)
                    and effective_capacity[r] >= enrollment
                ]

                if same_building_rooms:
                    room_id = same_building_rooms[0]  # Take the first suitable room
                    allocations.append(
                        {
                            "date": date,
                            "slot": slot,
                            "course_id": course_id,
                            "room_id": room_id,
                            "capacity": remaining_capacity[room_id],
                            "enrollment": enrollment,
                            "roll_numbers": course["roll_numbers"],
                        }
                    )
                    remaining_capacity[room_id] -= enrollment
                    allocated_students.update(students)
                    allocated = True

            # If not already allocated, try any available room
            if not allocated:
                for room_id, capacity in effective_capacity.items():
                    if capacity >= enrollment:
                        # Extract building ID (assuming format like "B101" where "B" is the building)
                        building = (
                            room_id.split("-")[0] if "-" in room_id else room_id[0]
                        )
                        course_buildings[course_id] = building

                        allocations.append(
                            {
                                "date": date,
                                "slot": slot,
                                "course_id": course_id,
                                "room_id": room_id,
                                "capacity": remaining_capacity[room_id],
                                "enrollment": enrollment,
                                "roll_numbers": course["roll_numbers"],
                            }
                        )
                        remaining_capacity[room_id] -= enrollment
                        allocated_students.update(students)
                        allocated = True
                        break

            if not allocated:
                error_msg = f"Cannot allocate classroom for course {course_id} with enrollment {enrollment}"
                logging.error(error_msg)
                print(error_msg)

        # Create DataFrame from allocations
        allocation_df = pd.DataFrame(allocations)

        # Create folder structure for individual course seating plans
        create_individual_seating_plans(allocation_df)

        # Calculate and save seats left information
        seats_left_df = calculate_seats_left(remaining_capacity)
        seats_left_df.to_excel("data/output/op_seats_left.xlsx", index=False)

        return allocation_df

    except Exception as e:
        logging.error(f"Error in classroom allocation: {str(e)}")
        raise


def calculate_seats_left(remaining_capacity):
    """Calculate seats left in each classroom after allocation."""
    seats_left = [
        {"room_id": room, "seats_left": capacity}
        for room, capacity in remaining_capacity.items()
    ]
    return pd.DataFrame(seats_left)


def create_individual_seating_plans(allocation_df):
    """Create individual seating plan Excel files for each course-classroom combination."""
    try:
        for _, row in allocation_df.iterrows():
            date = row["date"].replace("/", "_")
            course_id = row["course_id"]
            room_id = row["room_id"]
            slot = row["slot"].lower()

            # Create directory structure
            output_dir = f"data/output/{date}/{slot.capitalize()}"
            os.makedirs(output_dir, exist_ok=True)

            # Create individual seating plan file
            output_file = f"{output_dir}/{date}_{course_id}_{room_id}.xlsx"

            # Create seating plan DataFrame
            seating_data = {
                "course_id": [course_id],
                "room_id": [room_id],
                "date": [row["date"]],
                "slot": [row["slot"]],
                "roll_numbers": [row["roll_numbers"]],
            }

            seating_df = pd.DataFrame(seating_data)
            seating_df.to_excel(output_file, index=False)

    except Exception as e:
        logging.error(f"Error creating individual seating plans: {str(e)}")
        raise
