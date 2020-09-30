""" Managed variant

    For potentially causative variants that are not yet in ClinVar
    and have yet not been marked causative in any existing case.

"""

from datetime import datetime
from scout.utils.md5 import generate_md5_key


class ManagedVariant(dict):
    """
    # required primary fields
    chromosome=str,  # required
    position=int,  # required
    end=int,  # required
    reference=str,  # required
    alternative=str,  # required
    build=str, # required, ["37","38"], default "37"
    date=datetime.datetime
    # required derived fields
    # display name is variant_id (no md5) chrom_pos_ref_alt (simple_id)
    display_name=str,  # required

    #optional fields
    # maintainer user_id list
    maintainer=list(user_id), # optional
    institute=institute_id, # optional

    # optional fields foreseen for future use
    category=str,  # choices=('sv', 'snv', 'str', 'cancer', 'cancer_sv')
    sub_category=str,  # choices=('snv', 'indel', 'del', 'ins', 'dup', 'inv', 'cnv', 'bnd', 'str')
    description=str,
    """

    def __init__(
        self,
        chromosome,
        position,
        end,
        reference,
        alternative,
        institute,
        maintainer=[],
        build="37",
        date=None,
        category="snv",
        sub_category="snv",
        description=None,
    ):
        super(ManagedVariant, self).__init__()
        self["chromosome"] = str(chromosome)
        self["position"] = position
        self["end"] = end
        self["reference"] = reference
        self["alternative"] = alternative
        self["build"] = build

        self["managed_variant_id"] = "_".join(
            [
                str(part)
                for part in (
                    chromosome,
                    position,
                    reference,
                    alternative,
                    category,
                    sub_category,
                    build,
                )
            ]
        )
        self["display_id"] = "_".join(
            [str(part) for part in (chromosome, position, reference, alternative)]
        )
        self["variant_id"] = generate_md5_key(
            [str(part) for part in (chromosome, position, reference, alternative, "clinical")]
        )
        self["date"] = date or datetime.now()

        self["institute"] = institute or None
        self["maintainer"] = maintainer or []
        self["category"] = category
        self["sub_category"] = sub_category
        self["description"] = description
