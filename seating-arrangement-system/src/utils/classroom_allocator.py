# filepath: /Users/asmitganguly/Developer/Github_Try/Mayank Sir/seating-arrangement-system/src/utils/classroom_allocator.py
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

        # Group courses by date and slot for conflict checking
        courses_by_slot = courses.groupby(["date", "slot"])

        # Process each date and slot
        for (date, slot), group in courses_by_slot:
            # Reset allocated students for this slot
            slot_allocated_students = set()

            for _, course in group.sort_values(
                by="enrollment", ascending=False
            ).iterrows():
                course_id = course["course_id"]
                enrollment = course["enrollment"]

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
                conflicts = students.intersection(slot_allocated_students)
                if conflicts:
                    logging.error(
                        f"Conflict detected for course {course_id}: {conflicts}"
                    )
                    print(f"Conflict detected for course {course_id}: {conflicts}")
                    continue

                # Calculate effective capacity based on buffer and density
                effective_capacity = {}
                for room_id, capacity in remaining_capacity.items():
                    effective_cap = capacity - buffer
                    if density == "sparse":
                        effective_cap = effective_cap // 2
                    effective_capacity[room_id] = effective_cap

                # New logic: For large courses, try to allocate across multiple rooms
                students_to_allocate = list(students)
                students_left = len(students_to_allocate)
                current_building = course_buildings.get(course_id)
                course_allocations = []

                # First try rooms in the same building if previously assigned
                if current_building:
                    same_building_rooms = sorted(
                        [
                            (r, effective_capacity[r])
                            for r in effective_capacity.keys()
                            if r.startswith(current_building)
                            and effective_capacity[r] > 0
                        ],
                        key=lambda x: x[1],
                        reverse=True,
                    )

                    # Allocate to rooms in the same building first
                    for room_id, room_capacity in same_building_rooms:
                        if students_left <= 0:
                            break

                        # Determine how many students we can allocate to this room
                        students_to_place = min(room_capacity, students_left)

                        if students_to_place > 0:
                            # Extract the students for this room
                            room_students = students_to_allocate[:students_to_place]
                            students_to_allocate = students_to_allocate[
                                students_to_place:
                            ]
                            students_left -= students_to_place

                            course_allocations.append(
                                {
                                    "date": date,
                                    "slot": slot,
                                    "course_id": course_id,
                                    "room_id": room_id,
                                    "capacity": remaining_capacity[room_id],
                                    "enrollment": students_to_place,
                                    "roll_numbers": ";".join(room_students),
                                }
                            )

                            remaining_capacity[room_id] -= students_to_place

                # If there are still students to allocate, try any available rooms
                if students_left > 0:
                    # Sort rooms by capacity for efficient allocation
                    sorted_rooms = sorted(
                        [
                            (r, effective_capacity[r])
                            for r in effective_capacity.keys()
                            if effective_capacity[r] > 0
                        ],
                        key=lambda x: x[1],
                        reverse=True,
                    )

                    for room_id, room_capacity in sorted_rooms:
                        if students_left <= 0:
                            break

                        # Extract building ID (assuming format like "B101" where "B" is the building)
                        building = (
                            room_id.split("-")[0] if "-" in room_id else room_id[0]
                        )

                        # Set the course building if this is the first allocation for this course
                        if not current_building:
                            course_buildings[course_id] = building
                            current_building = building

                        # Determine how many students we can allocate to this room
                        students_to_place = min(room_capacity, students_left)

                        if students_to_place > 0:
                            # Extract the students for this room
                            room_students = students_to_allocate[:students_to_place]
                            students_to_allocate = students_to_allocate[
                                students_to_place:
                            ]
                            students_left -= students_to_place

                            course_allocations.append(
                                {
                                    "date": date,
                                    "slot": slot,
                                    "course_id": course_id,
                                    "room_id": room_id,
                                    "capacity": remaining_capacity[room_id],
                                    "enrollment": students_to_place,
                                    "roll_numbers": ";".join(room_students),
                                }
                            )

                            remaining_capacity[room_id] -= students_to_place

                # Check if all students were allocated
                if students_left > 0:
                    error_msg = f"Cannot allocate classroom for course {course_id} with enrollment {enrollment}"
                    logging.error(error_msg)
                    print(error_msg)
                else:
                    # Add all allocations for this course
                    allocations.extend(course_allocations)

                    # Add these students to the set of allocated students for this slot
                    slot_allocated_students.update(students)

            # Add the allocated students for this slot to the overall set
            allocated_students.update(slot_allocated_students)

        # Create DataFrame from allocations
        allocation_df = pd.DataFrame(allocations)

        if allocation_df.empty:
            logging.warning(
                "No allocations were made. All rooms may be too small for the courses."
            )
            return pd.DataFrame(
                columns=[
                    "date",
                    "slot",
                    "course_id",
                    "room_id",
                    "capacity",
                    "enrollment",
                    "roll_numbers",
                ]
            )

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
    # Sort by seats left in descending order to see which rooms have the most capacity remaining
    return pd.DataFrame(seats_left).sort_values(by="seats_left", ascending=False)


