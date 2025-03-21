# -*- coding: utf-8 -*-
import uuid

import pytest
from flask_login import login_user
from werkzeug.datastructures import ImmutableMultiDict

from scout.server.app import create_app
from scout.server.blueprints.login.models import LoginUser


class MockMail:
    _send_was_called = False
    _message = None

    def send(self, message):
        self._send_was_called = True
        self._message = message


@pytest.fixture
def mock_mail():
    return MockMail()


@pytest.fixture
def mock_sender():
    return "mock_sender"


@pytest.fixture
def mock_comment():
    return "mock_comment"


@pytest.fixture
def loqusdburl():
    """Return the base url of a loqusdb mock"""
    return "http://127.0.0.1:9000"


@pytest.fixture
def loqusdb():
    """Return a loqusdb mock"""
    loqus_mock = LoqusdbMock()
    return loqus_mock


@pytest.fixture
def app(real_database_name, real_variant_database, user_obj, loqusdburl):
    """A test app containing the endpoints of the real app"""

    app = create_app(
        config=dict(
            TESTING=True,
            DEBUG=True,
            MONGO_DBNAME=real_database_name,
            DEBUG_TB_ENABLED=False,
            LOGIN_DISABLED=True,
            WTF_CSRF_ENABLED=False,
            MME_URL="test_matchmaker.com",
            MME_ACCEPTS="application/vnd.ga4gh.matchmaker.v1.0+json",
            MME_TOKEN=str(uuid.uuid4()),
            BEACON_URL="http://localhost:6000/apiv1.0",
            BEACON_TOKEN="DEMO",
            LOQUSDB_SETTINGS={
                "test": {
                    "api_url": loqusdburl,
                    "instance_type": "api",
                    "id": "loqusRD",
                    "version": "2.5",
                }
            },
        )
    )

    @app.route("/auto_login")
    def auto_login():
        user_inst = LoginUser(user_obj)
        assert login_user(user_inst, remember=True)
        return "ok"

    @app.route("/auto_login_not_authorized")
    def auto_login_not_authorized():
        user_obj["roles"] = []
        user_obj["institutes"] = []
        user_inst = LoginUser(user_obj)
        assert login_user(user_inst, remember=True)
        return "ok"

    return app


@pytest.fixture
def rerunner_app(user_obj):
    _mock_app = create_app(
        config=dict(
            TESTING=True,
            LOGIN_DISABLED=True,
            SERVER_NAME="test",
            RERUNNER_API_ENTRYPOINT="http://rerunner:5001/v1.0/rerun",
            RERUNNER_API_KEY="test_key",
            REMEMBER_COOKIE_NAME="remember_me",
            SESSION_TIMEOUT_MINUTES=10,
        )
    )

    return _mock_app


@pytest.fixture
def institute_info():
    _institute_info = dict(internal_id="cust000", display_name="test_institute")
    return _institute_info


@pytest.fixture
def user_info(institute_info):
    _user_info = dict(
        email="john@doe.com",
        name="John Doe",
        roles=["admin", "mme_submitter"],
        institutes=[institute_info["internal_id"]],
    )
    return _user_info


@pytest.fixture
def hpo_checkboxes():
    """Returns a list of dictionaries representing HPO checkboxes"""
    checkbox1 = {
        "_id": "HP:0025190",
        "hpo_id": "HP:0025190",
        "description": "Bilateral tonic-clonic seizure with generalized onset",
        "children": ["HP:0032661"],
        "ancestors": [],
    }
    checkbox2 = {
        "_id": "HP:0032661",
        "hpo_id": "HP:0032661",
        "description": "Generalized convulsive status epilepticus",
        "children": [],
        "ancestors": ["HP:0025190"],
    }
    return [checkbox1, checkbox2]


@pytest.fixture
def omim_checkbox():
    """Returns a dictionaries representing an OMIM checkboxe"""
    checkbox = {
        "_id": "OMIM:121210",
        "description": "Febrile seizures familial 1",
    }
    return checkbox


