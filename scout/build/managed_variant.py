import logging
from scout.models.managed_variant import ManagedVariant

LOG = logging.getLogger(__name__)


def build_managed_variant(managed_variant_info):
    """Build a managed_variant object
    Args:
        managed_variant_info(dict): Compare scout.models.ManagedVariant for details

    Returns:
        managed_variant_obj(scout.models.ManagedVariant): A dictionary with variant information

    """

    end = managed_variant_info.get("end", None)
    if end:
        managed_variant_info["end"] = int(end)
    try:
        managed_variant = ManagedVariant(
            chromosome=str(managed_variant_info["chromosome"]),
            position=int(managed_variant_info["position"]),
            end=managed_variant_info.get("end", None),
            reference=managed_variant_info["reference"],
            alternative=managed_variant_info["alternative"],
            build=managed_variant_info.get("build", "37"),
            maintainer=managed_variant_info.get("", []),
            institute=managed_variant_info.get("institute", ""),
            category=managed_variant_info.get("category", "snv"),
            sub_category=managed_variant_info.get("sub_category", "snv"),
            description=managed_variant_info.get("description", ""),
        )
    except KeyError:
        raise KeyError("Managed variant has to have chr, pos, ref and alt.")

    LOG.debug("Built managed variant %s", managed_variant.get("display_id"))

    return managed_variant
