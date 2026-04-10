import logging

from scout.models.individual import Individual

log = logging.getLogger(__name__)


def build_individual(ind: dict) -> dict:
    """Build an Individual object using Pydantic validation.

    Wraps the Pydantic Individual model for backward compatibility.
    Validates individual data for database insertion.

    Args:
        ind: Dictionary with individual information (individual_id required)

    Returns:
        dict: Validated individual data ready for database insertion

    Raises:
        PedigreeError: If required fields missing or invalid
    """
    individual_id = ind.get("individual_id")
    log.info(f"Building Individual with id: {individual_id}")

    # Create and validate using Pydantic model
    individual = Individual(**ind)
    return individual.to_dict()
