import logging

from scout.utils.acmg import get_acmg
from scout.build.acmg import build_evaluation

log = logging.getLogger(__name__)

class ACMGHandler(object):

    def submit_evaluation(self, variant_obj, user_obj, institute_obj, case_obj, link, criterias):
        """Submit an evaluation to the database
        
        Get all the relevant information, build a evaluation_obj
        
        Args:
            variant_obj(dict)
            user_obj(dict)
            institute_obj(dict)
            case_obj(dict)
            link(str): variant url
            criterias(list(dict)):
        
                [
            {
            'term': str,
            'comment': str,
            'links': list(str)
            },
            .
            .
        ]
        """
        variant_specific = variant_obj['_id']
        variant_id = variant_obj['variant_id']
        user_id = user_obj['_id']
        user_name = user_obj.get('name', user_obj['_id'])
        institute_id = institute_obj['_id']
        case_id = case_obj['_id']
        
        evaluation_terms = [evluation_info['term'] for evluation_info in criterias]
        
        classification = get_acmg(evaluation_terms)
        
        evaluation_obj = build_evaluation(
            variant_specific, variant_id, user_id, user_name, institute_id,
            case_id, criterias
        )
    
        self._load_evaluation(evaluation_obj)
        
        # Update the acmg classification for the variant:
        self.update_acmg(institute_obj, case_obj, user_obj, link, variant_obj, classification)
        

    def _load_evaluation(self, evaluation_obj):
        """Load a evaluation object into the database"""
        res = self.acmg_collection.insert_one(evaluation_obj)
        return res
        
    def get_evaluations(self, variant_specific, variant_id):
        """Return all evaluations for a certain variant
        
        Args:
            variant_specific(str): _id for a variant
            variant_id(str): md5 string for a variant
        
        Returns:
            res(pymongo.cursor)
        """
        query = {}
        if variant_specific:
            query['variant_specific'] = variant_specific
        elif variant_id:
            query['variant_id'] = variant_id
        else:
            raise SyntaxError("Either variant specific or variant id has to be specified")

        res = self.acmg_collection.find(query)
        
        return res