import random, string

def generate_id(length: int = 8) -> str:
    """Generates a random ID of a given length.

    Args:
        length: The length of the ID to generate.

    Returns:
        The generated ID.
    """
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))
