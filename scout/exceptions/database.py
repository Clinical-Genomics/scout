"""The following exceptions follow PEP249:
    https://www.python.org/dev/peps/pep-0249
"""


class DatabaseError(Exception):
    """Exception raised for errors that are related to the database."""

    pass


class IntegrityError(DatabaseError):
    """Exception raised when the relational integrity of the database
    is affected, e.g. a foreign key check fails."""

    pass


class OperationalError(DatabaseError):
    """Exception raised for errors that are related to the database's
    operation and not necessarily under the control of the programmer,
    e.g. an unexpected disconnect occurs, the data source name is not
    found, a transaction could not be processed, a memory allocation
    error occurred during processing, etc."""

    pass


class DataError(DatabaseError):
    """Exception raised for errors that are due to problems with the processed data like division by
    zero, numeric value out of range, etc. It must be a subclass of DatabaseError."""

    pass


class DataNotFoundError(DataError):
    """Requested data object not found in the database"""

    pass
