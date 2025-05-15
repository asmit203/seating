# Configuration settings for the seating arrangement system

# Default buffer and density settings
BUFFER = 5  # Default buffer size for classroom allocation
SPARSE_DENSE = {
    "sparse": 0.5,  # Ratio for sparse filling of classrooms (50%)
    "dense": 1.0,  # Ratio for dense filling of classrooms (100%)
}

# Path settings
INPUT_DIR = "data/input"
OUTPUT_DIR = "data/output"
LOG_DIR = "logs"

# Input file paths
INPUT_FILES = {
    "roll_name_mapping": f"{INPUT_DIR}/in_roll_name_mapping.xlsx",
    "courses": f"{INPUT_DIR}/in_courses.xlsx",
    "classrooms": f"{INPUT_DIR}/in_classrooms.xlsx",
}

# Output file paths
OUTPUT_FILES = {
    "seating_arrangement": f"{OUTPUT_DIR}/op_overall_seating_arrangement.xlsx",
    "seats_left": f"{OUTPUT_DIR}/op_seats_left.xlsx",
}

# Log file settings
LOG_FILE_PATH = f"{LOG_DIR}/errors.txt"  # Path to the error log file
INPUT_FOLDER = "../data/input/"  # Input data folder
OUTPUT_FOLDER = "../data/output/"  # Output data folder

# Excel file names
ROLL_NAME_MAPPING_FILE = "in_roll_name_mapping.xlsx"
COURSES_FILE = "in_courses.xlsx"
CLASSROOMS_FILE = "in_classrooms.xlsx"
OVERALL_SEATING_OUTPUT_FILE = "op_overall_seating_arrangement.xlsx"
SEATS_LEFT_OUTPUT_FILE = "op_seats_left.xlsx"
