# seating_arrangement.py

import os
import pandas as pd
import logging
import time
from datetime import datetime
from utils.file_handler import read_excel, write_excel
from utils.classroom_allocator import allocate_classrooms
from utils.conflict_checker import check_conflicts, display_conflicts
from config.settings import BUFFER, SPARSE_DENSE


class SeatingArrangement:
    def __init__(self):
        """Initialize the seating arrangement system."""
        # Make sure output directories exist
        os.makedirs("data/output", exist_ok=True)
        os.makedirs("logs", exist_ok=True)

    def process_seating(self, buffer, sparse_dense):
        """
        Process the seating arrangement based on given parameters.

        Args:
            buffer (int): Number of buffer seats to keep in each classroom
            sparse_dense (str): Either 'sparse' or 'dense' seating arrangement

        Returns:
            tuple: (seating_arrangement DataFrame, conflicts list)
        """
        start_time = time.time()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        try:
            logging.info("Starting seating arrangement process")
            print("Starting seating arrangement process...")

            # Create output directory with timestamp
            output_dir = f"data/output/run_{timestamp}"
            os.makedirs(output_dir, exist_ok=True)

            # Load input data
            print("Loading input data...")
            roll_name_mapping = read_excel("data/input/in_roll_name_mapping.xlsx")
            courses = read_excel("data/input/in_courses.xlsx")
            classrooms = read_excel("data/input/in_classrooms.xlsx")

            logging.info(
                f"Loaded {len(courses)} courses and {len(classrooms)} classrooms"
            )
            print(f"Loaded {len(courses)} courses and {len(classrooms)} classrooms")

            # Validate user input
            if sparse_dense not in ["sparse", "dense"]:
                raise ValueError(
                    "Invalid input for Sparse/Dense. Please enter 'Sparse' or 'Dense'."
                )

            # Check for scheduling conflicts before allocation
            print("Checking for scheduling conflicts...")
            conflicts = check_conflicts(courses)

            # Allocate classrooms
            print(
                f"Allocating classrooms with buffer={buffer}, density={sparse_dense}..."
            )
            seating_arrangement = allocate_classrooms(
                courses, classrooms, buffer, sparse_dense
            )

            # Save run metadata
            metadata = {
                "timestamp": timestamp,
                "buffer": buffer,
                "density": sparse_dense,
                "num_courses": len(courses),
                "num_classrooms": len(classrooms),
                "num_allocations": len(seating_arrangement),
                "num_conflicts": len(conflicts),
                "execution_time_seconds": time.time() - start_time,
            }
            pd.DataFrame([metadata]).to_excel(
                f"{output_dir}/metadata.xlsx", index=False
            )

            # Write outputs to Excel
            output_file = "data/output/op_overall_seating_arrangement.xlsx"
            write_excel(output_file, seating_arrangement)

            # Also save a copy in the timestamped directory
            seating_arrangement.to_excel(
                f"{output_dir}/seating_arrangement.xlsx", index=False
            )

            # Create a simple HTML summary for easy viewing
            create_html_summary(
                seating_arrangement, conflicts, metadata, f"{output_dir}/summary.html"
            )

            print("\n" + "=" * 50)
            print("SEATING ARRANGEMENT SUMMARY")
            print("=" * 50)
            print(f"Total courses processed: {len(courses)}")
            print(f"Total classrooms available: {len(classrooms)}")
            print(f"Buffer seats per classroom: {buffer}")
            print(f"Seating density: {sparse_dense.capitalize()}")
            print(f"Total allocations created: {len(seating_arrangement)}")

            # Display conflicts if any
            display_conflicts(conflicts)

            execution_time = time.time() - start_time
            print(f"\nExecution completed in {execution_time:.2f} seconds")
            print(f"Results saved to: {output_file}")
            logging.info(
                f"Seating arrangement completed successfully in {execution_time:.2f} seconds"
            )

            return seating_arrangement, conflicts

        except Exception as e:
            logging.error(f"An error occurred: {str(e)}", exc_info=True)
            print(f"An error occurred: {str(e)}")
            print("Please check the logs for more details.")
            return None, None


