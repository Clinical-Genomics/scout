from scout.parse.variant.gene import parse_genes
from scout.parse.variant.transcript import parse_transcripts


def test_get_genes():
    csq_entry = (
        "C|missense_variant|MODERATE|POC1A|ENSG00000164087|"
        "Transcript|ENST00000296484|protein_coding|4/11||ENST00000296484.2"
        ":c.322A>G|ENSP00000296484.2:p.Ser108Gly|362|322|108|S/G|Agt/Ggt"
        "|||-1|HGNC|24488||CCDS2846.1|ENSP00000296484|POC1A_HUMAN|"
        "B2RDV4_HUMAN|UPI000045711C|deleterious|possibly_damaging|"
        "PROSITE_profiles:PS50082&PROSITE_profiles:PS50294&hmmpanther"
        ":PTHR22847:SF319&hmmpanther:PTHR22847&Gene3D:2.130.10.10&"
        "Pfam_domain:PF00400&SMART_domains:SM00320&Superfamily_domains:"
        "SSF50978|||||,C|missense_variant|MODERATE|POC1A|ENSG00000164087"
        "|Transcript|ENST00000394970|protein_coding|4/10||"
        "ENST00000394970.2:c.322A>G|ENSP00000378421.2:p.Ser108Gly|640"
        "|322|108|S/G|Agt/Ggt|||-1|HGNC|24488||CCDS54592.1|ENSP00000378421"
        "|POC1A_HUMAN||UPI00006633C6|deleterious|benign|"
        "Superfamily_domains:SSF50978&SMART_domains:SM00320&Pfam_domain"
        ":PF00400&Gene3D:2.130.10.10&hmmpanther:PTHR22847&hmmpanther:"
        "PTHR22847:SF319&PROSITE_profiles:PS50082&PROSITE_profiles:PS50294"
        "|||||,C|missense_variant|MODERATE|POC1A|ENSG00000164087|"
        "Transcript|ENST00000474012|protein_coding|4/11||ENST00000474012"
        ".1:c.208A>G|ENSP00000418968.1:p.Ser70Gly|425|208|70|S/G|Agt"
        "/Ggt|||-1|HGNC|24488||CCDS54591.1|ENSP00000418968|POC1A_HUMAN|"
        "B2RDV4_HUMAN|UPI0000E1FCF5|tolerated|possibly_damaging|Superfami"
        "ly_domains:SSF50978&SMART_domains:SM00320&Gene3D:2.130.10.10&"
        "Pfam_domain:PF00400&hmmpanther:PTHR22847:SF319&hmmpanther:"
        "PTHR22847&PROSITE_profiles:PS50294&PROSITE_profiles:PS50082|||||"
    )

    csq_header = (
        "Allele|Consequence|IMPACT|SYMBOL|Gene|Feature_type|"
        "Feature|BIOTYPE|EXON|INTRON|HGVSc|HGVSp|cDNA_position|CDS_position|"
        "Protein_position|Amino_acids|Codons|Existing_variation|DISTANCE|"
        "STRAND|SYMBOL_SOURCE|HGNC_ID|TSL|CCDS|ENSP|SWISSPROT|TREMBL|UNIPARC|"
        "SIFT|PolyPhen|DOMAINS|HGVS_OFFSET|MOTIF_NAME|MOTIF_POS|HIGH_INF_POS|"
        "MOTIF_SCORE_CHANGE"
    )

    header = [word.upper() for word in csq_header.split("|")]

    ## GIVEN a variant with vep annotation and a vep header
    raw_transcripts = (
        dict(zip(header, csq_entry.split("|"))) for transcript_info in csq_entry.split(",")
    )
    parsed_transcripts = []
    for parsed_transcript in parse_transcripts(raw_transcripts):
        parsed_transcripts.append(parsed_transcript)

    # variant = cyvcf2_variant
    # variant.INFO['CSQ'] = csq_entry
    genes = parse_genes(parsed_transcripts)

    for gene in genes:
        assert gene["hgnc_id"] == 24488
    assert len(genes) == 1
