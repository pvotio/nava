class InvalidTemplateIDError(Exception):
    """Raised when the template_id is invalid."""

    pass


class InvalidArgsError(Exception):
    """Raised when one or more required arguments are missing."""

    def __init__(self, missing_args):
        super().__init__(f"Missing arguments: {', '.join(missing_args)}")
        self.missing_args = missing_args


class NoDataFoundError(Exception):
    """Raised when no data is found for the given arguments."""

    pass


class ReportGenerationError(Exception):
    """Raised when an unexpected error occurs during report generation."""

    pass


class DatabaseConnectionError(Exception):
    """Raised when cannot establish a connection with a database."""

    pass