def create_html_summary(seating_arrangement, conflicts, metadata, output_file):
    """Create a simple HTML summary of the seating arrangement."""
    try:
        # Group by date and slot
        date_slot_groups = seating_arrangement.groupby(["date", "slot"])

        # Create HTML content
        html_content = f"""<!DOCTYPE html>
        <html>
        <head>
            <title>Seating Arrangement Summary</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1, h2, h3 {{ color: #2c3e50; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .summary-box {{ background-color: #f8f9fa; border: 1px solid #e9ecef; padding: 15px; margin-bottom: 20px; border-radius: 5px; }}
                .conflict {{ color: red; }}
            </style>
        </head>
        <body>
            <h1>Seating Arrangement Summary</h1>
            
            <div class="summary-box">
                <h2>Run Information</h2>
                <p><strong>Timestamp:</strong> {metadata['timestamp']}</p>
                <p><strong>Buffer:</strong> {metadata['buffer']} seats</p>
                <p><strong>Density:</strong> {metadata['density'].capitalize()}</p>
                <p><strong>Courses:</strong> {metadata['num_courses']}</p>
                <p><strong>Classrooms:</strong> {metadata['num_classrooms']}</p>
                <p><strong>Allocations:</strong> {metadata['num_allocations']}</p>
                <p><strong>Conflicts:</strong> <span class="{'conflict' if metadata['num_conflicts'] > 0 else ''}">{metadata['num_conflicts']}</span></p>
                <p><strong>Execution Time:</strong> {metadata['execution_time_seconds']:.2f} seconds</p>
            </div>
        """

        # Add schedule table
        html_content += """
            <h2>Schedule Overview</h2>
            <table>
                <tr>
                    <th>Date</th>
                    <th>Slot</th>
                    <th>Courses</th>
                    <th>Rooms</th>
                    <th>Students</th>
                </tr>
        """

        for (date, slot), group in date_slot_groups:
            courses_count = group["course_id"].nunique()
            rooms_count = group["room_id"].nunique()
            students_count = group["enrollment"].sum()

            html_content += f"""
                <tr>
                    <td>{date}</td>
                    <td>{slot}</td>
                    <td>{courses_count}</td>
                    <td>{rooms_count}</td>
                    <td>{students_count}</td>
                </tr>
            """

        html_content += """
            </table>
        """

        # Add conflicts section if there are conflicts
        if conflicts:
            html_content += """
                <h2 class="conflict">Conflicts Detected</h2>
                <p>The following students have scheduling conflicts:</p>
                <table>
                    <tr>
                        <th>Student</th>
                        <th>Date</th>
                        <th>Slot</th>
                        <th>Course 1</th>
                        <th>Course 2</th>
                    </tr>
            """

            for conflict in conflicts[
                :100
            ]:  # Limit to 100 conflicts to avoid huge HTML files
                html_content += f"""
                    <tr>
                        <td>{conflict['roll_number']}</td>
                        <td>{conflict['date']}</td>
                        <td>{conflict['slot']}</td>
                        <td>{conflict['course1']}</td>
                        <td>{conflict['course2']}</td>
                    </tr>
                """

            if len(conflicts) > 100:
                html_content += f"""
                    <tr>
                        <td colspan="5">... and {len(conflicts) - 100} more conflicts (see Excel reports for full details)</td>
                    </tr>
                """

            html_content += """
                </table>
            """

        # Close HTML
        html_content += """
        </body>
        </html>
        """

        # Write to file
        with open(output_file, "w") as f:
            f.write(html_content)

    except Exception as e:
        logging.error(f"Error creating HTML summary: {str(e)}")


# For direct execution of this module
def main():
    seating = SeatingArrangement()
    buffer = int(input("Enter buffer size: ").strip())
    sparse_dense = input("Enter Sparse or Dense: ").strip().lower()
    seating.process_seating(buffer, sparse_dense)


if __name__ == "__main__":
    main()
