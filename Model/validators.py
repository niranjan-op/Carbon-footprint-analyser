import re
from django.core.exceptions import ValidationError
def validate_financial_year(value):
    """
    Validate that the financial year is in the format YYYY-YYYY.
    """
    pattern = r'^20\d{2}-20\d{2}$'
    if not re.match(pattern, value):
        raise ValidationError(
            f'{value} is not a valid financial year. It should be in the format YYYY-YYYY.'
        )
    else:
        start_year, end_year = map(int, value.split('-'))
        if end_year - start_year != 1:
            raise ValidationError(
                f'{value} is not a valid financial year. The end year must be one year after the start year.'
            )