@pytest.fixture
def variant_gene_updated_info():
    """Returns a dictionary with the information from variant gene with updated info, ready to be visualized on the portal"""
    updated_variant_gene = {
        "hgnc_id": 30213,
        "hgnc_symbol": "ATP13A2",
        "ensembl_id": "ENSG00000159363",
        "description": "ATPase cation transporting 13A2",
        "inheritance": ["AR"],
        "transcripts": [
            {  # Transcript with refseq_id (and primary)
                "transcript_id": "ENST00000452699",
                "hgnc_id": 30213,
                "protein_id": "ENSP00000413307",
                "sift_prediction": "deleterious",
                "polyphen_prediction": "probably_damaging",
                "swiss_prot": "Q9NQ11",
                "biotype": "protein_coding",
                "functional_annotations": ["missense_variant"],
                "region_annotations": ["exonic"],
                "exon": "26/29",
                "strand": "-",
                "coding_sequence_name": "c.2963C>T",
                "protein_sequence_name": "p.Pro988Leu",
                "is_canonical": False,
                "is_primary": True,
                "refseq_id": "NM_022089",
                "refseq_identifiers": ["NM_022089", "NM_001141973"],
                "ensembl_37_link": "http://grch37.ensembl.org/Homo_sapiens/Gene/Summary?t=ENST00000452699",
                "ensembl_38_link": "http://ensembl.org/Homo_sapiens/Gene/Summary?t=ENST00000452699",
                "ensembl_link": "http://grch37.ensembl.org/Homo_sapiens/Gene/Summary?t=ENST00000452699",
                "refseq_links": [
                    {
                        "link": "http://www.ncbi.nlm.nih.gov/nuccore/NM_022089",
                        "id": "NM_022089",
                    }
                ],
                "swiss_prot_link": "http://www.uniprot.org/uniprot/Q9NQ11",
                "pfam_domain_link": None,
                "prosite_profile_link": None,
                "smart_domain_link": None,
                "varsome_link": "https://varsome.com/variant/hg37/NM_022089:c.2963C>T",
                "tp53_link": None,
                "cbioportal_link": "https://www.cbioportal.org/ln?q=ATP13A2:MUT%20%3DP988L",
                "mycancergenome_link": "https://www.mycancergenome.org/content/alteration/ATP13A2-p988l",
                "change_str": "ATP13A2:NM_022089:exon26:c.2963C>T:p.Pro988Leu",
            },
            {  # Transcript with NO refseq_id, no primary, no canonical
                "transcript_id": "NM_001141974.3",
                "hgnc_id": 30213,
                "protein_id": "NP_001135446.1",
                "sift_prediction": "tolerated",
                "polyphen_prediction": "possibly_damaging",
                "swiss_prot": "unknown",
                "biotype": "protein_coding",
                "functional_annotations": ["missense_variant"],
                "region_annotations": ["exonic"],
                "exon": "25/27",
                "strand": "-",
                "coding_sequence_name": "c.2846C>T",
                "protein_sequence_name": "p.Pro949Leu",
                "is_canonical": False,
            },
            {  # Transcript with NO refseq_id, no primary, but canonical
                "transcript_id": "NM_022089.4",
                "hgnc_id": 30213,
                "protein_id": "NP_071372.1",
                "sift_prediction": "deleterious",
                "polyphen_prediction": "possibly_damaging",
                "swiss_prot": "unknown",
                "biotype": "protein_coding",
                "functional_annotations": ["missense_variant"],
                "region_annotations": ["exonic"],
                "exon": "26/29",
                "strand": "-",
                "coding_sequence_name": "c.2978C>T",
                "protein_sequence_name": "p.Pro993Leu",
                "is_canonical": True,
            },
        ],
        "functional_annotation": "missense_variant",
        "region_annotation": "exonic",
        "sift_prediction": "deleterious",
        "polyphen_prediction": "possibly_damaging",
        "hgvs_identifier": "c.2978C>T",
        "canonical_transcript": "NM_022089.4",
        "exon": "26/29",
        "disease_associated_transcripts": [],
        "manual_penetrance": False,
        "mosaicism": False,
        "manual_inheritance": [],
        "common": {
            "primary_transcripts": ["NM_022089"],
        },
    }
    return updated_variant_gene


