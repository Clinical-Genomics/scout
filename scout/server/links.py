from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote

from flask import current_app

from scout.constants import SPIDEX_HUMAN
from scout.utils.convert import amino_acid_residue_change_3_to_1

SHALLOW_REFERENCE_STR_LOCI = ["ARX", "HOXA13"]
BEACON_LINK_TEMPLATE = (
    "https://beacon-network.org/#/search?pos={this[position]}&"
    "chrom={this[chromosome]}&allele={this[alternative]}&"
    "ref={this[reference]}&rs={build}"
)


def add_gene_links(
    gene_obj: Dict[str, Any], build: int = 37, institute: Optional[Dict[str, Any]] = None
):
    """Update a gene object with links

    Args:
        gene_obj (scout.models.variant.Gene)
        institute(scout.models.Institute)
    """
    try:
        build = int(build)
    except (ValueError, TypeError) as err:
        build = 37
    # Add links that use the hgnc_id
    hgnc_id = gene_obj["hgnc_id"]
    gene_obj["hgnc_link"] = genenames(hgnc_id)
    gene_obj["omim_link"] = omim(hgnc_id)
    # Add links that use ensembl_id
    ensembl_id = gene_obj.get("common", {}).get("ensembl_id")
    if not ensembl_id:
        ensembl_id = gene_obj.get("ensembl_id")

    hgnc_symbol = gene_obj.get("common", {}).get("hgnc_symbol")
    if not hgnc_symbol:
        hgnc_symbol = gene_obj.get("hgnc_symbol")

    gene_aliases = gene_obj.get("common", {}).get("aliases")
    if not gene_aliases:
        gene_aliases = gene_obj.get("aliases", [])

    ensembl_37_link = ensembl(ensembl_id, build=37)
    ensembl_38_link = ensembl(ensembl_id, build=38)
    gene_obj["ensembl_37_link"] = ensembl_37_link
    gene_obj["ensembl_38_link"] = ensembl_38_link
    gene_obj["ensembl_link"] = ensembl_37_link
    if build == 38:
        gene_obj["ensembl_link"] = ensembl_38_link
    gene_obj["hpa_link"] = hpa(ensembl_id)
    gene_obj["string_link"] = string(ensembl_id)
    gene_obj["reactome_link"] = reactome(ensembl_id)
    gene_obj["clingen_link"] = clingen(hgnc_id)
    gene_obj["gencc_link"] = gencc(hgnc_id)
    gene_obj["expression_atlas_link"] = expression_atlas(ensembl_id)
    gene_obj["exac_link"] = exac(ensembl_id)
    gene_obj["gnomad_link"] = gnomad(ensembl_id, build)
    # Add links that use entrez_id
    entrez_id = gene_obj.get("common", {}).get("entrez_id")
    gene_obj["entrez_link"] = entrez(entrez_id)
    gene_obj["pubmed_link"] = pubmed(hgnc_symbol, gene_aliases)
    gene_obj["ckb_link"] = ckb_gene(entrez_id)
    # Add links that use omim id
    gene_obj["omim_link"] = omim(gene_obj.get("omim_id"))
    # Add links that use hgnc_symbol
    gene_obj["ppaint_link"] = ppaint(hgnc_symbol)
    # Add links that use vega_id
    gene_obj["vega_link"] = vega(gene_obj.get("vega_id"))
    # Add links that use ucsc link
    gene_obj["ucsc_link"] = ucsc(gene_obj.get("ucsc_id"))
    gene_obj["genemania_link"] = genemania(hgnc_symbol)
    gene_obj["oncokb_link"] = oncokb(hgnc_symbol)
    gene_obj["cbioportal_link"] = cbioportal_gene(hgnc_symbol)
    gene_obj["civic_link"] = civic_gene(hgnc_symbol)
    gene_obj["iarctp53_link"] = iarctp53(hgnc_symbol)
    gene_obj["stripy_link"] = stripy_gene(hgnc_symbol)
    gene_obj["gnomad_str_link"] = gnomad_str_gene(hgnc_symbol)
    gene_obj["panelapp_link"] = panelapp_gene(hgnc_symbol)
    gene_obj["decipher_link"] = decipher_gene(hgnc_symbol)
    if institute:
        gene_obj["alamut_link"] = alamut_gene_link(institute, gene_obj, build)


