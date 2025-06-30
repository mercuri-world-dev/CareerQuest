from typing import TypeVar, Generic

T = TypeVar('T')

class Result(Generic[T]):
    """
    A generic Result class to encapsulate the outcome of an operation.
    
    Attributes:
        success (bool): Indicates if the operation was successful.
        data (T): The result data if the operation was successful.
        error (str): An error message if the operation failed.
    """
    
    def __init__(self, success: bool, data: T = None, error: str = None):
        self.success = success
        self.data = data
        self.error = error
    
    def is_success(self) -> bool:
        """Check if the operation was successful."""
        return self.success
    
    def __repr__(self):
        return f"Result(success={self.success}, data={self.data}, error={self.error})"