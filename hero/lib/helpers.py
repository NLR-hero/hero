def kwargs_to_json_for_request(**kwargs):
    """
    Converts a set of kwargs into a JSON object for request params and the like.

    Note: The keys must match what the API is expecting not what is pythonic. Use camelCase instead of snake_case, for example:

    ```py
    the_answer = 42
    no_way = None # will be removed since it is None

    kwargs_to_json_for_request(theAnswer=the_answer, noWay=no_way)

    -> {myValue=42}
    ```
    """
    return {k: v for k, v in kwargs.items() if v is not None}
