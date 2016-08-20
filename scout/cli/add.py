# -*- coding: utf-8 -*-
from datetime import datetime
import logging

from ped_parser import FamilyParser

from scout.models import Case, Individual, GenePanel
from scout.exc import MadelineIncompatibleError
from .madeline import make_svg

log = logging.getLogger(__name__)


def new_info(old_case, new_case):
    """Compare a new case with what is already in the database."""
    if new_case.analysis_dates[-1] > old_case.analysis_dates[-1]:
        return False
    elif new_case.variant_type == 'research' and not old_case.is_research:
        return False
    return True


def add_case(adapter, sampleinfo, ped_stream, vcf_path, variant_type,
             madeline_exe, variants=5000, threshold=0):
    """Do all that is necessary to add a case."""
    new_case = parse_mip(sampleinfo, ped_stream, vcf_path,
                         madeline_exe=madeline_exe)
    new_case.variant_type = variant_type
    old_case = adapter.case(new_case.owner, new_case.case_id)
    has_new_info = new_info(old_case, new_case)
    if old_case and has_new_info:
        update_case(old_case, new_case)
        old_case.save()
        current_case = old_case
        log.info("updated existing case: %s", old_case.case_id)
    elif old_case is None:
        new_case.save()
        current_case = new_case
        log.info("saved new case: %s", new_case.case_id)

    if old_case is None or has_new_info:
        log.debug("load variants for case {}".format(current_case.case_id))
        adapter.add_variants(
            vcf_file=vcf_path, variant_type=variant_type, case=current_case,
            variant_number_treshold=variants,
            rank_score_threshold=threshold
        )


def parse_mip(sampleinfo, ped_stream, vcf_path, madeline_exe=None):
    """Parse MIP output to load into Scout."""
    ped_family = FamilyParser(ped_stream, family_type='cmms')
    si_data = parse_sampleinfo(sampleinfo)
    new_individuals, default_panels = parse_ped(ped_family)
    try:
        madeline_str = make_svg(ped_family, si_data['name'],
                                madeline_exe=madeline_exe)
    except MadelineIncompatibleError:
        madeline_str = None

    new_case = build_case(individuals=new_individuals,
                          default_panels=default_panels,
                          vcf_file=vcf_path,
                          madeline=madeline_str,
                          **si_data)
    return new_case


def build_case(case_id, name, owner, individuals, analysis_type, analyzed_at,
               clinical_panels=None, research_panels=None, default_panels=None,
               collaborators=None, genome_build=None, genome_version=None,
               rank_model=None, madeline=None, vcf_file=None):
    """Add a new case document."""
    new_case = Case(
        case_id=case_id,
        display_name=name,
        owner=owner,
        genome_build=genome_build,
        genome_version=genome_version,
        analysis_type=analysis_type,
        rank_model_version=rank_model,
        clinical_panels=clinical_panels if clinical_panels else [],
        research_panels=research_panels if research_panels else [],
        default_panels=default_panels if default_panels else [],
        vcf_file=vcf_file,
        madeline_info=madeline,
    )

    for individual in individuals:
        new_case.individuals.append(individual)

    for institute in (collaborators or []):
        new_case.collaborators.append(institute.internal_id)

    new_case.analysis_dates.append(analyzed_at)
    return new_case


def parse_ped(ped_family, bam_map=None):
    """Parse information about individuals from a PED file."""
    if len(ped_family.families) > 1:
        raise SyntaxError("PED file with multiple families")
    individuals = ped_family.individuals.values()
    new_individuals = [parse_individual(individual) for individual in
                       individuals]
    gene_panels = parse_genepanels(individuals)
    return new_individuals, gene_panels


def parse_individual(individual):
    """Parse a ped_parse.Individual to Individual record."""
    display_name = individual.extra_info.get('display_name')
    new_ind = Individual(
        individual_id=individual.individual_id,
        father=None if individual.father == '0' else individual.father,
        mother=None if individual.mother == '0' else individual.mother,
        display_name=display_name,
        sex=str(individual.sex),
        phenotype=individual.phenotype,
    )
    capture_kit = individual.extra_info.get('Capture_kit')
    if capture_kit:
        new_ind.capture_kits.append(capture_kit)
    return new_ind


def parse_genepanels(individuals):
    """Parse out consensus gene panels."""
    all_panels = set()
    for individual in individuals:
        raw_panels = individual.extra_info.get('Clinical_db')
        if raw_panels:
            for panel_id in raw_panels.split(';'):
                all_panels.add(panel_id)
    return list(all_panels)


def parse_sampleinfo(data):
    """Parse QC sampleinfo file and extract information."""
    fam_key = data.keys()[0]
    fam_data = data[fam_key][fam_key]
    owner = fam_data['InstanceTag'][0]
    case_id = "{}-{}".format(owner, fam_key)
    raw_genepanels = fam_data['VCFParser']['SelectFile']['Database'].values()
    gene_panels = [parse_genepanel(raw_panel, owner) for raw_panel in
                   raw_genepanels]
    raw_researchpanels = fam_data['VCFParser']['RangeFile']['Database'].values()
    research_panels = [parse_genepanel(raw_panel, owner) for raw_panel in
                       raw_researchpanels]
    rank_model = fam_data['Program']['RankVariants']['RankModel']['Version']
    return_data = {
        'owner': owner,
        'name': fam_key,
        'case_id': case_id,
        'analyzed_at': fam_data['AnalysisDate'],
        'analysis_type': fam_data['AnalysisType'],
        'clinical_panels': gene_panels,
        'research_panels': research_panels,
        'genome_build': fam_data['HumanGenomeBuild']['Source'],
        'genome_version': fam_data['HumanGenomeBuild']['Version'],
        'rank_model': rank_model,
    }
    return return_data


def parse_genepanel(panel_data, owner):
    """Parse gene list data."""
    new_panel = GenePanel(
        panel_name=panel_data['Acronym'],
        display_name=panel_data['CompleteName'],
        version=panel_data['Version'],
        date=str(panel_data['Date']),
        institute=owner,
    )
    return new_panel


def update_case(old_case, new_case):
    """Update an existing case with (possibly) new information."""
    old_case.display_name = new_case.display_name
    old_case.updated_at = datetime.now()
    old_case.individuals = new_case.individuals
    old_case.analysis_date = new_case.analysis_date
    old_case.analysis_dates.append(new_case.analysis_dates[0])
    old_case.rank_model_version = new_case.rank_model_version
    old_case.analysis_type = new_case.analysis_type
    old_case.madeline_info = new_case.madeline_info
    old_case.vcf_file = new_case.vcf_file
    old_case.default_panels = new_case.default_panels

    for panel in old_case.clinical_panels:
        panel.delete()
    for panel in old_case.research_panels:
        panel.delete()
    old_case.clinical_panels = new_case.clinical_panels
    old_case.research_panels = new_case.research_panels
