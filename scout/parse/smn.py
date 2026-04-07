from scout.utils.convert import convert_number, make_bool_pass_none


def parse_smn_file(lines):
    """Parse a SMNCopyNumberCaller TSV file.

    Args:
        lines(iterable(str))

    Returns:
        list(sma_info_per_individual(dict))
    """
    individuals = []
    header = []

    for i, line in enumerate(lines):
        line = line.rstrip()
        if i == 0:
            # Header line
            header = line.split("\t")
        else:
            ind_info = dict(zip(header, line.split("\t")))
            smn_ind_info = {}
            smn_ind_info["sample_id"] = ind_info["Sample"]
            smn_ind_info["is_sma"] = make_bool_pass_none(ind_info["isSMA"])
            smn_ind_info["is_sma_carrier"] = make_bool_pass_none(ind_info["isCarrier"])
            smn_ind_info["smn1_cn"] = convert_number(ind_info["SMN1_CN"])
            smn_ind_info["smn2_cn"] = convert_number(ind_info["SMN2_CN"])
            smn_ind_info["smn2delta78_cn"] = convert_number(ind_info["SMN2delta7-8_CN"])
            smn_ind_info["smn_27134_cn"] = convert_number(ind_info["g.27134T>G_CN"])

            individuals.append(smn_ind_info)

    return individuals
