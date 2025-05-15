import pandas as pd
import os
import logging


def read_excel(file_path):
    """Read an Excel file and return its contents as a DataFrame."""
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist.")
        # Explicitly specify engine to avoid detection issues
        return pd.read_excel(file_path, engine="openpyxl")
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {str(e)}")
        raise


def write_excel(file_path, dataframe):
    """Write a DataFrame to an Excel file."""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        dataframe.to_excel(file_path, index=False, engine="openpyxl")
    except Exception as e:
        logging.error(f"Error writing to file {file_path}: {str(e)}")
        raise


def read_roll_name_mapping(file_path):
    """Read the roll number to name mapping and return as a dictionary."""
    df = read_excel(file_path)
    return dict(zip(df["Roll Number"].astype(str), df["Name"].fillna("Unknown Name")))
    return df


def write_seating_arrangement(output_path, overall_seating, seats_left):
    write_excel(output_path + "/op_overall_seating_arrangement.xlsx", overall_seating)
    write_excel(output_path + "/op_seats_left.xlsx", seats_left)
