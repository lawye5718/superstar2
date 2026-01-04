"""Custom exceptions"""

class SuperstarException(Exception):
    """Base exception for Superstar application"""
    def __init__(self, message: str = "Superstar application error", status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)