@pytest.fixture
def variant_gene():
    """Returns a dictionary with the information from a variant gene"""
    gene = {
        "hgnc_id": 30213,
        "hgnc_symbol": "ATP13A2",
        "ensembl_id": "ENSG00000159363",
        "description": "ATPase cation transporting 13A2",
        "transcripts": [
            {
                "transcript_id": "ENST00000452699",
                "hgnc_id": 30213,
                "protein_id": "ENSP00000413307",
                "sift_prediction": "deleterious",
                "polyphen_prediction": "probably_damaging",
                "swiss_prot": "Q9NQ11",
                "biotype": "protein_coding",
                "functional_annotations": ["missense_variant"],
                "region_annotations": ["exonic"],
                "exon": "26/29",
                "strand": "-",
                "coding_sequence_name": "c.2963C>T",
                "protein_sequence_name": "p.Pro988Leu",
                "is_canonical": False,
            },
        ],
        "disease_associated_no_version": set(),
    }
    return gene


@pytest.fixture
def hgnc_gene():
    """docstring for hgnc_gene"""
    gene = {
        "_id": {"$oid": "5fe1dc0ea7dc6a0f011139b1"},
        "hgnc_id": 30213,
        "hgnc_symbol": "ATP13A2",
        "ensembl_id": "ENSG00000159363",
        "chromosome": "1",
        "start": 17312453,
        "end": 17338423,
        "length": 25970,
        "description": "ATPase cation transporting 13A2",
        "aliases": ["CLN12", "PARK9", "ATP13A2", "HSA9947"],
        "primary_transcripts": ["NM_022089"],
        "inheritance_models": ["AR"],
        "entrez_id": 23400,
        "omim_id": 610513,
        "ucsc_id": "uc001baa.3",
        "uniprot_ids": ["Q9NQ11"],
        "vega_id": "OTTHUMG00000002293",
        "pli_score": 0.00120495054739301,
        "incomplete_penetrance": False,
        "build": "37",
        "transcripts": [
            {
                "_id": {"$oid": "5fe1dc3ea7dc6a0f0111e103"},
                "ensembl_transcript_id": "ENST00000452699",
                "hgnc_id": 30213,
                "chrom": "1",
                "start": 17312453,
                "end": 17338423,
                "is_primary": True,
                "refseq_id": "NM_022089",
                "refseq_identifiers": ["NM_022089", "NM_001141973"],
                "build": "37",
                "length": 25970,
            }
        ],
    }
    return gene


