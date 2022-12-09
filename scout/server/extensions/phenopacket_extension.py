"""
Extension to Scout for Phenopacket integration (http://phenopackets.org).
Write and read JSON Phenopackets, and interact with phenopacket-api backend
(https://github.com/squeezeday/phenopacket-api).
"""
import logging

from google.protobuf.json_format import MessageToJson, Parse
from phenopackets import Individual, OntologyClass, Phenopacket, PhenotypicFeature

LOG = logging.getLogger(__name__)


class PhenopacketAPI:
    def __init__(self):
        self.url = None
        self.api_key = None

    def init_app(self, app):
        self.url = app.config.get("PHENOPACKET_API_URL")
        # Also API key at some point, but not yet supported on the backend (uses IP filter)
        self.api_key = app.config.get("PHENOPACKET_API_KEY")

    def phenopacket_hpo(case, export_ind_id=None):
        """Generate Phenopacket JSON for a Scout case.
        HPO terms associated with the first affected individual (or optionally a selected individual), and the IDs of that individual,
        is exported.

        Args:
            case: Scout case object dict
        Returns:
            json: Phenopacket json string
        """

        phenotype_terms = case.get("phenotype_terms")

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
                if name in [
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

    def phenopacket_file_import(
        store, institute_obj, case_obj, user_obj, case_url, phenopacket_file
    ):
        """Import Phenopacket json and add HPO terms found to affected individual
        Args:
            store:  store object
            institute_obj:  institute object
            case_obj: case object
            user_obj: user object
            case_url: case url
            phenopacket_file: werkzeug FileStorage object
        """

        phenopacket = Parse(
            message=Phenopacket(),
            text=phenopacket_file.read(),
        )

        # add a new phenotype item/group to the case
        hpo_term = None
        omim_term = None

        for feature in phenopacket.phenotypic_features:
            phenotype_term = feature.type
            LOG.debug(f"found phenopacket term {phenotype_term.id} labelled {phenotype_term.label}")

            if phenotype_term.id.startswith("HP:") or len(phenotype_term.id) == 7:
                hpo_term = phenotype_term.id
            else:
                omim_term = phenotype_term.id

            store.add_phenotype(
                institute=institute_obj,
                case=case_obj,
                user=user_obj,
                link=case_url,
                hpo_term=hpo_term,
                omim_term=omim_term,
                is_group=False,
                phenotype_inds=[],
            )