def decipher_gene(hgnc_symbol: str) -> Optional[str]:
    """Create link to Decipher gene."""
    if hgnc_symbol:
        return f"https://www.deciphergenomics.org/gene/{hgnc_symbol}/overview/clinical-info"


def panelapp_gene(hgnc_symbol):
    link = "https://panelapp.genomicsengland.co.uk/panels/entities/{}"

    if not hgnc_symbol:
        return None
    return link.format(hgnc_symbol)


def stripy_gene(hgnc_symbol):
    link = "https://stripy.org/database/{}"

    if not hgnc_symbol:
        return None

    if hgnc_symbol in SHALLOW_REFERENCE_STR_LOCI:
        return "https://stripy.org/database"
    return link.format(hgnc_symbol)


def gnomad_str_gene(hgnc_symbol):
    link = "https://gnomad.broadinstitute.org/short-tandem-repeat/{}?dataset=gnomad_r4"

    if not hgnc_symbol:
        return None

    if hgnc_symbol in SHALLOW_REFERENCE_STR_LOCI:
        return "https://gnomad.broadinstitute.org/short-tandem-repeats?dataset=gnomad_r4"

    return link.format(hgnc_symbol)


def ckb_gene(entrez_id):
    link = "https://ckb.jax.org/gene/show?geneId={}"
    if not entrez_id:
        return None
    return link.format(entrez_id)


def civic_gene(hgnc_symbol):
    link = "https://civicdb.org/links/entrez_name/{}"

    if not hgnc_symbol:
        return None
    return link.format(hgnc_symbol)


def cbioportal_gene(hgnc_symbol):
    link = "https://www.cbioportal.org/ln?q={}%3AMUT"
    if not hgnc_symbol:
        return None
    return link.format(hgnc_symbol)


def oncokb(hgnc_symbol):
    link = "https://www.oncokb.org/gene/{}"
    if not hgnc_symbol:
        return None
    return link.format(hgnc_symbol)


def genemania(hgnc_symbol):
    link = "https://genemania.org/search/homo-sapiens/{}/"
    if not hgnc_symbol:
        return None
    return link.format(hgnc_symbol)


def genenames(hgnc_id):
    link = "https://www.genenames.org/cgi-bin/gene_symbol_report?hgnc_id=HGNC:{}"
    if not hgnc_id:
        return None
    return link.format(hgnc_id)


def omim(omim_id):
    link = "https://www.omim.org/entry/{}"
    if not omim_id:
        return None
    return link.format(omim_id)


def disease_link(disease_id: str) -> str:
    """Returns a link for disease depending on the source of the term"""
    source, disease_nr = disease_id.split(":")
    link = None
    if source == "OMIM":
        link = f"https://www.omim.org/entry/{disease_nr}"
    elif source == "ORPHA":
        link = f"https://www.orpha.net/consor/cgi-bin/OC_Exp.php?lng=en&Expert={disease_nr}"

    return link


def ensembl(ensembl_id, build=37):
    link = "http://grch37.ensembl.org/Homo_sapiens/Gene/Summary?db=core;g={}"
    if build == 38:
        link = "http://ensembl.org/Homo_sapiens/Gene/Summary?db=core;g={}"
    if not ensembl_id:
        return None

    return link.format(ensembl_id)


def exac(ensembl_id):
    link = "https://gnomad.broadinstitute.org/gene/{}?dataset=exac"
    if not ensembl_id:
        return None

    return link.format(ensembl_id)


def gnomad(ensembl_id, build=37):
    if not ensembl_id:
        return None

    link = "https://gnomad.broadinstitute.org/gene/{}?dataset="
    if build == 37:
        link += "gnomad_r2_1"
    if build == 38:
        link += "gnomad_r4"

    return link.format(ensembl_id)


def hpa(ensembl_id):
    link = "http://www.proteinatlas.org/search/{}"

    if not ensembl_id:
        return None

    return link.format(ensembl_id)


def string(ensembl_id):
    link = "http://string-db.org/newstring_cgi/show_network_" "section.pl?identifier={}"

    if not ensembl_id:
        return None

    return link.format(ensembl_id)


def reactome(ensembl_id):
    link = (
        "http://www.reactome.org/content/query?q={}&species=Homo+sapiens"
        "&species=Entries+without+species&cluster=true"
    )
    if not ensembl_id:
        return None

    return link.format(ensembl_id)


