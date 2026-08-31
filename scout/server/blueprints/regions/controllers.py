def regions(store, query, build):
    """Fetch matching regions and convert to JSON."""
    region_query_result = store.get_regions(build, query)
    region_terms = [
        {
            "chrom": region["chromosome"],
            "start": region["start"],
            "end": region["end"],
            "name": "{} | {}".format(region["isca_id"], region["display_name"]),
        }
        for region in region_query_result
    ]
    return region_terms


def region(store, query, build):
    """Fetch a single region and convert to JSON."""
    region_query_result = store.get_regions(build, query)
    if not region_query_result:
        return None
    region = region_query_result[0]
    region_term = {
        "chrom": region["chromosome"],
        "start": region["start"],
        "end": region["end"],
        "name": "{} | {}".format(region["isca_id"], region["display_name"]),
    }
    return region_term


def regions_to_json(store, query, build):
    """Fetch matching regions and convert to JSON."""
    region_query_result = store.get_regions(build, query)
    json_terms = {
        region["isca_id"]: {
            "name": "{} | {}".format(
                region["isca_id"],
                region["display_name"],
            ),
            "id": region["isca_id"],
        }
        for region in region_query_result
    }
    return list(json_terms.values())


def regions_to_bed(store, query, build):
    """Fetch matching regions and convert to BED format."""
    region_query_result = store.get_regions(build, query)
    bed_terms = [
        {
            "chrom": region["chromosome"],
            "start": region["start"],
            "end": region["end"],
            "name": "{} | {}".format(region["isca_id"], region["display_name"]),
        }
        for region in region_query_result
    ]
    return bed_terms