def create_individual_seating_plans(allocation_df):
    """Create individual seating plan Excel files for each course-classroom combination."""
    try:
        # Group allocations by course to generate summaries
        course_groups = allocation_df.groupby(["date", "slot", "course_id"])

        # Track courses allocated to multiple rooms
        courses_in_multiple_rooms = []

        for (date, slot, course_id), group in course_groups:
            formatted_date = date.replace("/", "_")
            slot_folder = slot.capitalize()

            # Create directory structure
            output_dir = f"data/output/{formatted_date}/{slot_folder}"
            os.makedirs(output_dir, exist_ok=True)

            # For each room allocation
            room_count = len(group)
            for _, row in group.iterrows():
                room_id = row["room_id"]

                # Individual room seating plan file
                output_file = (
                    f"{output_dir}/{formatted_date}_{course_id}_{room_id}.xlsx"
                )

                # Create seating plan DataFrame for this room
                seating_data = {
                    "course_id": [course_id],
                    "room_id": [room_id],
                    "date": [date],
                    "slot": [slot],
                    "enrollment": [row["enrollment"]],
                    "roll_numbers": [row["roll_numbers"]],
                }

                # Add multi-room indicator if applicable
                if room_count > 1:
                    seating_data["multi_room"] = [
                        f"Room {list(group['room_id']).index(room_id) + 1} of {room_count}"
                    ]

                seating_df = pd.DataFrame(seating_data)
                seating_df.to_excel(output_file, index=False, engine="openpyxl")

            # If course is allocated across multiple rooms, create a summary file
            if room_count > 1:
                courses_in_multiple_rooms.append(
                    {
                        "course_id": course_id,
                        "date": date,
                        "slot": slot,
                        "rooms": ", ".join(group["room_id"]),
                        "room_count": room_count,
                        "total_enrollment": group["enrollment"].sum(),
                    }
                )

                # Create summary file
                summary_file = f"{output_dir}/{formatted_date}_{course_id}_summary.xlsx"
                summary_df = pd.DataFrame(
                    [
                        {
                            "course_id": course_id,
                            "date": date,
                            "slot": slot,
                            "total_enrollment": group["enrollment"].sum(),
                            "rooms": ", ".join(group["room_id"]),
                            "room_count": room_count,
                        }
                    ]
                )
                summary_df.to_excel(summary_file, index=False, engine="openpyxl")

        # Create a master list of courses allocated to multiple rooms
        if courses_in_multiple_rooms:
            multi_room_df = pd.DataFrame(courses_in_multiple_rooms)
            multi_room_file = "data/output/courses_in_multiple_rooms.xlsx"
            logging.info(
                f"{len(courses_in_multiple_rooms)} courses allocated across multiple rooms"
            )
            print(
                f"{len(courses_in_multiple_rooms)} courses allocated across multiple rooms"
            )
            multi_room_df.to_excel(multi_room_file, index=False, engine="openpyxl")

    except Exception as e:
        logging.error(f"Error creating individual seating plans: {str(e)}")
        raise