def clingen(hgnc_id):
    link = "https://search.clinicalgenome.org/kb/genes/HGNC:{}"
    if not hgnc_id:
        return None
    return link.format(hgnc_id)


def gencc(hgnc_id):
    link = "https://search.thegencc.org/genes/HGNC:{}"
    if not hgnc_id:
        return None
    return link.format(hgnc_id)


def expression_atlas(ensembl_id):
    link = "https://www.ebi.ac.uk/gxa/genes/{}"
    if not ensembl_id:
        return None

    return link.format(ensembl_id)


def entrez(entrez_id):
    link = "https://www.ncbi.nlm.nih.gov/gene/{}"

    if not entrez_id:
        return None

    return link.format(entrez_id)


def pubmed(hgnc_symbol: str, gene_aliases: List[str]) -> str:
    if not len(gene_aliases):
        link = "https://pubmed.ncbi.nlm.nih.gov/?term={}"
        return link.format(hgnc_symbol)

    link = "https://pubmed.ncbi.nlm.nih.gov/?term=" + hgnc_symbol
    for alias in gene_aliases:
        link += "+OR+" + alias
    return link


def ppaint(hgnc_symbol):
    link = "https://pecan.stjude.cloud/variants/proteinpaint?gene={}"
    if not hgnc_symbol:
        return None

    return link.format(hgnc_symbol)


def vega(vega_id):
    link = (
        "http://vega.archive.ensembl.org/Homo_sapiens/Gene/Summary?db=core;g=OTTHUMG00000018506{}"
    )

    if not vega_id:
        return None

    return link.format(vega_id)


def ucsc(ucsc_id):
    link = (
        "http://genome.cse.ucsc.edu/cgi-bin/hgGene?org=Human&hgg_chrom=none&hgg_type=knownGene"
        "&hgg_gene={}"
    )

    if not ucsc_id:
        return None

    return link.format(ucsc_id)


def add_tx_links(tx_obj, build=37, hgnc_symbol=None):
    try:
        build = int(build)
    except ValueError:
        build = 37

    ensembl_id = tx_obj.get("ensembl_transcript_id", tx_obj.get("transcript_id"))
    ensembl_37_link = ensembl_tx(ensembl_id, 37)
    ensembl_38_link = ensembl_tx(ensembl_id, 38)

    tx_obj["ensembl_37_link"] = ensembl_37_link
    tx_obj["ensembl_38_link"] = ensembl_38_link
    tx_obj["ensembl_link"] = ensembl_37_link
    if build == 38:
        tx_obj["ensembl_link"] = ensembl_38_link

    refseq_links = []
    if tx_obj.get("refseq_id"):
        refseq_id = tx_obj["refseq_id"]
        refseq_links.append({"link": refseq(refseq_id), "id": refseq_id})
    tx_obj["refseq_links"] = refseq_links
    tx_obj["swiss_prot_link"] = swiss_prot(tx_obj.get("swiss_prot"))
    tx_obj["pfam_domain_link"] = pfam(tx_obj.get("pfam_domain"))
    tx_obj["prosite_profile_link"] = prosite(tx_obj.get("prosite_profile"))
    tx_obj["smart_domain_link"] = smart(tx_obj.get("smart_domain"))
    tx_obj["varsome_link"] = varsome(
        build, tx_obj.get("refseq_id"), tx_obj.get("coding_sequence_name")
    )
    tx_obj["mutalyzer_link"] = mutalyzer(
        tx_obj.get("refseq_id"), tx_obj.get("coding_sequence_name")
    )
    tx_obj["tp53_link"] = mutantp53(tx_obj.get("hgnc_id"), tx_obj.get("protein_sequence_name"))
    tx_obj["cbioportal_link"] = cbioportal(hgnc_symbol, tx_obj.get("protein_sequence_name"))
    tx_obj["mycancergenome_link"] = mycancergenome(hgnc_symbol, tx_obj.get("protein_sequence_name"))

    return tx_obj


##  Transcript links
def refseq(refseq_id):
    link = "http://www.ncbi.nlm.nih.gov/nuccore/{}"
    if not refseq_id:
        return None

    return link.format(refseq_id)


