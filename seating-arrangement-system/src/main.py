import logging
import os
import sys
from seating_arrangement import SeatingArrangement
from datetime import datetime


def setup_logging():
    """Set up logging configuration with timestamps."""
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)

    # Create a log file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"logs/seating_arrangement_{timestamp}.log"

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)],
    )

    return log_file


def validate_buffer(buffer_str):
    """Validate the buffer input."""
    try:
        buffer = int(buffer_str)
        if buffer < 0:
            raise ValueError("Buffer must be a non-negative integer.")
        return buffer
    except ValueError:
        raise ValueError("Buffer must be a non-negative integer.")


def validate_density(density_str):
    """Validate the density input."""
    density = density_str.lower()
    if density not in ["sparse", "dense"]:
        raise ValueError("Density must be either 'Sparse' or 'Dense'.")
    return density


def main():
    log_file = setup_logging()
    logging.info("Starting seating arrangement system")

    try:
        # Initialize the seating arrangement system
        seating_arrangement_system = SeatingArrangement()

        # Get and validate user inputs
        while True:
            try:
                buffer_input = input(
                    "Enter the buffer size (number of seats to reserve in each room): "
                ).strip()
                buffer = validate_buffer(buffer_input)
                break
            except ValueError as e:
                print(f"Error: {e} Please try again.")

        while True:
            try:
                density_input = input(
                    "Enter the seating density (Sparse/Dense): "
                ).strip()
                density = validate_density(density_input)
                break
            except ValueError as e:
                print(f"Error: {e} Please try again.")

        logging.info(f"Configuration: Buffer={buffer}, Density={density}")
        print(f"Configuration set: Buffer={buffer}, Density={density}")

        # Process the seating arrangement
        start_time = datetime.now()
        seating_arrangement_system.process_seating(buffer, density)
        end_time = datetime.now()

        duration = (end_time - start_time).total_seconds()
        logging.info(f"Seating arrangement completed in {duration:.2f} seconds")
        print(f"Seating arrangement completed in {duration:.2f} seconds")
        print(f"Log file created at: {log_file}")

    except KeyboardInterrupt:
        logging.warning("Process interrupted by user")
        print("\nProcess interrupted by user. Exiting...")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}", exc_info=True)
        print(f"An error occurred: {str(e)}")
        print(f"Please check the log file for more details: {log_file}")


if __name__ == "__main__":
    main()
