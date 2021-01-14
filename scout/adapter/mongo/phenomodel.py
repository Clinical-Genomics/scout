# -*- coding: utf-8 -*-
import datetime
import pymongo
from bson import ObjectId


class PhenoModelHandler(object):
    """Class handling phenomodels creation and use"""

    def phenomodels(self, institute_id):
        """Return all phenopanels for a given institute
        Args:
            institute_id(str): institute id
        Returns:
            phenotype_models(pymongo.cursor.Cursor)
        """
        query = {"institute": institute_id}
        phenotype_models = self.phenomodel_collection.find(query)
        return phenotype_models

    def create_phenomodel(self, institute_id, name, description):
        """Create an empty advanced phenotype model with data provided by a user
        Args:
            institute_id(str): institute id
            name(str) a model name
            description(str) a model description
        Returns:
            phenomodel_obj(dict) a newly created model
        """
        phenomodel_obj = dict(
            institute=institute_id,
            name=name,
            description=description,
            subpanels={},
            created=datetime.datetime.now(),
            updated=datetime.datetime.now(),
        )
        phenomodel_obj = self.phenomodel_collection.insert_one(phenomodel_obj)
        return phenomodel_obj

    def update_phenomodel(self, model_id, model_obj):
        """Update a phenotype model using its ObjectId
        Args:
            model_id(str): document ObjectId string id
            model_obj(dict): a dictionary of key/values to update a phenomodel with

        Returns:
            updated_model(dict): the phenomodel document after the update
        """
        updated_model = self.phenomodel_collection.find_one_and_update(
            {"_id": ObjectId(model_id)},
            {
                "$set": {
                    "name": model_obj["name"],
                    "description": model_obj["description"],
                    "subpanels": model_obj.get("subpanels", {}),
                    "updated": datetime.datetime.now(),
                    "admins": model_obj.get("admins", []),
                }
            },
            return_document=pymongo.ReturnDocument.AFTER,
        )
        return updated_model

    def phenomodel(self, model_id):
        """Retrieve a phenomodel object using its ObjectId
        Args:
            model_id(ObjectId): document ObjectId
        Returns
            model_obj(dict)
        """
        query = {"_id": ObjectId(model_id)}
        model_obj = self.phenomodel_collection.find_one(query)
        return model_obj