def ensembl_tx(ens_tx_id, build=37):
    link = "http://grch37.ensembl.org/Homo_sapiens/" "Gene/Summary?t={}"

    if build == 38:
        link = "http://ensembl.org/Homo_sapiens/" "Gene/Summary?t={}"
    if not ens_tx_id:
        return None

    return link.format(ens_tx_id)


def swiss_prot(swiss_prot_id):
    link = "http://www.uniprot.org/uniprot/{}"

    if not swiss_prot_id:
        return None

    return link.format(swiss_prot_id)


def pfam(pfam_domain):
    link = "http://pfam.xfam.org/family/{}"

    if not pfam_domain:
        return None

    return link.format(pfam_domain)


def prosite(prosat_profile):
    link = "http://prosite.expasy.org/cgi-bin/prosite/" "prosite-search-ac?{}"
    if not prosat_profile:
        return None

    return link.format(prosat_profile)


def smart(smart_domain):
    link = "http://smart.embl.de/smart/search.cgi?keywords={}"

    if not smart_domain:
        return None

    return link.format(smart_domain)


def varsome(build: int, refseq_id: str, protein_sequence_name: str):
    """Return a string corresponding to a link to varsome page

    Args:
        build(int): chromosome build
        refseq_id(str): transcript refseq id
        protein_sequence_name(str): transcript sequence name

    """

    if not all([refseq_id, protein_sequence_name]):
        return None

    if build == 37:
        build = 19

    link = "https://varsome.com/variant/hg{}/{}:{}"

    return link.format(build, refseq_id, protein_sequence_name)


def mutalyzer(refseq_id, hgvs):
    """Return a string corresponding to a link to the Normalizer tool of Mutalyzer

    Args:
        refseq_id(str): transcript refseq id
        hgvs(str): hgvs
    """
    if not all([refseq_id, hgvs]):
        return None

    link = "https://mutalyzer.nl/normalizer/{}:{}"
    return link.format(refseq_id, hgvs)


def iarctp53(hgnc_symbol):
    if hgnc_symbol != "TP53":
        return None

    link = "https://tp53.isb-cgc.org/"

    return link


############# Variant links ####################


def get_variant_links(institute_obj: dict, variant_obj: dict, build: int = None):
    """Return links for a variant object

    Args:
        variant_obj(scout.models.Variant)
        build(int)

    Returns:
        links(dict): The variant links
    """
    try:
        build = int(build)
    except (ValueError, TypeError) as err:
        build = 37

    links = dict(
        thousandg_link=thousandg_link(variant_obj, build),
        exac_link=exac_link(variant_obj),
        gnomad_link=gnomad_link(variant_obj, build),
        gnomad_sv_link=gnomad_sv_link(variant_obj, build),
        swegen_link=swegen_link(variant_obj),
        cosmic_links=cosmic_links(variant_obj),
        beacon_link=beacon_link(variant_obj, build),
        ucsc_link=ucsc_link(variant_obj, build),
        decipher_link=decipher_link(variant_obj, build),
        ensembl_link=ensembl_link(variant_obj, build),
        mitomap_link=mitomap_link(variant_obj),
        hmtvar_link=hmtvar_link(variant_obj),
        spidex_human=spidex_human(variant_obj),
        spliceai_link=spliceai_link(variant_obj, build),
        str_source_link=str_source_link(variant_obj),
        snp_links=snp_links(variant_obj),
        alamut_link=alamut_variant_link(institute_obj, variant_obj, build),
    )
    return links


def str_source_link(variant_obj):
    """Compose link for STR data source."""

    if not variant_obj.get("str_source"):
        return None

    source = variant_obj["str_source"]

    if source["id"] is None:
        return None

    url_template = "{}"
    if source["type"] == "GeneReviews":
        url_template = "https://www.ncbi.nlm.nih.gov/books/{}/"
    if source["type"] == "PubMed":
        url_template = "https://pubmed.ncbi.nlm.nih.gov/{}/"

    return url_template.format(source["id"])


def thousandg_link(variant_obj, build=None):
    """Compose link to 1000G page for detailed information."""
    dbsnp_id = variant_obj.get("dbsnp_id")
    build = build or 37

    if not dbsnp_id:
        return None

    if build == 37:
        url_template = (
            "http://grch37.ensembl.org/Homo_sapiens/Variation/Explore" "?v={};vdb=variation"
        )
    else:
        url_template = "http://www.ensembl.org/Homo_sapiens/Variation/Explore" "?v={};vdb=variation"

    return url_template.format(dbsnp_id)


