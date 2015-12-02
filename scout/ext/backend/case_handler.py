import logging

from path import path
from mongoengine import DoesNotExist, Q

from ped_parser import FamilyParser
from scout.models import (Case, Individual, Institute)

logger = logging.getLogger(__name__)


class CaseHandler(object):
    """Part of the mongo adapter that handles cases"""
    
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
        
        if self.case(institute_id=owner, case_id=case_id):
            self.update_case(case)
        else:
            logger.info("Adding case {0} to database".format(case_id))
            case.save()
    
    def update_case(self, case):
        """Update a case in the database"""
        pass
    
    def add_institute(self, internal_id, display_name):
        """docstring for add_institute"""
    pass
    