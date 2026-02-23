# Import required modules and packages
import yaml
from .logs import die


def read_config(fname: str) -> dict:
    """
    Load a YAML configuration file and return its contents as a dictionary.

    This function reads the specified YAML file and parses its contents.
    If the file cannot be parsed correctly, the program exits using the
    `die` function from the logging module.

    Args:
        fname (str): Path to the YAML configuration file.

    Returns:
        dict: Dictionary containing the configuration parameters from the YAML file.

    Raises:
        SystemExit: If there is an error parsing the YAML file, `die` is called and
        the program exits.
    """
    try:
        with open(fname) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
    except yaml.YAMLError as err:
        die(err)
    return data
