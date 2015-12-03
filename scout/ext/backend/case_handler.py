import os
import logging
import codecs

from path import path
from datetime import datetime
from mongoengine import DoesNotExist, Q

from ped_parser import FamilyParser
from scout.models import (Case, Individual, Institute)
from scout.ext.backend.utils.get_gene_lists import get_gene_lists

logger = logging.getLogger(__name__)


class CaseHandler(object):
    """Part of the mongo adapter that handles cases and institutes"""
    
    def add_institute(self, internal_id, display_name):
        """Add a institute to the database
        
            Args:
                internal_id(str): The internal id (like cust003)
                display_name(str): The display name for a institute (like CMMS)
        """
        logger.info("Creating institute with internal_id: {0} and"\
                    " display_name: {1}".format(internal_id, display_name))
        institute = Institute(
            internal_id=internal_id,
            display_name=display_name
        )
        institute.save()
        ##TODO create event for doing this?
    
    def update_institute(self, internal_id, sanger_recipient=None, 
                            coverage_cutoff=None):
        """Update the information for an institute
        
            Args:
                internal_id(str): The internal institute id
                sanger_recipient(str): Email adress for ordering sanger
                coverage_cutoff(int): Update coverage cutoff
        """
        institute = self.institute(internal_id)
        if institute:
            if sanger_recipient:
                logger.info("Updating sanger recipients for institute"\
                            " {0} with {1}".format(
                                internal_id, sanger_recipient))
                institute.sanger_recipients.append(sanger_recipient)
            if coverage_cutoff:
                logger.info("Updating coverage cutoff for institute"\
                            " {0} with {1}".format(
                                internal_id, coverage_cutoff))
                institute.coverage_cutoff = coverage_cutoff
            institute.save()
        ##TODO create event?
    
    def institute(self, internal_id):
        """Featch a single institute from the backend
        
            Args:
                internal_id(str)
            
            Returns:
                Institute object
        """
        logger.info("Fetch institute {}".format(
            internal_id))
        try:
            return Institute.objects.get(internal_id=internal_id)
        except DoesNotExist:
            logger.warning("Could not find institute {0}".format(internal_id))
            return None
        
    def cases(self, collaborator=None, query=None):
        """Fetches all cases from the backend.

        Args:
            collaborator(str): If collaborator should be considered
            query(dict): If a specific query is used
        
        Yields:
            Cases ordered by date
        """
        logger.info("Fetch all cases")
        if collaborator:
            logger.info("Use collaborator {0}".format(collaborator))
            case_query = Case.objects(collaborators=collaborator)
        else:
            case_query = Case.objects

            if query:
                # filter cases by matching display name of case or individuals
                case_query = case_query.filter(Q(display_name__contains=query) |
                Q(individuals__display_name__contains=query))

        return case_query.order_by('-updated_at')

    def case(self, institute_id, case_id):
        """Fetches a single case from database

        Args:
            institute_id(str)
            case_id(str)

        Yields:
            A single Case
        """
        
        logger.info("Fetch case {0} from institute {1}".format(
            case_id, institute_id))
        try:
            return Case.objects.get(
                collaborators__contains=institute_id,
                display_name=case_id
            )
        except DoesNotExist:
            logger.warning("Could not find case {0}".format(case_id))
            return None
    
    def delete_case(self, institute_id, case_id):
        """Delete a single case from database

        Args:
            institute_id(str)
            case_id(str)

        """
        logger.info("Fetch case {0} from institute {1}".format(
            case_id, institute_id))
        try:
            case = Case.objects.get(
                collaborators__contains=institute_id,
                display_name=case_id
            )
            logger.info("Deleting case {0}".format(case.case_id))
            case.delete()
            logger.debug("Case deleted")
            ##TODO Add event for deleting case?
            
        except DoesNotExist:
            logger.warning("Could not find case {0}".format(case_id))
    
    def add_case(self, case_lines, case_type, owner, scout_configs={}):
        """Add a case to the database

            If case exists in database it will be updated.
            This method will take information in a ped like format and create 
            a case object. If the case is already in database it will update 
            the necessary information.
            
            Args:
                case_lines(Iterator): An iterator with the pedigree infromation
                case_type(str): The format of the case lines
                owner(str): The institute id for owner of the case
        """
        logger.info("Setting up a family parser")
        case_parser = FamilyParser(case_lines,
                                   family_type=case_type)

        if len(case_parser.families) != 1:
            raise SyntaxError("Only one case per ped file is allowed")
        
        case_id = list(case_parser.families.keys())[0]
        logger.info("Found case {0}".format(case_id))
        
        logger.info("Creating Case with id {0}".format(
            '_'.join([owner, case_id])))

        case = Case(
            case_id='_'.join([owner, case_id]),
            display_name=case_id,
            owner=owner,
        )
        
        collaborators = scout_configs.get('collaborators') or set()
        if collaborators:
            if isinstance(collaborators, list):
                collaborators = set(collaborators)
            else:
                collaborators = set([collaborators])

        collaborators.add(owner)

        case['collaborators'] = list(collaborators)
        logger.debug("Setting collaborators to: {0}".format(
          ', '.join(collaborators)))
        
        analysis_type = scout_configs.get('analysis_type', 'unknown').lower()
        case['analysis_type'] = analysis_type
        logger.debug("Setting analysis type to: {0}".format(analysis_type))
        
        # Get the path of vcf from configs
        vcf = scout_configs.get('igv_vcf', '')
        case['vcf_file'] = vcf
        logger.debug("Setting igv vcf file to: {0}".format(vcf))
        
        # Add the genome build information
        genome_build = scout_configs.get('human_genome_build', '')
        case['genome_build'] = genome_build
        logger.debug("Setting genome build to: {0}".format(genome_build))
        
        # Get the genome version
        genome_version = float(scout_configs.get('human_genome_version', '0'))
        case['genome_version'] = genome_version
        logger.debug("Setting genome version to: {0}".format(genome_version))
        
        # Add the rank model version
        rank_model_version = scout_configs.get('rank_model_version', '')
        case['rank_model_version'] = rank_model_version
        logger.debug("Setting rank model version to: {0}".format(
              rank_model_version))
        
        # Check the analysis date
        analysis_date = scout_configs.get('analysis_date', '')
        case['analysis_date'] = analysis_date
        logger.debug("Setting analysis date to: {0}".format(analysis_date))
        
        # Add the pedigree picture, this is a xml file that will be read and
        # saved in the mongo database
        madeline_path = path(scout_configs.get('madeline', '/__menoexist.tXt'))
        if madeline_path.exists():
            logger.debug("Found madeline info")
            with madeline_path.open('r') as handle:
                case['madeline_info'] = handle.read()
                logger.debug("Madeline file was read succesfully")
        else:
            logger.info("No madeline file found. Skipping madeline file.")

        # Add the coverage report
        coverage_report_path = path(scout_configs.get('coverage_report', '/__menoexist.tXt'))
        if coverage_report_path.exists():
            logger.debug("Found a coverage report")
            with coverage_report_path.open('rb') as handle:
                case['coverage_report'] = handle.read()
                logger.debug("Coverage was read succesfully")
        else:
            logger.info("No coverage report found. Skipping coverage report.")
        
        individuals = []
        # Add the individuals
        for ind_id in case_parser.individuals:
            ped_individual = case_parser.individuals[ind_id]
            individual = Individual(
                individual_id = ind_id,
                father = ped_individual.father,
                mother = ped_individual.mother,
                display_name = ped_individual.extra_info.get(
                                    'display_name', ind_id),
                sex = str(ped_individual.sex),
                phenotype = ped_individual.phenotype,
            )
            # Path to the bam file for IGV:
            individual['bam_file'] = scout_configs.get(
                'individuals',{}).get(
                    ind_id, {}).get(
                        'bam_path', '')
            
            individual['capture_kits'] = scout_configs.get(
                'individuals',{}).get(
                    ind_id, {}).get(
                        'capture_kit', [])
            #Add affected individuals first
            if ped_individual.affected:
                logger.info("Adding individual {0} to case {1}".format(
                    ind_id, case_id))
                case.individuals.append(individual)
            else:
                individuals.append(individual)
        
        for individual in individuals:
            logger.info("Adding individual {0} to case {1}".format(
                    individual.individual_id, case_id))
            case.individuals.append(individual)
        
        clinical_panels = []
        research_panels = []
        
        for gene_list in scout_configs.get('gene_lists', {}):
            logger.info("Found gene list {0}".format(gene_list))
            list_info = scout_configs['gene_lists'][gene_list]

            list_path = list_info.get('file')
            list_type = list_info.get('type', 'clinical')
            
            if os.path.isfile(list_path):
                with codecs.open(list_path, 'r') as list_lines:
                    panels = get_gene_lists(list_lines, owner)

                for panel in panels:
                    logger.info("Store gene panel {0} in database".format(
                        panel.panel_name))
                    panel.save()
                    if list_type == 'clinical':
                        logger.info("Adding {0} to clinical gene lists".format(
                            panel.panel_name))
                        clinical_panels.append(panel)
                    else:
                        logger.info("Adding {0} to research gene lists".format(
                            panel.panel_name))
                        research_panels.append(panel)

        case['clinical_panels'] = clinical_panels
        case['research_panels'] = research_panels
        
        default_panels = scout_configs.get('default_panels', [])
        logger.info("Adding {0} as default panels to case {1}".format(
            ', '.join(default_panels), case_id))
        case['default_panels'] = list(default_panels)
        
        #If the case exists we need tu update the information
        if self.case(institute_id=owner, case_id=case_id):
            self.update_case(case)
        else:
            logger.info("Adding case {0} to database".format(case_id))
            case.save()
        
        return case
    
    def update_case(self, case):
        """Update a case in the database
        
            Args:
                case(Case): The new case information
        """
        logger.info("Updating case {0}".format(case.case_id))
        existing_case = self.case(
            institute_id=case.owner, 
            case_id=case.display_name
        )
        case['collaborators'] = list(set(case['collaborators'] + existing_case.collaborators))
        logger.debug("Updating collaborators to {0}".format(
            case['collaborators']))
        logger.debug("Updating is_research to {0}".format(
            existing_case.is_research))
        case['is_research'] = existing_case['is_research']
        logger.debug("Updating created_at to {0}".format(
            existing_case['created_at']))
        case['created_at'] = existing_case['created_at']
        
        logger.info("Deleting old case {0}".format(
            existing_case['case_id']))
        existing_case.delete()
        
        ##TODO Add event for updating case?
        
        logger.info("Saving updated case {0}".format(
            case['case_id']))
        
        case.save()
        