@pytest.fixture
def sv_var_obj():
    sv_var = {
        "_id": "19ecad237722da35ec5ed01ecc9f0c3b",
        "length": 1,
        "mate_id": null,
        "document_id": "19ecad237722da35ec5ed01ecc9f0c3b",
        "end_chrom": "1",
        "variant_id": "9657183743c80ef8552ef7725c0f4bef",
        "freebayes": "Pass",
        "reference": "A",
        "category": "snv",
        "spidex": 1.7039999961853027,
        "institute": "cust003",
        "dbsnp_id": "rs147223770",
        "hgnc_ids": [7882],
        "end": 120478125,
        "compounds": [
            {
                "display_name": "1_120602372_A_G",
                "not_loaded": false,
                "variant": "cd6c106e6010a97d20dce3265a7b527a",
                "genes": [
                    {
                        "functional_annotation": "non_coding_transcript_variant",
                        "hgnc_id": 7882,
                        "region_annotation": "ncRNA_exonic",
                        "hgnc_symbol": "NOTCH2",
                    }
                ],
                "combined_score": 25,
                "rank_score": 9,
            },
            {
                "display_name": "1_120576878_C_A",
                "not_loaded": false,
                "variant": "d334f56b68089c490a130f6707d05a52",
                "genes": [
                    {
                        "functional_annotation": "non_coding_transcript_variant",
                        "hgnc_id": 7882,
                        "region_annotation": "ncRNA_exonic",
                        "hgnc_symbol": "NOTCH2",
                    }
                ],
                "combined_score": 24,
                "rank_score": 8,
            },
            {
                "display_name": "1_120464481_T_C",
                "not_loaded": false,
                "variant": "e1b3a61989b641b5173a68c94960dac7",
                "genes": [
                    {
                        "functional_annotation": "intron_variant",
                        "hgnc_id": 7882,
                        "region_annotation": "intronic",
                        "hgnc_symbol": "NOTCH2",
                    }
                ],
                "combined_score": 22,
                "rank_score": 6,
            },
            {
                "display_name": "1_120500463_A_ACACC",
                "not_loaded": false,
                "variant": "61f871950ff8c599df4d6513f959bb9e",
                "genes": [
                    {
                        "functional_annotation": "non_coding_transcript_variant",
                        "hgnc_id": 7882,
                        "region_annotation": "ncRNA_exonic",
                        "hgnc_symbol": "NOTCH2",
                    }
                ],
                "combined_score": 22,
                "rank_score": 6,
            },
            {
                "display_name": "1_120560920_T_C",
                "not_loaded": false,
                "variant": "7f6a7dc349249fdcecbf23d084744a1f",
                "genes": [
                    {
                        "functional_annotation": "non_coding_transcript_variant",
                        "hgnc_id": 7882,
                        "region_annotation": "ncRNA_exonic",
                        "hgnc_symbol": "NOTCH2",
                    }
                ],
                "combined_score": 22,
                "rank_score": 6,
            },
        ],
        "samples": [
            {
                "genotype_quality": 99,
                "display_name": "25-1-1A",
                "read_depth": 38,
                "genotype_call": "0/1",
                "allele_depths": [22, 16],
                "sample_id": "SVE2126A23",
            },
            {
                "genotype_quality": 99,
                "display_name": "25-2-1U",
                "read_depth": 26,
                "genotype_call": "0/1",
                "allele_depths": [13, 13],
                "sample_id": "ACC3320A8",
            },
            {
                "genotype_quality": 99,
                "display_name": "25-2-2U",
                "read_depth": 33,
                "genotype_call": "0/0",
                "allele_depths": [33, 0],
                "sample_id": "ACC3320A9",
            },
        ],
        "panels": [
            "NJU",
            "MSKI",
            "PEDHEP",
            "panel1",
            "OMIM-AUTO",
            "SKD",
            "PIDCAD",
            "IEM",
            "ID",
            "OMIM",
        ],
        "variant_rank": 18,
        "local_obs_old": 4,
        "missing_data": false,
        "rank_score": 16,
        "chromosome": "1",
        "display_name": "1_120478125_A_C_clinical",
        "variant_type": "clinical",
        "case_id": "soundclam",
        "clnsig": [{"revstat": "single", "accession": "RCV000121717.2", "value": 2}],
        "samtools": "Filtered",
        "cytoband_start": "p12",
        "cadd_score": 29,
        "hgnc_symbols": ["NOTCH2"],
        "rank_score_results": [
            {"score": 3, "category": "Splicing"},
            {"score": 3, "category": "Variant_call_quality_filter"},
            {"score": 1, "category": "Inheritance_Models"},
            {"score": 1, "category": "Clinical_significance"},
            {"score": 5, "category": "Consequence"},
            {"score": 0, "category": "Gene_intolerance_prediction"},
            {"score": 3, "category": "Conservation"},
            {"score": 2, "category": "allele_frequency"},
            {"score": 3, "category": "Deleteriousness"},
            {"score": 1, "category": "Protein_prediction"},
        ],
        "cytoband_end": "p12",
        "thousand_genomes_frequency": 0.001597439986653626,
        "gatk": "Pass",
        "simple_id": "1_120478125_A_C",
        "genetic_models": ["AR_comp", "AR_comp_dn"],
        "quality": 990.1599731445312,
        "filters": ["PASS"],
        "sub_category": "snv",
        "genes": [
            {
                "functional_annotation": "missense_variant",
                "hgnc_id": 7882,
                "sift_prediction": "deleterious",
                "polyphen_prediction": "unknown",
                "ensembl_id": "ENSG00000134250",
                "inheritance": [],
                "description": "notch 2",
                "region_annotation": "exonic",
                "transcripts": [
                    {
                        "smart_domain": "SM00181",
                        "hgnc_id": 7882,
                        "transcript_id": "ENST00000256646",
                        "coding_sequence_name": "c.3625T>G",
                        "sift_prediction": "deleterious",
                        "region_annotations": ["exonic"],
                        "swiss_prot": "Q04721",
                        "functional_annotations": ["missense_variant"],
                        "is_canonical": true,
                        "protein_sequence_name": "p.Phe1209Val",
                        "biotype": "protein_coding",
                        "strand": "-",
                        "protein_id": "ENSP00000256646",
                        "pfam_domain": "PF00008",
                        "prosite_profile": "PS50026",
                        "polyphen_prediction": "unknown",
                        "exon": "22/34",
                    },
                    {
                        "hgnc_id": 7882,
                        "transcript_id": "ENST00000478864",
                        "polyphen_prediction": "unknown",
                        "sift_prediction": "unknown",
                        "region_annotations": ["ncRNA_exonic"],
                        "swiss_prot": "unknown",
                        "functional_annotations": ["non_coding_transcript_exon_variant"],
                        "is_canonical": false,
                        "biotype": "processed_transcript",
                        "strand": "-",
                        "coding_sequence_name": "n.285T>G",
                        "exon": "2/2",
                    },
                ],
                "hgnc_symbol": "NOTCH2",
            }
        ],
        "alternative": "C",
        "exac_frequency": 0.003318999893963337,
        "position": 120478125,
        "cosmic_ids": null,
    }
    return sv_var


