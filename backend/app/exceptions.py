class AppException(Exception):
    """Base application exception."""
    
    def __init__(self, message: str, status_code: int = 400, detail: str = None):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)


class DatasetNotFoundError(AppException):
    def __init__(self, dataset_id: str):
        super().__init__(
            message=f"Dataset not found: {dataset_id}",
            status_code=404,
            detail="The requested dataset does not exist or you don't have access.",
        )


class ModelTrainingError(AppException):
    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=500,
            detail="An error occurred during model training.",
        )


class FileValidationError(AppException):
    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=422,
            detail="The uploaded file did not pass validation.",
        )


class AuthenticationError(AppException):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            status_code=401,
            detail="Invalid or missing authentication token.",
        )