def ensembl_link(variant_obj, build=37):
    """Compose (sv) variant link to ensembl"""

    my_end = variant_obj["end"]
    if variant_obj["chromosome"] != variant_obj.get("end_chrom", variant_obj["chromosome"]):
        my_end = variant_obj["position"]

    if build == 37:
        url_template = "http://grch37.ensembl.org/Homo_sapiens/Location/View?db=core;r={this[chromosome]}:{this[position]}-{my_end}"
    else:
        url_template = "http://www.ensembl.org/Homo_sapiens/Location/View?db=core;r={this[chromosome]}:{this[position]}-{my_end}"
    return url_template.format(this=variant_obj, my_end=my_end)


def decipher_link(variant_obj, build=37):
    """Compose DECIPHER SV variant links"""

    my_end = variant_obj["end"]
    if variant_obj["chromosome"] != variant_obj.get("end_chrom", variant_obj["chromosome"]):
        my_end = variant_obj["position"]

    if build == 37:
        url_template = "https://www.deciphergenomics.org/search/patients/browser?q=grch37:{this[chromosome]}:{this[position]}-{my_end}"
    else:
        url_template = "https://www.deciphergenomics.org/browser#q/{this[chromosome]}:{this[position]}-{this[end]}/location/{this[chromosome]}:{this[position]}-{my_end}"
    return url_template.format(this=variant_obj, my_end=my_end)


def exac_link(variant_obj):
    """Compose link to ExAC website for a variant position."""
    url_template = (
        "https://exac.broadinstitute.org/variant/"
        "{this[chromosome]}-{this[position]}-{this[reference]}"
        "-{this[alternative]}"
    )
    return url_template.format(this=variant_obj)


def gnomad_link(variant_obj, build=37):
    """Compose link to gnomAD website for a variant."""
    url_template = (
        "https://gnomad.broadinstitute.org/variant/{this[chromosome]}-"
        "{this[position]}-{this[reference]}-{this[alternative]}"
    ).format(this=variant_obj)

    if build == 37:
        url_template += "?dataset=gnomad_r2_1"
        return url_template

    if build == 38 or variant_obj["chromosome"] in ["M", "MT"]:
        url_template += "?dataset=gnomad_r4"

    return url_template


def spliceai_link(variant_obj, build=37):
    """Compopse a link to BROADs SpliceAI Lookup for a somewhat live view of SpliceAI and Pangolin scores."""
    url_template = (
        "https://spliceailookup.broadinstitute.org/#variant={this[chromosome]}-"
        "{this[position]}-{this[reference]}-{this[alternative]}&hg={build}&distance=500&mask=1"
    ).format(this=variant_obj, build=build)

    return url_template


def gnomad_sv_link(variant_obj, build=37):
    """Compose link to gnomAD website for a structural variant.

    Since we do not track the GnomAD variant ID we link to the region view instead.
    For balanced variants, we pick the region for the start position (the var is available in both).

    MT SVs are not available for 38 yet.
    """

    url_template = (
        "https://gnomad.broadinstitute.org/region/{this[chromosome]}-{this[position]}"
    ).format(this=variant_obj)

    if variant_obj["chromosome"] == variant_obj.get("end_chrom"):
        url_template += f"-{variant_obj['end']}"
    else:
        url_template += f"-{variant_obj['position']}"

    if build == 37:
        url_template += "?dataset=gnomad_sv_r2_1"
        return url_template

    url_template += "?dataset=gnomad_sv_r4"

    return url_template


def swegen_link(variant_obj):
    """Compose link to SweGen Variant Frequency Database."""
    url_template = (
        "https://swegen-exac.nbis.se/variant/{this[chromosome]}-"
        "{this[position]}-{this[reference]}-{this[alternative]}"
    )
    return url_template.format(this=variant_obj)


