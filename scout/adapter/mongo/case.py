# -*- coding: utf-8 -*-
import datetime
import logging
import operator
import re
from copy import deepcopy
from typing import Any, Dict, List, Optional

import pymongo
from bson import ObjectId

from scout.build.case import build_case
from scout.constants import ACMG_MAP, ID_PROJECTION
from scout.exceptions import ConfigError, IntegrityError
from scout.parse.variant.ids import parse_document_id
from scout.utils.algorithms import ui_score

LOG = logging.getLogger(__name__)


class CaseHandler(object):
    """Part of the pymongo adapter that handles cases and institutes"""

    def cases_by_phenotype(self, phenotype_terms, owner, case_id=None):
        """Take a case obj and return a iterable with the most phenotypically similar cases

        Args:
            phenotype_terms(list):[ "HP:0001250", "HP:0000707",.. ]
            owner(str): institute id
            case_id(str): Id of a case, when searching for cases similar to another

        Returns:
            scores(list(tuple)): Returns a list of tuples like (case_id, score) with the most
                                 similar case first
        """
        scores = {}
        set_1 = set()
        if len(phenotype_terms) == 0:
            LOG.warning("No phenotype terms provided, please provide ar least one HPO term")
            return None
        # Add all ancestors of all terms
        for term in phenotype_terms:
            hpo_term = self.hpo_term(term)
            if not hpo_term:
                continue
            set_1 = set_1.union(set(hpo_term.get("all_ancestors", [])))
        # Need to control what cases to look for here
        # Fetch all cases with phenotypes
        CASES_BY_PHENOTYPE_PROJECTION = {"phenotype_terms": 1}
        for case in self.cases(
            phenotype_terms=True, owner=owner, projection=CASES_BY_PHENOTYPE_PROJECTION
        ):
            set_2 = set()
            if case["_id"] == case_id:
                continue
            # Add all ancestors if all terms
            for term in case["phenotype_terms"]:
                hpo_term = self.hpo_term(term["phenotype_id"])
                if not hpo_term:
                    continue
                set_2 = set_2.union(set(hpo_term.get("all_ancestors", [])))

            LOG.debug(
                f"Check phenotypic similarity between terms:{phenotype_terms} and case {case['_id']}"
            )

            scores[case["_id"]] = ui_score(set_1, set_2)
        # Returns a list of tuples with highest score first
        return sorted(scores.items(), key=operator.itemgetter(1), reverse=True)

    def _set_similar_phenotype_query(
        self,
        query: Dict[str, Any],
        query_field: str,
        query_term: str,
        institute_id: str,
    ):
        """Adds query parameters when search is performed by case or phenotype similarity

        Args:
            query(dict): cases search query
            query_field(str) example:"status"
            query_term(str) example:"active"
            name_query(dict) args provided by users in cases filter search
            institute_id(str): institute to search cases for
        """
        hpo_terms = []
        order = None
        CASE_SIMILAR_PROJECTION = {"phenotype_terms": 1}
        if query_field == "similar_case":
            case_obj = self.case(
                display_name=query_term,
                institute_id=institute_id,
                projection=CASE_SIMILAR_PROJECTION,
            )
            if case_obj is None:
                query["_id"] = {"$in": []}  # No result should be returned by query
                return

            for term in case_obj.get("phenotype_terms", []):
                hpo_terms.append(term.get("phenotype_id"))
            similar_cases = self.cases_by_phenotype(hpo_terms, institute_id, case_obj["_id"])
        else:  # similar HPO terms
            hpo_terms = list(query_term.replace(" ", "").split(","))
            similar_cases = self.cases_by_phenotype(hpo_terms, institute_id, None)

        if len(similar_cases) == 0:  # No cases similar to given phenotype
            query["_id"] = {"$in": []}  # No result should be returned by query
            return

        similar_case_ids = []
        order = []
        for i in similar_cases:
            similar_case_ids.append(i[0])
            order.append(i[1])
        query["_id"] = {"$in": similar_case_ids}

        return order

    def _set_genes_of_interest_query(
        self, query: Dict[str, Any], query_field: str, query_term: str
    ):
        """Adds query parameters when search is aimed at retrieving cases with a certain pinned or causative gene

        If the gene is not found in the hgnc collection, the id query should not return any results.

        Args:
            query(dict): cases search query
            query_field(str) "pinned" or "causative"
            query_term(str) example:"POT1"
        """
        hgnc_id = self.hgnc_id(hgnc_symbol=query_term)
        if hgnc_id is None:
            LOG.debug(f"No gene with the HGNC symbol {query_term} found.")
            query["_id"] = {"$in": []}  # No result should be returned by query
            return

        unwind = "$causatives"
        lookup_local = "causatives"
        if query_field == "pinned":
            unwind = "$suspects"
            lookup_local = "suspects"

        cases_with_gene_doc = self.case_collection.aggregate(
            [
                {"$unwind": unwind},
                {
                    "$lookup": {
                        "from": "variant",
                        "localField": lookup_local,
                        "foreignField": "_id",
                        "as": "lookup_variant",
                    }
                },
                {"$match": {"lookup_variant.hgnc_ids": hgnc_id}},
                {"$project": ID_PROJECTION},
            ]
        )
        case_ids = [case["_id"] for case in cases_with_gene_doc]
        query["_id"] = {"$in": case_ids}

    def _set_case_name_query(self, query: Dict[str, Any], query_term: str):
        """Set case query to reg exp search in case and individual display names for parts of the name query."""

        case_name_regex = {"$regex": re.escape(query_term)}
        query["$or"] = [
            {"display_name": case_name_regex},
            {"individuals.display_name": case_name_regex},
            {"_id": case_name_regex},
        ]

    def _set_case_phenotype_query(self, query: Dict[str, Any], query_term: str):
        """Set case query based on phenotype terms.

        The user may have provided multiple query (HPO) terms.

        If the no query term is given (the phenotype query string is empty), instead query for cases
        that lack HPO terms.
        """
        if query_term != "":
            query["phenotype_terms.phenotype_id"] = {
                "$in": list(query_term.replace(" ", "").split(","))
            }
            return

        query["$or"] = [
            {"phenotype_terms": {"$size": 0}},
            {"phenotype_terms": {"$exists": False}},
        ]

    def _set_diagnosis_query(self, query: Dict[str, Any], query_term: str):
        """Set diagnosis query based on query term.
        The user might have provided multiple query terms.

        The OMIM query terms needs to match both old style and current phenotypes for backwards
        compatibility.

        Presently, OMIM phenotypes are assigned as a list of dictionaries, but we also need to
        match the old way of saving OMIM terms, which was a list of ids [616538,611277]

        The query should be set to check for cases with no HPO terms if the query term is empty.
        """
        if query_term != "":
            omim_terms = list(query_term.replace(" ", "").split(","))
            query["$or"] = [
                {"diagnosis_phenotypes.disease_id": {"$in": omim_terms}},
                {"diagnosis_phenotypes": {"$in": omim_terms}},
            ]
            return

        query["$or"] = [
            {"diagnosis_phenotypes": {"$size": 0}},
            {"diagnosis_phenotypes": {"$exists": False}},
        ]

    def _set_synopsis_query(self, query: Dict[str, Any], query_term: str):
        """Set query to search in the free text synopsis for query_term."""

        if query_term != "":
            query["$text"] = {"$search": re.escape(query_term)}
        else:
            query["synopsis"] = ""

    def _populate_name_query(self, query, name_query, owner=None, collaborator=None):
        """Parses and adds query parameters provided by users in cases search filter.

        Args:
            query(dict): cases search query
            name_query(dict): args provided by users in cases filter search
            owner(dict): an institute id
            collaborator(dict): an institute id
        """
        order = None
        query_field = name_query.split(":")[0]  # example:status
        query_term = name_query[name_query.index(":") + 1 :].strip()

        if query_field == "case" and query_term != "":
            self._set_case_name_query(query, query_term)

        if query_field == "exact_pheno":
            self._set_case_phenotype_query(query, query_term)

        if query_field == "exact_dia":
            self._set_diagnosis_query(query, query_term)

        if query_field == "synopsis":
            self._set_synopsis_query(query, query_term)

        if query_field == "panel":
            query["panels"] = {"$elemMatch": {"panel_name": query_term, "is_default": True}}

        if query_field == "status":
            query["status"] = query_term

        if query_field == "tags":
            query["tags"] = query_term.lower()

        if query_field == "track":
            query["track"] = query_term

        if query_field == "pheno_group":
            if query_term != "":
                query["phenotype_groups.phenotype_id"] = query_term
            else:
                query["$or"] = [
                    {"phenotype_groups": {"$size": 0}},
                    {"phenotype_groups": {"$exists": False}},
                ]
        if query_field == "cohort":
            query["cohorts"] = query_term

        if query_term != "" and query_field in ["similar_case", "similar_pheno"]:
            order = self._set_similar_phenotype_query(
                query, query_field, query_term, owner or collaborator
            )

        if query_term != "" and query_field in ["pinned", "causative"]:
            self._set_genes_of_interest_query(query, query_field, query_term)

        if query_field == "user":
            query_terms = query_term.split(" ")
            user_query = {
                "$and": [{"name": {"$regex": term, "$options": "i"}} for term in query_terms]
            }
            users = self.user_collection.find(user_query)
            query["assignees"] = {"$in": [user["_id"] for user in users]}

        return order

    def _update_case_id_query(self, query, id_list):
        """Update a case query ["_id"]["$in"] values using an additional list of case _ids

        Args:
            query(dict): a query dictionary that contains a ["_id"]["$in"] key with case _ids as value
            id_list(list): a list of case _ids to update query with
        """
        if query.get("_id"):  # Check if other filter already limits the search by case _id
            preselected_ids = query["_id"].get("$in", [])
            query["_id"]["$in"] = list(
                set(preselected_ids).intersection(set(id_list))
            )  # limit also by case _ids present in id_list
        else:  # use id_list for filtering
            query["_id"] = {"$in": id_list}

    def cases(
        self,
        owner: Optional[str] = None,
        collaborator: Optional[str] = None,
        query: Optional[Dict[str, Any]] = None,
        skip_assigned: bool = False,
        has_causatives: bool = False,
        reruns: bool = False,
        rerun_monitor: bool = False,
        finished: bool = False,
        research_requested: bool = False,
        is_research: bool = False,
        has_rna_data: bool = False,
        status: Any = None,
        phenotype_terms: bool = False,
        group: Optional[ObjectId] = None,
        pinned: bool = False,
        cohort: bool = False,
        name_query: Optional[str] = None,
        yield_query: bool = False,
        within_days: Optional[int] = None,
        assignee: Optional[str] = None,
        verification_pending: bool = None,
        has_clinvar_submission: bool = None,
        projection: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Fetches all cases from the backend.

        Args:
            collaborator(str): If collaborator should be considered
            owner(str): Query cases for specified case owner only
            query(dict): If a specific query is used
            skip_assigned(bool)
            has_causatives(bool)
            reruns(bool)
            finished(bool)
            research_requested(bool)
            is_research(bool)
            has_rna_data(bool): if case has RNA-seq data associated
            status(str or dict expression)
            tags(list(str)): search case tags
            group(ObjectId): fetch all cases in a named case group
            cohort(bool): Fetch all cases with cohort tags
            phenotype_terms(bool): Fetch all cases with phenotype
            pinned(bool): Fetch all cases with pinned variants
            name_query(str): Could be hpo term, HPO-group, user, part of display name,
                             part of ids or part of synopsis
            yield_query(bool): If true, only return mongo query dict for use in
                                compound querying.
            within_days(int): timespan (in days) for latest event on case
            assignee(str): id of an assignee
            verification_pending(bool): If search should be restricted to cases with verification_pending
            has_clinvar_submission(bool): If search should be limited to cases with a ClinVar submission
            projection(dict): Sometimes only some values in each case are required. This saves memory.

        Returns:
            Cases ordered by date.
            If yield_query is True, does not pose query to db;
                instead returns corresponding query dict
                that can be reused in compound queries or for testing.
        """

        def _conditional_set_query_value(query, condition, set_key, set_value):
            """Adds kes/values to a growing query dictionary for selecting cases from db.
            Checks if 'condition' has a value. If it does, adds set_key/set_value as key/value to the growing
            query dictionary

            Args:
                query(dict): case query dictionary
                condition(misc): a variable that could have a value or be None
                set_key(str): new query key query[set_key]
                set_value(misc): value to assign to query[set_key]
            """
            if condition:
                query[set_key] = set_value

        query = query or {}
        order = None
        # Prioritize when both owner and collaborator params are present
        if collaborator and owner:
            collaborator = None

        _conditional_set_query_value(
            query=query,
            condition=collaborator,
            set_key="collaborators",
            set_value=collaborator,
        )

        _conditional_set_query_value(query=query, condition=owner, set_key="owner", set_value=owner)

        _conditional_set_query_value(
            query=query,
            condition=skip_assigned,
            set_key="assignees",
            set_value={"$exists": False},
        )

        _conditional_set_query_value(
            query=query,
            condition=has_causatives,
            set_key="causatives",
            set_value={"$exists": True, "$ne": []},
        )

        _conditional_set_query_value(
            query=query, condition=reruns, set_key="rerun_requested", set_value=True
        )

        _conditional_set_query_value(
            query=query,
            condition=rerun_monitor,
            set_key="rerun_monitoring",
            set_value=True,
        )

        _conditional_set_query_value(
            query=query, condition=status, set_key="status", set_value=status
        )

        _conditional_set_query_value(
            query=query,
            condition=finished,
            set_key="status",
            set_value={"$in": ["solved", "archived"]},
        )

        _conditional_set_query_value(
            query=query,
            condition=research_requested,
            set_key="research_requested",
            set_value=True,
        )

        _conditional_set_query_value(
            query=query,
            condition=is_research,
            set_key="is_research",
            set_value={"$exists": True, "$eq": True},
        )

        _conditional_set_query_value(
            query=query,
            condition=phenotype_terms,
            set_key="phenotype_terms",
            set_value={"$exists": True, "$ne": []},
        )

        _conditional_set_query_value(
            query=query,
            condition=pinned,
            set_key="suspects",
            set_value={"$exists": True, "$ne": []},
        )

        _conditional_set_query_value(
            query=query,
            condition=cohort,
            set_key="cohorts",
            set_value={"$exists": True, "$ne": []},
        )

        _conditional_set_query_value(
            query=query, condition=group, set_key="group", set_value={"$in": [group]}
        )

        _conditional_set_query_value(
            query=query,
            condition=assignee,
            set_key="assignees",
            set_value={"$in": [assignee]},
        )

        if name_query:
            # Case search filter form query
            order = self._populate_name_query(query, name_query, owner, collaborator)

        if within_days:
            query["_id"] = {
                "$in": self.last_modified_cases(
                    within_days,
                    has_causatives,
                    finished,
                    reruns,
                    research_requested,
                    status,
                )
            }

        if verification_pending:  # Filter for cases with Sanger verification pending
            sanger_pending_cases = self.verification_missing_cases(owner)
            self._update_case_id_query(query, sanger_pending_cases)

        if has_clinvar_submission:
            clinvar_subm_cases = self.clinvar_cases(collaborator or owner)
            self._update_case_id_query(query, clinvar_subm_cases)

        if has_rna_data:
            cases_with_rna = self.rna_cases(collaborator or owner)
            self._update_case_id_query(query, cases_with_rna)

        if yield_query:
            return query

        if order:
            return self.case_collection.find(query, projection)

        return self.case_collection.find(query, projection).sort("updated_at", -1)

    def rna_cases(self, owner):
        """Retrieve all cases with RNA-seq data for a given institute

        Args:
            owner(str): _id of an institute

        Returns:
            list of case _ids
        """
        EXISTS_NOT_NULL = {"$exists": True, "$nin": [None, ""]}
        query = {
            "owner": owner,
            "$or": [
                {"gene_fusion_report": EXISTS_NOT_NULL},
                {"gene_fusion_report_research": EXISTS_NOT_NULL},
                {"individuals.rna_alignment_path": EXISTS_NOT_NULL},
                {"individuals.splice_junctions_bed": EXISTS_NOT_NULL},
                {"individuals.rna_coverage_bigwig": EXISTS_NOT_NULL},
                {"RNAfusion_report": EXISTS_NOT_NULL},
                {"RNAfusion_report_research": EXISTS_NOT_NULL},
                {"RNAfusion_inspector": EXISTS_NOT_NULL},
                {"RNAfusion_inspector_research": EXISTS_NOT_NULL},
            ],
        }
        return [case["_id"] for case in self.case_collection.find(query)]

    def last_modified_cases(
        self, within_days, has_causatives, finished, reruns, research_requested, status
    ):
        """Retrieve cases that have been modified during the last n. days
        Args:
            within_days(int)
            has_causatives(bool)
            finished(bool)
            reruns(bool)
            research_requested(bool)
            status(str)

        Returns:
            recent_cases(list): list of case _ids
        """
        verbs = set()
        if has_causatives:
            verbs.add("mark_causative")
        if finished:
            verbs.add("archive")
            verbs.add("mark_causative")
        if reruns:
            verbs.add("rerun")
        if research_requested:
            verbs.add("open_research")
        if status and status == "solved":
            verbs.add("mark_causative")
        verbs = list(verbs)

        days_datetime = datetime.datetime.now() - datetime.timedelta(days=within_days)
        # Look up 'mark_causative' events added since specified number days ago
        event_query = {
            "category": "case",
            "verb": {"$in": verbs},
            "created_at": {"$gte": days_datetime},
        }
        recent_events = self.event_collection.find(event_query)
        recent_cases = set()
        # Find what cases these events concern
        for event in recent_events:
            recent_cases.add(event["case"])
        return list(recent_cases)

    def verification_missing_cases(self, institute_id):
        """Fetch all cases with at least a variant with validation ordered but still pending
        Args:
            institute_id(str): id of an institute

        Returns:
            sanger_missing_cases(list): a list of case _ids with variants having Sanger validation missing
        """
        sanger_missing_cases = []
        sanger_ordered_by_case = self.sanger_ordered(
            institute_id=institute_id
        )  # a list of dictionaries like this: [{'_id': 'internal_id', 'vars': ['a1d6df24404c007570021531b80b1e1e']}, ..]
        for case_variants in sanger_ordered_by_case:
            if self.case(case_id=case_variants["_id"], projection=ID_PROJECTION) is None:
                continue
            for variant_id in case_variants["vars"]:
                var_obj = self.variant(case_id=case_variants["_id"], document_id=variant_id)

                if var_obj is None or var_obj.get("validation") in [
                    "True positive",
                    "False positive",
                ]:
                    continue
                sanger_missing_cases.append(case_variants["_id"])

        return sanger_missing_cases

    def cases_by_status(
        self, status: str, institute_id: Optional[str] = None, projection: Optional[Dict] = None
    ):
        """retrieves all cases for an institute given their status."""
        query = {}

        if institute_id:
            query["collaborators"] = institute_id

        query["status"] = status

        return self.case_collection.find(query, projection=projection).sort("updated_at", -1)

    def case_ids_from_group_id(self, group_id):
        """Fetches any cases with given group_id from backend.

        Args:
            group_id(str): A tag for related cases. A case can belong to several groups.

        Returns:
            case_ids(list): A list of case _ids
        """

        return [
            case["_id"]
            for case in self.case_collection.find(
                {"group": {"$elemMatch": {"$eq": group_id}}}, ID_PROJECTION
            )
        ]

    def nr_cases_by_status(self, institute_id=None):
        """For an institute, retrieves number of cases in each case status category
        Args:
            institute_id(str): Institute id

        Returns:
            dict with case.status as keys and nr cases as value
        """
        pipeline = []
        if institute_id:
            pipeline.append({"$match": {"collaborators": institute_id}})
        pipeline.append({"$group": {"_id": "$status", "count": {"$sum": 1}}})
        result = self.case_collection.aggregate(pipeline)
        return {res["_id"]: res["count"] for res in result}

    def update_dynamic_gene_list(
        self,
        case,
        hgnc_symbols=None,
        hgnc_ids=None,
        phenotype_ids=None,
        add_only=False,
        delete_only=False,
    ):
        """Update the dynamic gene list for a case

        Adds a list of dictionaries to case['dynamic_gene_list'] that looks like

        {
            hgnc_symbol: str,
            hgnc_id: int,
            description: str
        }

        Arguments:
            case (dict): The case that should be updated
            hgnc_symbols (iterable): A list of hgnc_symbols
            hgnc_ids (iterable): A list of hgnc_ids
            phenotype_ids(list): optionally add phenotype_ids used to generate list
            add_only(bool): set by ADDGENE to add genes, and NOT reset previous dynamic_gene_list
            delete_only(bool): set by REMOVEGENES when user removes genes from the auto-generated HPO panel

        Returns:
            updated_case(dict)
        """
        case_build = str(case.get("genome_build", "37"))
        build = case_build if case_build in ["37", "38"] else "37"
        dynamic_gene_list = []
        if add_only:
            dynamic_gene_list = list(
                self.case_collection.find_one(
                    {"_id": case["_id"]}, {"dynamic_gene_list": 1, "_id": 0}
                ).get("dynamic_gene_list", [])
            )

        res = []
        if hgnc_ids:
            res = self.hgnc_collection.find({"hgnc_id": {"$in": hgnc_ids}, "build": build})
        elif hgnc_symbols:
            for symbol in hgnc_symbols:
                those_genes = self.gene_aliases(symbol=symbol, build=build)
                for gene_obj in those_genes:
                    res.append(gene_obj)

        for gene_obj in res:
            dynamic_gene_list.append(
                {
                    "hgnc_symbol": gene_obj["hgnc_symbol"],
                    "hgnc_id": gene_obj["hgnc_id"],
                    "description": gene_obj["description"],
                }
            )
        updated_case = self.case_collection.find_one_and_update(
            {"_id": case["_id"]},
            {
                "$set": {
                    "dynamic_gene_list": dynamic_gene_list,
                    "dynamic_panel_phenotypes": phenotype_ids,
                    "dynamic_gene_list_edited": (add_only or delete_only)
                    or (dynamic_gene_list and not phenotype_ids),
                }
            },
            return_document=pymongo.ReturnDocument.AFTER,
        )
        return updated_case

    def case(
        self,
        case_id: Optional[str] = None,
        institute_id: Optional[str] = None,
        display_name: Optional[str] = None,
        projection: Optional[Dict] = None,
    ) -> Dict:
        """Fetches a single case from database
        Use either the _id or combination of institute_id and display_name.
        Projection is a pymongo projection dict.
        Yields a single Case, possibly a thin version case projected by the projection.
        """
        query = {}
        if case_id:
            query["_id"] = case_id
        else:
            if not (institute_id and display_name):
                raise ValueError(
                    "Please provide either case ID or both institute_id and display_name."
                )
            query["owner"] = institute_id
            query["display_name"] = display_name

        return self.case_collection.find_one(filter=query, projection=projection)

    def delete_case(self, case_id=None, institute_id=None, display_name=None):
        """Delete a single case from database

        Args:
            institute_id(str)
            case_id(str)

        Returns:
            case_obj(dict): The case that was deleted
        """
        query = {}
        if case_id:
            query["_id"] = case_id
            LOG.info("Deleting case %s", case_id)
        else:
            if not (institute_id and display_name):
                raise ValueError("Have to provide both institute_id and display_name")
            LOG.info("Deleting case %s institute %s", display_name, institute_id)
            query["owner"] = institute_id
            query["display_name"] = display_name

        result = self.case_collection.delete_one(query)
        return result

    def check_existing_data(self, case_obj, existing_case, institute_obj, update, keep_actions):
        """Make sure data from case to be loaded/reuploaded conforms to case data already saved in database.
           Return eventual evaluated variants to be propagated to the updated case if keep_actions is True

        Args:
            case_obj(dict): case dictionary to be loaded/reuploaded
            existing_case(dict): a case with same _id or same display_name and institute_id as case_obj
            institute_obj(dict): institute dictionary
            update(bool): If existing case should be updated
            keep_actions(bool): If old evaluated variants should be kept when case is updated

        Returns:
            previous_evaluated_variants(list): list of variants evaluated in previous case
                or None if case is not already present in the database.
        """

        if existing_case is None:
            return

        if (
            existing_case["_id"] != case_obj["_id"]
        ):  # This happens whenever institute and case display name coincide
            raise IntegrityError(
                f"A case with different _id ({existing_case['_id']} vs {case_obj['_id']}) and same display name ({case_obj['display_name']}) already exists for this institute."
            )

        if existing_case and not update:
            raise IntegrityError("Case %s already exists in database" % case_obj["_id"])

        # Enforce same display name for updated case as existing case
        if case_obj["display_name"] != existing_case["display_name"]:
            raise IntegrityError("Updated case name doesn't match existing case name.")

        # Check that individuals from updated case match individuals from existing case in ID, name and affected status
        existing_case_inds = set(
            [
                (ind["individual_id"], ind["display_name"], ind["phenotype"])
                for ind in existing_case.get("individuals")
            ]
        )
        case_inds = set(
            [
                (ind["individual_id"], ind["display_name"], ind["phenotype"])
                for ind in case_obj.get("individuals")
            ]
        )
        if existing_case_inds != case_inds:
            raise IntegrityError(
                f"Updated case individuals ({case_inds}) don't match individuals from existing case ({existing_case_inds}). Please either delete old case or modify updated case individuals."
            )

        if keep_actions:
            # collect all variants with user actions for this case
            return list(self.evaluated_variants(case_obj["_id"], institute_obj["_id"]))

    def update_case_data_sharing(self, old_case: dict, new_case: dict):
        """Update data sharing info for a case that is re-runned/re-uploaded."""
        for key in ["beacon", "mme_submission"]:
            if key in old_case:
                new_case[key] = old_case[key]

    def load_case(self, config_data: dict, update: bool = False, keep_actions: bool = True) -> dict:
        """Load a case into the database

        Check if the owner and the institute exists.
        If update is True, old case variants will be removed.

        Args:
            config_data(dict): A dictionary with all the necessary information
            update(bool): If existing case should be updated
            keep_actions(bool): Attempt transfer of existing case user actions to new vars
        """
        # Check that the owner exists in the database
        institute_obj = self.institute(config_data["owner"])
        if not institute_obj:
            raise IntegrityError("Institute '%s' does not exist in database" % config_data["owner"])
        # Build the case object
        case_obj = build_case(config_data, self)
        # Check if case exists with old case id
        old_caseid = "-".join([case_obj["owner"], case_obj["display_name"]])
        old_case = self.case(old_caseid)

        # This is to keep sanger order and validation status
        old_sanger_variants = self.case_sanger_variants(case_obj["_id"])

        genome_build = str(config_data.get("genome_build", 37))

        if old_case:
            LOG.info(
                "Update case id for existing case: %s -> %s",
                old_caseid,
                case_obj["_id"],
            )
            self.update_caseid(old_case, case_obj["_id"])
            update = True

        # Retrieve info to be propagated to eventual updated case
        # previously evaluated variants (acmg, manual rank, cancer tier, dismissed, mosaic, commented)
        existing_case = self.case(case_id=case_obj["_id"]) or self.case(
            institute_id=institute_obj["_id"], display_name=case_obj["display_name"]
        )
        old_evaluated_variants = self.check_existing_data(
            case_obj, existing_case, institute_obj, update, keep_actions
        )

        if existing_case and keep_actions:
            # collect all variants with user actions for this case
            old_evaluated_variants = list(
                self.evaluated_variants(case_obj["_id"], case_obj["owner"])
            )

        files = [
            {"file_name": "vcf_snv", "variant_type": "clinical", "category": "snv"},
            {"file_name": "vcf_sv", "variant_type": "clinical", "category": "sv"},
            {
                "file_name": "vcf_cancer",
                "variant_type": "clinical",
                "category": "cancer",
            },
            {
                "file_name": "vcf_cancer_sv",
                "variant_type": "clinical",
                "category": "cancer_sv",
            },
            {"file_name": "vcf_str", "variant_type": "clinical", "category": "str"},
            {"file_name": "vcf_mei", "variant_type": "clinical", "category": "mei"},
            {
                "file_name": "vcf_fusion",
                "variant_type": "clinical",
                "category": "fusion",
            },
        ]

        try:
            for vcf_file in files:
                # Check if file exists
                if not case_obj["vcf_files"].get(vcf_file["file_name"]):
                    LOG.debug("didn't find {}, skipping".format(vcf_file["file_name"]))
                    continue

                variant_type = vcf_file["variant_type"]
                category = vcf_file["category"]
                if update:
                    self.delete_variants(
                        case_id=case_obj["_id"],
                        variant_type=variant_type,
                        category=category,
                    )

                # add variants
                self.load_variants(
                    case_obj=case_obj,
                    variant_type=variant_type,
                    category=category,
                    build=genome_build,
                    rank_threshold=case_obj.get("rank_score_threshold", 5),
                    custom_images=self._get_variants_custom_images(
                        variant_category=category, case=case_obj
                    ),
                )

        except (IntegrityError, ValueError, ConfigError, KeyError) as error:
            LOG.warning(error)

        if existing_case:
            self.update_case_data_sharing(old_case=existing_case, new_case=case_obj)
            case_obj["rerun_requested"] = False
            if case_obj["status"] in ["active", "archived"]:
                case_obj["status"] = "inactive"

            case_obj["variants_stats"] = self.case_variants_count(
                case_id=case_obj["_id"],
                institute_id=institute_obj["_id"],
                force_update_case=True,
            )

            self.update_case(case_obj)
            # update Sanger status for the new inserted variants
            self.update_case_sanger_variants(institute_obj, case_obj, old_sanger_variants)

            if keep_actions and old_evaluated_variants:
                self.update_variant_actions(institute_obj, case_obj, old_evaluated_variants)

        else:
            LOG.info("Loading case %s into database", case_obj["display_name"])
            self._add_case(case_obj)

        return case_obj

    def _get_variants_custom_images(
        self, variant_category: str, case: dict
    ) -> Optional[List[dict]]:
        """Retrieve a list of images associated to a variant category.
        supports old cases with case_obj["custom_images"]["str"] key and new cases with key case_obj["custom_images"]["str_variants_images"] key
        """
        if case.get("custom_images"):
            return case["custom_images"].get(f"{variant_category}_variants_images") or case[
                "custom_images"
            ].get(variant_category)

    def _add_case(self, case_obj):
        """Add a case to the database
        If the case already exists exception is raised

         Args:
             case_obj(Case)
        """
        if self.case(case_obj["_id"], projection=ID_PROJECTION):
            raise IntegrityError("Case %s already exists in database" % case_obj["_id"])

        return self.case_collection.insert_one(case_obj)

    def update_case(self, case_obj, keep_date=False):
        """Update a case in the database.
        While updating the case, it compares the date of the latest analysis (case_obj["analysis_date"]) against
        the date of the analysis saved in db (old_case["analysis_date"]). If the 2 dates are different, it creates a new analysis
        containing data from the old analysis under "analyses" in the updated case document.

        The following will be updated:
            - analysis_date: Is updated to the new date
            - cnv_report: path to the CNV report file
            - collaborators: If new collaborators these will be added to the old ones
            - coverage_qc_report: path to the static coverage and qc report file
            - delivery_report: path to the static delivery report file
            - gene_fusion_report: path to the gene fusions report
            - gene_fusion_report_research: path to the research gene fusions report
            - genome_build: If there is a new genome build
            - has_meivariants: If there are new mei variants
            - has_strvariants: If there are new strvariants
            - has_svvariants: If there are new svvariants
            - individuals: There could be new individuals
            - is_research: True is is a research case otherwise False
            - madeline_info: If there is a new pedigree
            - mme_submission: If case was submitted to MatchMaker Exchange
            - multiqc: If there's an updated multiqc report location
            - panels: The new gene panels are added
            - pipeline_version: path to the pipeline executable version report file
            - rank_model_version: If there is a new rank model
            - reference_info: path to the pipeline reference version report file
            - rerun_requested: Is set to False since that is probably what happened
            - research_requested: Boolean, if research variants where requested for this case
            - RNAfusion_inspector: path to the RNA fusion inspector report
            - RNAfusion_inspector_research: path to the research RNA fusion inspector report
            - RNAfusion_report: path to the RNA fusion report
            - RNAfusion_report_research: path to the research RNA fusion report
            - smn_tsv: path to static SMN TSV file
            - status: case status
            - sv_rank_model_version: If there is a new sv rank model
            - track: "rare" or "cancer"
            - updated_at: When the case was updated in the database
            - variants_stats: dict. Number of variants by type
            - vcf_files: paths to the new files

            Args:
                case_obj(dict): The new case information
                keep_date(boolean): The update is small and should not trigger a date change

            Returns:
                updated_case(dict): The updated case information
        """
        LOG.info("Updating case {0}".format(case_obj["_id"]))
        old_case = self.case_collection.find_one({"_id": case_obj["_id"]})

        updated_at = datetime.datetime.now()
        if keep_date:
            updated_at = old_case.get("updated_at")

        # collect already available info from individuals
        old_individuals = old_case.get("individuals")
        for ind in case_obj.get("individuals"):
            for old_ind in old_individuals:
                # if the same individual is present in new case and old case
                if ind["individual_id"] != old_ind["individual_id"]:
                    continue
                # collect user-entered info and save at the individual level in new case_obj
                if ind.get("age") is None:
                    ind["age"] = old_ind.get("age")
                if ind.get("tissue_type") is None:
                    ind["tissue_type"] = old_ind.get("tissue_type")

        analysis_date = case_obj["analysis_date"]
        old_analysis_date = old_case["analysis_date"]
        update_actions = {
            "$addToSet": {"collaborators": {"$each": case_obj["collaborators"]}},
            "$set": {
                "analysis_date": analysis_date,
                "beacon": case_obj.get("beacon"),
                "custom_images": case_obj.get("custom_images"),
                "cnv_report": case_obj.get("cnv_report"),
                "coverage_qc_report": case_obj.get("coverage_qc_report"),
                "delivery_report": case_obj.get("delivery_report"),
                "gene_fusion_report": case_obj.get("gene_fusion_report"),
                "gene_fusion_report_research": case_obj.get("gene_fusion_report_research"),
                "genome_build": case_obj.get("genome_build", "37"),
                "has_meivariants": case_obj.get("has_meivariants"),
                "has_strvariants": case_obj.get("has_strvariants"),
                "has_svvariants": case_obj.get("has_svvariants"),
                "individuals": case_obj["individuals"],
                "is_research": case_obj.get("is_research", False),
                "madeline_info": case_obj.get("madeline_info"),
                "mme_submission": case_obj.get("mme_submission"),
                "multiqc": case_obj.get("multiqc"),
                "multiqc_rna": case_obj.get("multiqc_rna"),
                "panels": case_obj.get("panels", []),
                "phenotype_groups": case_obj.get("phenotype_groups"),
                "phenotype_terms": case_obj.get("phenotype_terms"),
                "pipeline_version": case_obj.get("pipeline_version"),
                "rank_model_version": case_obj.get("rank_model_version"),
                "rerun_requested": case_obj.get("rerun_requested", False),
                "research_requested": case_obj.get("research_requested", False),
                "reference_info": case_obj.get("reference_info"),
                "RNAfusion_inspector": case_obj.get("RNAfusion_inspector"),
                "RNAfusion_inspector_research": case_obj.get("RNAfusion_inspector_research"),
                "RNAfusion_report": case_obj.get("RNAfusion_report"),
                "RNAfusion_report_research": case_obj.get("RNAfusion_report_research"),
                "smn_tsv": case_obj.get("smn_tsv"),
                "status": case_obj.get("status"),
                "sv_rank_model_version": case_obj.get("sv_rank_model_version"),
                "track": case_obj.get("track", "rare"),
                "updated_at": updated_at,
                "variants_stats": case_obj.get("variants_stats"),
                "vcf_files": case_obj.get("vcf_files"),
            },
        }
        analysis_dates = [analysis.get("date") for analysis in old_case.get("analyses", [])]
        if analysis_date != old_analysis_date and old_analysis_date not in analysis_dates:
            update_actions["$addToSet"]["analyses"] = {
                "date": old_analysis_date,
                "delivery_report": old_case.get("delivery_report"),
            }

        updated_case = self.case_collection.find_one_and_update(
            {"_id": case_obj["_id"]},
            update_actions,
            return_document=pymongo.ReturnDocument.AFTER,
        )

        # Remove non-mandatory key/values if they contain a null value
        unset_keys = {}
        for key in [
            "beacon",
            "collaborators",
            "custom_images",
            "cnv_report",
            "coverage_qc_report",
            "delivery_report",
            "family",
            "gene_fusion_report",
            "gene_fusion_report_research",
            "lims_id",
            "mme_submission",
            "multiqc",
            "multiqc_rna",
            "pipeline_version",
            "phenotype_groups",
            "phenotype_terms",
            "pipeline_version",
            "rank_model_version",
            "reference_info",
            "RNAfusion_inspector",
            "RNAfusion_inspector_research",
            "RNAfusion_report",
            "RNAfusion_report_research",
            "smn_tsv",
            "sv_rank_model_version",
        ]:
            if updated_case.get(key):  # Do not remove key if it has a value
                continue
            unset_keys[key] = ""

        if len(unset_keys.keys()) > 0:
            LOG.debug(f"Removing the following unused keys from updated case: {unset_keys.keys()}")
            updated_case = self.case_collection.find_one_and_update(
                {"_id": case_obj["_id"]},
                {"$unset": unset_keys},
                return_document=pymongo.ReturnDocument.AFTER,
            )

        LOG.info("Case updated")
        return updated_case

    def replace_case(self, case_obj):
        """Replace a existing case with a new one

        Keeps the object id

        Args:
            case_obj(dict)

        Returns:
            updated_case(dict)
        """
        LOG.info("Saving case %s", case_obj["_id"])
        # update updated_at of case to "today"

        case_obj["updated_at"] = datetime.datetime.now()

        return self.case_collection.find_one_and_replace(
            {"_id": case_obj["_id"]},
            case_obj,
            return_document=pymongo.ReturnDocument.AFTER,
        )

    def update_caseid(self, case_obj, family_id):
        """Update case id for a case across the database.

        This function is used when a case is a rerun or updated for another reason.

        Args:
            case_obj(dict)
            family_id(str): The new family id

        Returns:
            new_case(dict): The updated case object

        """
        new_case = deepcopy(case_obj)
        new_case["_id"] = family_id

        # update suspects and causatives
        for case_variants in ["suspects", "causatives"]:
            new_variantids = []
            for variant_id in case_obj.get(case_variants, []):
                case_variant = self.variant(variant_id)
                if not case_variant:
                    continue
                new_variantid = get_variantid(case_variant, family_id)
                new_variantids.append(new_variantid)
            new_case[case_variants] = new_variantids

        # update ACMG
        for acmg_obj in self.acmg_collection.find({"case_id": case_obj["_id"]}):
            LOG.info("update ACMG classification: %s", acmg_obj["classification"])
            acmg_variant = self.variant(acmg_obj["variant_specific"])
            new_specific_id = get_variantid(acmg_variant, family_id)
            self.acmg_collection.find_one_and_update(
                {"_id": acmg_obj["_id"]},
                {"$set": {"case_id": family_id, "variant_specific": new_specific_id}},
            )

        # update events
        institute_obj = self.institute(case_obj["owner"])
        for event_obj in self.events(institute_obj, case=case_obj):
            LOG.info("update event: %s", event_obj["verb"])
            self.event_collection.find_one_and_update(
                {"_id": event_obj["_id"]}, {"$set": {"case": family_id}}
            )

        # insert the updated case
        self.case_collection.insert_one(new_case)
        # delete the old case
        self.case_collection.find_one_and_delete({"_id": case_obj["_id"]})
        return new_case

    def case_sanger_variants(self, case_id):
        """Get all variants with verification ordered or
            already verified for a case.

        Accepts:
            case_id(str): a case _id

        Returns:
            case_verif_variants(dict): a dictionary like this: {
                'sanger_verified' : [list of vars],
                'sanger_ordered' : [list of vars]
            }
        """
        case_verif_variants = {"sanger_verified": [], "sanger_ordered": []}

        # Add the verified variants
        results = {
            "sanger_verified": self.validated(case_id=case_id),
            "sanger_ordered": self.sanger_ordered(case_id=case_id),
        }

        for category in results:
            res = results[category]
            if not res:
                continue
            for var_id in res[0]["vars"]:
                variant_obj = self.variant(case_id=case_id, document_id=var_id)
                if not variant_obj:
                    continue
                case_verif_variants[category].append(variant_obj)

        LOG.info(
            "Nr variants with sanger verification found: %s",
            len(case_verif_variants["sanger_verified"]),
        )
        LOG.info(
            "Nr variants with sanger ordered found: %s",
            len(case_verif_variants["sanger_ordered"]),
        )

        return case_verif_variants

    def update_variant_actions(self, institute_obj, case_obj, old_eval_variants):
        """Update existing variants of a case according to the tagged status
            (manual_rank, dismiss_variant, mosaic_tags) of its previous variants

        Accepts:
            institute_obj(dict): an institute object
            case_obj(dict): a case object
            old_eval_variants(list(Variant))

        Returns:
            updated_variants(dict): a dictionary like this:
                'manual_rank' : [list of variant ids],
                'dismiss_variant' : [list of variant ids],
                'mosaic_tags' : [list of variant ids],
                'cancer_tier': [list of variant ids],
                'acmg_classification': [list of variant ids]
                'is_commented': [list of variant ids]
        """
        updated_variants = {
            "manual_rank": [],
            "dismiss_variant": [],
            "mosaic_tags": [],
            "cancer_tier": [],
            "acmg_classification": [],
            "is_commented": [],
        }

        update_action_map = {
            "manual_rank": self.update_manual_rank,
            "dismiss_variant": self.update_dismiss_variant,
            "mosaic_tags": self.update_mosaic_tags,
            "cancer_tier": self.update_cancer_tier,
        }

        LOG.debug(
            "Updating action status for {} variants in case:{}".format(
                len(old_eval_variants), case_obj["_id"]
            )
        )

        n_status_updated = 0
        for old_var in old_eval_variants:
            # search for the same variant in newly uploaded vars for this case
            display_name = old_var["display_name"]

            new_var = self.variant_collection.find_one(
                {"case_id": case_obj["_id"], "display_name": display_name}
            )

            if new_var is None:  # same var is no more among case variants, skip it
                LOG.warning(
                    "Trying to propagate manual action from an old variant to a new, but couldn't find same variant any more"
                )
                continue

            for action in list(
                updated_variants.keys()
            ):  # manual_rank, dismiss_variant, mosaic_tags
                # collect only the latest associated event:
                if (
                    old_var.get(action) is None and action != "is_commented"
                ):  # tag new variant accordingly
                    continue
                verb = action
                if action == "acmg_classification":
                    verb = "acmg"
                elif action == "is_commented":
                    verb = "comment"

                old_event = self.event_collection.find_one(
                    {
                        "case": case_obj["_id"],
                        "verb": verb,
                        "variant_id": old_var["variant_id"],
                        "category": "variant",
                    },
                    sort=[("updated_at", pymongo.DESCENDING)],
                )

                if old_event is None:
                    continue

                user_obj = self.user(old_event["user_id"])
                if user_obj is None:
                    continue

                updated_variant = None

                if action == "is_commented":
                    updated_comments = self.comments_reupload(
                        old_var, new_var, institute_obj, case_obj
                    )
                    if updated_comments > 0:
                        LOG.info(
                            "Created {} new comments for variant {} after reupload".format(
                                updated_comments, display_name
                            )
                        )
                        updated_variant = new_var

                # create a link to the new variant for the events
                link = "/{0}/{1}/{2}".format(
                    new_var["institute"], case_obj["display_name"], new_var["_id"]
                )

                if action == "acmg_classification":
                    str_classif = ACMG_MAP.get(old_var.get("acmg_classification"))
                    updated_variant = self.update_acmg(
                        institute_obj=institute_obj,
                        case_obj=case_obj,
                        user_obj=user_obj,
                        link=link,
                        variant_obj=new_var,
                        acmg_str=str_classif,
                    )

                if action in update_action_map.keys():
                    updated_variant = update_action_map[action](
                        institute_obj,
                        case_obj,
                        user_obj,
                        link,
                        new_var,
                        old_var.get(action),
                    )

                if updated_variant is not None:
                    n_status_updated += 1
                    updated_variants[action].append(updated_variant["_id"])

        LOG.info("Variant actions updated {} times".format(n_status_updated))
        return updated_variants

    def update_case_sanger_variants(self, institute_obj, case_obj, case_verif_variants):
        """Update existing variants for a case according to a previous
        verification status.

        Accepts:
            institute_obj(dict): an institute object
            case_obj(dict): a case object

        Returns:
            updated_variants(dict): a dictionary like this: {
                'updated_verified' : [list of variant ids],
                'updated_ordered' : [list of variant ids]
            }

        """
        LOG.debug("Updating verification status for variants in case:{}".format(case_obj["_id"]))

        updated_variants = {"updated_verified": [], "updated_ordered": []}
        # update verification status for verified variants of a case
        for category in case_verif_variants:
            variants = case_verif_variants[category]
            verb = "sanger"
            if category == "sanger_verified":
                verb = "validate"

            for old_var in variants:
                # new var display name should be the same as old display name:
                display_name = old_var["display_name"]
                # check if variant still exists
                new_var = self.variant_collection.find_one(
                    {"case_id": case_obj["_id"], "display_name": display_name}
                )

                if new_var is None:  # if variant doesn't exist any more
                    continue

                # create a link to the new variant for the events
                link = "/{0}/{1}/{2}".format(
                    new_var["institute"], case_obj["display_name"], new_var["_id"]
                )

                old_event = self.event_collection.find_one(
                    {
                        "case": case_obj["_id"],
                        "verb": verb,
                        "variant_id": old_var["variant_id"],
                    }
                )

                if old_event is None:
                    continue

                user_obj = self.user(old_event["user_id"])

                if category == "sanger_verified":
                    # if a new variant coresponds to the old and
                    # there exist a verification event for the old one
                    # validate new variant as well:
                    updated_var = self.validate(
                        institute=institute_obj,
                        case=case_obj,
                        user=user_obj,
                        link=link,
                        variant=new_var,
                        validate_type=old_var.get("validation"),
                    )
                    if updated_var:
                        updated_variants["updated_verified"].append(updated_var["_id"])

                else:
                    # old variant had Sanger validation ordered
                    # check old event to collect user_obj that ordered the verification:
                    # set sanger ordered status for the new variant as well:
                    updated_var = self.order_verification(
                        institute=institute_obj,
                        case=case_obj,
                        user=user_obj,
                        link=link,
                        variant=new_var,
                    )
                    if updated_var:
                        updated_variants["updated_ordered"].append(updated_var["_id"])

        n_status_updated = len(updated_variants["updated_verified"]) + len(
            updated_variants["updated_ordered"]
        )
        LOG.info("Verification status updated for {} variants".format(n_status_updated))
        return updated_variants


def get_variantid(variant_obj, family_id):
    """Create a new variant id.

    Args:
        variant_obj(dict)
        family_id(str)

    Returns:
        new_id(str): The new variant id
    """
    new_id = parse_document_id(
        chrom=variant_obj["chromosome"],
        pos=str(variant_obj["position"]),
        ref=variant_obj["reference"],
        alt=variant_obj["alternative"],
        variant_type=variant_obj["variant_type"],
        case_id=family_id,
    )
    return new_id
