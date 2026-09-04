class AppError(Exception):
	code: str
	message: str

	def __init__(self, code: str, message: str) -> None:
		super().__init__(message)
		self.code = code
		self.message = message


class ResourceNotFoundError(AppError):
	def __init__(self, code: str = "RESOURCE_NOT_FOUND", message: str = "resource not found") -> None:
		super().__init__(
			code=code,
			message=message,
		)


class AppValidationError(AppError):
	def __init__(self, code: str = "VALIDATION_ERROR", message: str = "request validation failed") -> None:
		super().__init__(
			code=code,
			message=message,
		)