def cosmic_links(variant_obj):
    """Compose link to COSMIC Database.

    Args:
        variant_obj(scout.models.Variant)

    Returns:
        cosmic_links(list): a list of tuples : [(id1, link1), (id2, link2), ..]
    """
    cosmic_ids = variant_obj.get("cosmic_ids")
    if not cosmic_ids:
        return None

    cosmic_links = []

    for c_id in cosmic_ids:
        cosmic_id = str(c_id)
        if cosmic_id.startswith("COS"):
            url_template = "https://cancer.sanger.ac.uk/cosmic/search?q={}"
        else:
            url_template = "https://cancer.sanger.ac.uk/cosmic/mutation/overview?id={}"
        cosmic_links.append((cosmic_id, url_template.format(cosmic_id)))

    return cosmic_links


def beacon_link(variant_obj: dict, build: int):
    """Compose link to Beacon Network."""
    url_template = BEACON_LINK_TEMPLATE

    build = "GRCh38" if build == 38 else "GRCh37"

    return url_template.format(this=variant_obj, build=build)


def snp_links(variant_obj):
    """Compose links to dbSNP and ClinVar variation"""

    if variant_obj.get("dbsnp_id") is None:
        return
    snp_links = {}
    snp_ids = variant_obj["dbsnp_id"].split(";")
    for snp in snp_ids:
        if "rs" in snp:
            snp_links[snp] = f"https://www.ncbi.nlm.nih.gov/snp/{snp}"  # dbSNP
        elif snp.isnumeric():
            snp_links[
                snp
            ] = f"https://www.ncbi.nlm.nih.gov/clinvar/variation/{snp}"  # ClinVar variation

    return snp_links


def ucsc_link(variant_obj, build=None):
    """Compose link to UCSC."""
    build = build or 37
    url_template = (
        "http://genome.ucsc.edu/cgi-bin/hgTracks?db=hg19&"
        "position=chr{this[chromosome]}:{this[position]}"
        "-{this[position]}&dgv=pack&knownGene=pack&omimGene=pack"
    )
    if build == 38:
        url_template = (
            "http://genome.ucsc.edu/cgi-bin/hgTracks?db=hg20&"
            "position=chr{this[chromosome]}:{this[position]}"
            "-{this[position]}&dgv=pack&knownGene=pack&omimGene=pack"
        )

    return url_template.format(this=variant_obj)


def mycancergenome(hgnc_symbol, protein_sequence_name):
    """Compose link to variant in mycancergenome"""
    link = "https://www.mycancergenome.org/content/alteration/{}-{}"

    if not hgnc_symbol:
        return None
    if not protein_sequence_name:
        return None

    protein_change = amino_acid_residue_change_3_to_1(protein_sequence_name)

    if not protein_change:
        return None

    return link.format(hgnc_symbol, protein_change.lower())


def cbioportal(hgnc_symbol, protein_sequence_name):
    """Compose link to variant in cbioportal"""
    link = "https://www.cbioportal.org/ln?q={}:MUT%20%3D{}"

    if not hgnc_symbol:
        return None
    if not protein_sequence_name:
        return None

    protein_change = amino_acid_residue_change_3_to_1(protein_sequence_name)

    if not protein_change:
        return None

    return link.format(hgnc_symbol, protein_change)


def mutantp53(hgnc_id, protein_variant):
    """Compose link to variant in mutantp53"""
    if hgnc_id != 11998:
        return None
    if not protein_variant or protein_variant.endswith("=") or protein_variant.endswith("%3D"):
        return None

    url_template = "http://mutantp53.broadinstitute.org/?query={}"

    return url_template.format(protein_variant)


def alamut_variant_link(
    institute_obj: Dict[str, Any],
    variant_obj: Dict[str, Any],
    build: Optional[int] = None,
) -> str:
    """Compose a link which open up variants in the Alamut software
    Alamut links require some settings from the institute object.
    This link is rendered on the variant side. Alamut has issues with GATK style genome coordinates for indels, but
    it can sometimes be good to be able to link to a given genome coordinate, e.g. for non coding variantion.

    We use variant coordinates, effectively making a build dependent g. string.

    Args:
        institute_obj(scout.models.Institute)
        variant_obj(scout.models.Variant):

    Returns:
        url_template(str): link to Alamut browser
    """

    if current_app.config.get("HIDE_ALAMUT_LINK"):
        return False

    if not institute_obj:
        return

    (search_verb, alamut_key_arg, alamut_inst_arg) = _get_alamut_config(institute_obj)

    url_template = (
        "http://localhost:10000/{search_verb}?{alamut_key_arg}{alamut_inst_arg}request={chromosome}{build_str}:"
        "{this[position]}{this[reference]}>{this[alternative]}"
    )
    chromosome = variant_obj.get("chromosome")

    build = build or 37
    build_str = ""
    if build == 38:
        build_str = "(GRCh38)"
        chromosome = chromosome.replace("M", "MT")

    return url_template.format(
        search_verb=search_verb,
        alamut_key_arg=alamut_key_arg,
        alamut_inst_arg=alamut_inst_arg,
        chromosome=chromosome,
        this=variant_obj,
        build_str=build_str,
    )


