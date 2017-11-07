"""A module to prove a way of locating and loading test resource files.

This is akin to the `iati.resources` module, but deals with test data.

"""
import iati.resources


def load_as_dataset(file_path):
    """Load a specified test data file as a Dataset.

    Args:
        file_path (str): The path of the file, relative to the root test data folder. Folders should be separated by a forward-slash (`/`).

    Returns:
        dataset: A Dataset containing the contents of the file at the specified location.

    Raises:
        iati.exceptions.ValidationError: If the provided XML does not conform to the IATI standard.

    """
    return iati.resources.load_as_dataset(iati.resources.get_test_data_path(file_path))


def load_as_string(file_path):
    """Load a specified test data file as a string.

    Args:
        file_path (str): The path of the file, relative to the root test data folder. Folders should be separated by a forward-slash (`/`).

    Returns:
        str (python3) / unicode (python2): The contents of the file at the specified location.

    """
    return iati.resources.load_as_string(iati.resources.get_test_data_path(file_path))
