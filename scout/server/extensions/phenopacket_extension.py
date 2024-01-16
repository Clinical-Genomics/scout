"""
Extension to Scout for Phenopacket integration (http://phenopackets.org).
Write and read JSON Phenopackets, and interact with phenopacket-api backend
(https://github.com/squeezeday/phenopacket-api).
"""
import json as json_lib
import logging

from google.protobuf.json_format import MessageToJson, Parse
from phenopackets import Individual, OntologyClass, Phenopacket, PhenotypicFeature

from scout.constants import PHENOTYPE_MAP, SEX_MAP
from scout.server.utils import jsonconverter
from scout.utils.scout_requests import get_request_json

LOG = logging.getLogger(__name__)


class PhenopacketAPI:
    def __init__(self):
        self.url = None
        self.api_key = None

    def init_app(self, app):
        self.url = app.config.get("PHENOPACKET_API_URL")

    def phenopacket_from_case(self, case, export_ind_id=None):
        """Generate Phenopacket JSON for a Scout case.
        HPO terms associated with the first affected individual (or optionally a selected individual), and the IDs of that individual,
        is exported.

        Args:
            case(dict): Scout case object
            export_ind_id(str): individual id selecting an individual for export. Leave unset to pick affected individuals.
        Returns:
            json: Phenopacket json string
        """

        phenotype_terms = case.get("phenotype_terms")

        if not phenotype_terms:
            return None

        p_individual = None
        p_features = []

        for ind in case.get("individuals", []):
            if (export_ind_id and export_ind_id != ind.get("individual_id")) or PHENOTYPE_MAP[
                int(ind.get("phenotype"))
            ] != "affected":
                continue

            sex = SEX_MAP[int(ind.get("sex"))].upper()
            name = ind.get("display_name")
            p_individual = Individual(id=name, sex=sex)

            for term in phenotype_terms:
                if not term.get("individuals") or name in [
                    term_ind.get("individual_name") for term_ind in term.get("individuals")
                ]:
                    p_features.append(
                        PhenotypicFeature(
                            type=OntologyClass(
                                id=term.get("phenotype_id"), label=term.get("feature")
                            )
                        )
                    )

        if not p_individual:
            return None

        phenopacket = Phenopacket(
            id=case.get("display_name"), subject=p_individual, phenotypic_features=p_features
        )
        return MessageToJson(phenopacket)

    def file_import(self, phenopacket_file):
        """Import Phenopacket from JSON file.
        Args:
            phenopacket_file: werkzeug FileStorage object
        Returns:
            phenopacket: Phenopacket object
        """

        phenopacket = Parse(
            message=Phenopacket(),
            text=phenopacket_file.read(),
        )

        return phenopacket

    def get_hash(self, phenopacket_hash):
        """Retrieve phenopacket from backend using hash.

        The retrieved serialized json phenopacket may not convert back easily to a phenopacket object.
        We simplify it a bit first, potentially dropping some data that we anyway do not save or use
        downstream, before actually converting it to a message string that can be parsed into a Phenopacket.
        """

        query = f"{self.url}/api/v1/phenopacket?hash={phenopacket_hash}"

        json_response = get_request_json(query)

        if json_response.get("message"):
            LOG.warning(json_response["message"])
            return

        json_content = json_response.get("content")
        if not json_content:
            return None
        json_content = json_content[0]

        selected_json = {}
        valid_phenopacket_fields = [
            "id",
            "subject",
            "phenotypicFeatures",
        ]
        for field in valid_phenopacket_fields:
            if field in json_content:
                if field == "subject":
                    # We only use the subject id, and parsing time, eg dateOfBirth, is complicated
                    subject = json_content["subject"]
                    subject_id = subject.get("id")
                    selected_json["subject"] = {"id": subject_id}
                else:
                    selected_json[field] = json_content[field]

        json_str = json_lib.dumps(selected_json, default=jsonconverter)

        return Parse(
            message=Phenopacket(),
            text=json_str,
        )

    def phenotype_individuals_affected_in_case(self, case_obj):
        """Return a list of phenotype individual strings for affected individuals.

        This type of strings (individual id + "|" + display name) are used to assign phenotypes to
        individuals on the case object.

        Args:
            case_obj: case object to get individuals
        Returns:
            selected_individuals(list(str)): a list of phenotype ind strings
        """
        selected_individuals = []
        for ind in case_obj.get("individuals", []):
            if PHENOTYPE_MAP[int(ind.get("phenotype"))] == "affected":
                selected_individuals.append(f"{ind.get('individual_id')}|{ind.get('display_name')}")
        return selected_individuals

    def add_phenopacket_to_case(
        self, store, institute_obj, case_obj, user_obj, case_url, phenopacket
    ):
        """
        Given a Phenopacket, add HPO terms found to individual in packet with matching ID,
        or all case affected individuals.

        Args:
            store: store object
            institute_obj: institute object for the case
            case_obj: case object to receive phenotypes
            user_obj: user object for user to associate action with
            case_url: case url to store on action
            phenopacket: Phenopacket obj
        """

        # Select individual(s) mentioned in phenopacket
        selected_individuals = []
        for ind in case_obj.get("individuals", []):
            if phenopacket.id == ind.get("individual_id") or phenopacket.subject.id == ind.get(
                "display_name"
            ):
                selected_individuals.append(f"{ind.get('individual_id')}|{ind.get('display_name')}")

        # Otherwise select affected individuals
        if not selected_individuals:
            selected_individuals = self.phenotype_individuals_affected_in_case(case_obj)

        # add a new phenotype item/group to the case
        hpo_term = None
        omim_term = None

        for feature in phenopacket.phenotypic_features:
            phenotype_term = feature.type

            if phenotype_term.id.startswith("HP:") or len(phenotype_term.id) == 7:
                hpo_term = phenotype_term.id
            else:
                omim_term = phenotype_term.id

            if feature.excluded == True:
                continue

            store.add_phenotype(
                institute=institute_obj,
                case=case_obj,
                user=user_obj,
                link=case_url,
                hpo_term=hpo_term,
                omim_term=omim_term,
                is_group=False,
                phenotype_inds=selected_individuals,
            )