#############################################################
##################### Clinvar fixtures ######################
#############################################################
@pytest.fixture
def processed_submission() -> dict:
    """Mocks a dictionary corresponding to a processed submission coming from ClinVar.
    Copied from the ClinVar howto pages: https://www.ncbi.nlm.nih.gov/clinvar/docs/api_http/
    """

    return {
        "actions": [
            {
                "id": "SUB999999-1",
                "responses": [
                    {
                        "status": "processed",
                        "message": {
                            "errorCode": None,
                            "severity": "info",
                            "text": 'Your ClinVar submission processing status is "Success". Please find the details in the file referenced by actions[0].responses[0].files[0].url.',
                        },
                        "files": [
                            {
                                "url": "https://submit.ncbi.nlm.nih.gov/api/2.0/files/xxxxxxxx/sub999999-summary-report.json/?format=attachment"
                            }
                        ],
                        "objects": [],
                    }
                ],
                "status": "processed",
                "targetDb": "clinvar",
                "updated": "2021-03-24T04:22:04.101297Z",
            }
        ]
    }


@pytest.fixture
def successful_submission_summary_file_content() -> dict:
    """Mocks the submission summary file which is downloadable from the ClinVar API. The submission contains the status 'Success'.
    Based on the example collected from ClinVar API howto: https://www.ncbi.nlm.nih.gov/clinvar/docs/api_http/
    """

    return {
        "submissionName": "SUB673156",
        "submissionDate": "2021-03-25",
        "batchProcessingStatus": "Success",
        "batchReleaseStatus": "Not released",
        "totalCount": 1,
        "totalErrors": 0,
        "totalSuccess": 1,
        "totalPublic": 0,
        "submissions": [
            {
                "identifiers": {
                    "localID": "adefc5ed-7d59-4119-8b3d-07dcdc504c09_success1",
                    "clinvarLocalKey": "adefc5ed-7d59-4119-8b3d-07dcdc504c09_success1",
                    "localKey": "adefc5ed-7d59-4119-8b3d-07dcdc504c09_success1",
                    "clinvarAccession": "SCV000839746",
                },
                "processingStatus": "Success",
            },
        ],
    }


@pytest.fixture(scope="function")
def clinvar_form(request):
    """Mocks a ClinVar form compiled by the user. Contains Variant and CaseData input data"""
    data = ImmutableMultiDict(
        {
            "case_id": "internal_id",
            "category": "snv",
            "local_id": "4c7d5c70d955875504db72ef8e1abe77",
            "linking_id": "4c7d5c70d955875504db72ef8e1abe77",
            "chromosome": "7",
            "ref": "C",
            "alt": "A",
            "start": "124491972",
            "stop": "124491972",
            "gene_symbol": "POT1",
            "last_evaluated": "2022-09-19",
            "inheritance_mode": "Autosomal dominant inheritance",
            "assertion_method": "ACMG Guidelines, 2015",
            "assertion_method_cit_db": "PMID",
            "assertion_method_cit_id": "25741868",
            "variations_ids": "rs116916706",
            "clinsig": "Likely pathogenic, low penetrance",
            "clinsig_comment": "test clinsig comment",
            "clinsig_cit": "test clinsig cit",
            "condition_comment": "test condition comment",
            "include_ind": ["NA12882"],
            "individual_id": ["NA12882", "NA12877", "NA12878"],
            "affected_status": ["yes", "no", "no"],
            "allele_of_origin": ["germline"] * 3,
            "collection_method": ["clinical testing"] * 3,
            "condition_type": "HPO",
            "conditions": ["0001298", "0001250"],
            "multiple_condition_explanation": "Novel disease",
        }
    )
    return data
