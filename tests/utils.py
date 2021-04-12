import random
import string
from typing import Any, Dict


def generate_username() -> str:
    """Creates a random valid sa user name

    Returns:
        str: [description]
    """
    return "".join(random.choices(string.ascii_letters + string.digits, k=15))


def is_sub_dict(main: Dict[str, Any], sub: Dict[str, Any]) -> bool:
    """Check if sub dict is in main dict

    Args:
        main (Dict[str, Any]): [description]
        sub (Dict[str, Any]): [description]

    Returns:
        bool: [description]
    """
    return all(main.get(key, None) == val for key, val in sub.items())