def alamut_gene_link(
    institute_obj: Dict[str, Any],
    gene_obj: Dict[str, Any],
    build: Optional[int] = None,
):
    """Compose a link which open up variants in the Alamut software.
    Alamut links require some settings from the institute object.
    The link is rendered on the gene side as Alamut has issues with GATK style genome coordinates for indels.

    We utilise the "canonical" transcript for each gene, as well as the HGVS c. string.

    Args:
        institute_obj(scout.models.Institute)
        variant_obj(scout.models.Variant):

    Returns:
        url_template(str): link to Alamut browser
    """

    if current_app.config.get("HIDE_ALAMUT_LINK"):
        return False

    if not institute_obj:
        return False

    (search_verb, alamut_key_arg, alamut_inst_arg) = _get_alamut_config(institute_obj)

    url_template = (
        "http://localhost:10000/{search_verb}?{alamut_key_arg}{alamut_inst_arg}request={this[canonical_transcript]}{build_str}:"
        "{hgvs_identifier}"
    )

    build = build or 37
    build_str = ""
    if build == 38:
        build_str = "(GRCh38)"

    hgvs_raw = gene_obj.get("hgvs_identifier")
    if not hgvs_raw:
        return False

    return url_template.format(
        search_verb=search_verb,
        alamut_key_arg=alamut_key_arg,
        alamut_inst_arg=alamut_inst_arg,
        this=gene_obj,
        build_str=build_str,
        hgvs_identifier=quote(hgvs_raw),
    )


def _get_alamut_config(institute_obj: dict) -> Tuple[str, ...]:
    """
    Prepare Alamut connection string specifics from institute level configuration.

    Args:
        institute_obj:   scout.models.Institute
    """

    alamut_key = institute_obj.get("alamut_key")
    search_verb = "search" if alamut_key else "show"
    alamut_key_arg = f"apikey={alamut_key}&" if alamut_key else ""

    alamut_institution = institute_obj.get("alamut_institution")
    alamut_inst_arg = f"institution={alamut_institution}&" if alamut_institution else ""

    return (search_verb, alamut_key_arg, alamut_inst_arg)


def mitomap_link(variant_obj):
    """Compose a link to a variant in mitomap"""
    url_template = "https://mitomap.org/cgi-bin/search_allele?variant={this[position]}{this[reference]}%3E{this[alternative]}"
    return url_template.format(this=variant_obj)


def hmtvar_link(variant_obj):
    """Compose a link to a variant in HmtVar"""
    url_template = "https://www.hmtvar.uniba.it/varCard/{id}"
    return url_template.format(id=variant_obj.get("hmtvar_variant_id"))


def spidex_human(variant_obj):
    """Translate SPIDEX annotation to human readable string."""
    if variant_obj.get("spidex") is None:
        return "not_reported"
    if abs(variant_obj["spidex"]) < SPIDEX_HUMAN["low"]["pos"][1]:
        return "low"
    if abs(variant_obj["spidex"]) < SPIDEX_HUMAN["medium"]["pos"][1]:
        return "medium"

    return "high"


def external_primer_order_link(variant_obj, build=None):
    """Compose link for primers orders based on the configuration paramaters EXTERNAL_PRIMER_ORDER_LINK_(37|38)"""
    build = build or 37

    url_template = ""

    if build == 38:
        url_template = current_app.config.get("EXTERNAL_PRIMER_ORDER_LINK_38", "")
    elif build == 37:
        url_template = current_app.config.get("EXTERNAL_PRIMER_ORDER_LINK_37", "")

    return url_template.format(
        chromosome=variant_obj.get("chromosome"), position=variant_obj.get("position")
    )
