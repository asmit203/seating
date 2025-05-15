# Seating Arrangement System

A comprehensive system for allocating classrooms to exam courses based on enrollment and room capacity while optimizing for various constraints such as:

- Largest courses first allocation priority
- Minimizing rooms for large courses
- Keeping courses in the same building when possible
- Configurable buffer space for classrooms
- Sparse/Dense seating options
- Conflict detection between student schedules

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Input Format](#input-format)
- [Output Format](#output-format)
- [Configuration](#configuration)
- [Advanced Features](#advanced-features)
- [Troubleshooting](#troubleshooting)

## Features

- **Smart Classroom Allocation**: Prioritizes the largest courses first and efficiently allocates rooms
- **Multi-Room Support**: Automatically splits large courses across multiple rooms when necessary
- **Building Optimization**: Attempts to keep courses in the same building to minimize student movement
- **Conflict Detection**: Identifies and reports students assigned to multiple exams in the same slot
- **Configurable Seating**: Supports both sparse (socially distanced) and dense seating arrangements
- **Detailed Reporting**: Generates comprehensive reports and seating plans

## Project Structure

```
seating-arrangement-system
├── src
│   ├── main.py                   # Entry point for the application
│   ├── seating_arrangement.py     # Main logic for seating arrangement
│   ├── convert_to_excel.py        # Script to convert CSV files to Excel
│   ├── utils
│   │   ├── __init__.py           # Marks the utils directory as a package
│   │   ├── file_handler.py        # Functions for reading/writing Excel files
│   │   ├── classroom_allocator.py  # Logic for allocating classrooms
│   │   └── conflict_checker.py     # Functions to check for scheduling conflicts
│   ├── config
│   │   ├── __init__.py           # Marks the config directory as a package
│   │   └── settings.py           # Configuration settings for the application
│   └── models
│       ├── __init__.py           # Marks the models directory as a package
│       ├── course.py              # Course class definition
│       ├── student.py             # Student class definition
│       └── classroom.py           # Classroom class definition
├── data
│   ├── input
│   │   ├── in_roll_name_mapping.xlsx  # Mapping of student roll numbers to names
│   │   ├── in_courses.xlsx             # Information about courses and enrollments
│   │   └── in_classrooms.xlsx          # Information about available classrooms
│   └── output
│       ├── op_overall_seating_arrangement.xlsx  # Overall seating arrangement
│       ├── op_seats_left.xlsx                   # Remaining seats in classrooms
│       ├── courses_in_multiple_rooms.xlsx       # Courses split across rooms
│       ├── conflicts/                           # Conflict reports directory
│       └── [date]/[slot]/                       # Individual seating plans
├── logs
│   └── seating_arrangement_[timestamp].log      # Log files
└── README.md                                    # This file
```

## Installation

### Prerequisites

- Python 3.8+
- pandas
- openpyxl

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/seating-arrangement-system.git
   cd seating-arrangement-system
   ```

2. Install dependencies:

   ```bash
   pip install pandas openpyxl
   ```

3. Prepare the data files in the `data/input` directory (see [Input Format](#input-format))

## Usage

### Basic Usage

Run the main script:

```bash
python src/main.py
```

You will be prompted to enter:

- Buffer size (number of seats to reserve in each room)
- Seating density ("sparse" or "dense")

### Converting CSV Files to Excel

If your data is in CSV format, you can use the conversion script:

```bash
python src/convert_to_excel.py
```

This will convert all CSV files in the `data/input` directory to Excel format.

## Input Format

The system requires the following input files in the `data/input` directory:

1. **in_roll_name_mapping.xlsx**

   - Contains the mapping between student roll numbers and names
   - Columns: `roll_number`, `name`

2. **in_courses.xlsx**

   - Contains information about courses and their enrollments
   - Columns: `course_id`, `enrollment`, `date`, `slot`, `roll_numbers`

3. **in_classrooms.xlsx**
   - Contains information about available classrooms
   - Columns: `room_id`, `capacity`

## Output Format

The system generates the following outputs in the `data/output` directory:

1. **op_overall_seating_arrangement.xlsx**

   - Main output containing the complete seating arrangement
   - Includes course assignments to rooms with student counts

2. **op_seats_left.xlsx**

   - Summary of remaining capacity in each classroom after allocation

3. **courses_in_multiple_rooms.xlsx**

   - List of courses that were allocated across multiple rooms

4. **Folder structure for each date and slot**

   - Individual seating plans for each course-room combination
   - Organized in folders by date and slot

5. **conflicts/** directory
   - Detailed conflict reports if any scheduling conflicts are detected

## Configuration

The system can be configured in several ways:

### Buffer Size

The buffer size determines how many seats to reserve in each classroom. This can be useful for:

- Accommodating late arrivals
- Reserving seats for invigilators
- Maintaining space between students

### Seating Density

Two seating density options are available:

- **Sparse**: Capacity is halved to allow for social distancing (every other seat)
- **Dense**: Full capacity is used with only the buffer reduction

### Advanced Configuration

For advanced configuration options, edit `src/config/settings.py`:

```python
# Default buffer and seating density
BUFFER = 2
SPARSE_DENSE = "sparse"
```

## Advanced Features

### Multi-Room Allocation for Large Courses

When a course is too large for a single classroom, the system will automatically:

1. Try to find rooms in the same building
2. Allocate students across multiple rooms optimally
3. Create summary files for courses in multiple rooms

### Conflict Detection and Resolution

The system checks for students assigned to multiple courses in the same time slot and:

1. Logs all conflicts found
2. Generates detailed conflict reports
3. Provides summaries by student, course, and time slot

## Troubleshooting

### Common Issues

1. **"Cannot allocate classroom" error**

   - This indicates there isn't enough classroom capacity for a course
   - Try using a smaller buffer or "dense" seating option
   - Consider splitting very large courses manually

2. **Conflict detection reports**

   - Review the conflict reports in `data/output/conflicts/`
   - Update course schedules to resolve conflicts
   - Or manually reassign students to avoid conflicts

3. **File not found errors**
   - Ensure all required input files are in `data/input/`
   - Check file naming conventions match the expected format

### Logs

Detailed logs are saved in the `logs/` directory to help diagnose issues.
│ └── op_seats_left.xlsx # Remaining seats after allocation
├── logs
│ └── errors.txt # Logs any errors encountered during execution
├── tests
│ ├── **init**.py # Marks the tests directory as a package
│ ├── test_allocator.py # Unit tests for classroom allocation logic
│ └── test_conflict_checker.py # Unit tests for conflict checking logic
├── requirements.txt # Lists dependencies required for the project
└── README.md # Documentation for the project

```

## Setup Instructions

1. Clone the repository:
```

git clone <repository-url>
cd seating-arrangement-system

```

2. Install the required dependencies:
```

pip install -r requirements.txt

```

3. Prepare the input data:
- Ensure that the input Excel files are placed in the `data/input` directory.

4. Run the application:
```

python3 src/seating_arrangement.py

```

## Usage Guidelines

- The application will prompt for user inputs such as buffer size and seating density (sparse/dense).
- It will process the input data and generate output files in the `data/output` directory.
- Check the `logs/errors.txt` file for any errors encountered during execution.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
```
