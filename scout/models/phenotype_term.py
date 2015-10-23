# -*- coding: utf-8 -*-
from mongoengine import (EmbeddedDocument, StringField, ListField)


class PhenotypeTerm(EmbeddedDocument):
  phenotype_id = StringField()
  feature = StringField()
  disease_models = ListField(StringField())

  @property
  def hpo_link(self):
      """Return a HPO link."""
      return ("http://compbio.charite.de/hpoweb/showterm?id={}"
              .format(self.phenotype_id))

  @property
  def omim_link(self):
    """Return a OMIM phenotype link."""
    return "http://www.omim.org/entry/{}".format(self.phenotype_id)

  def __repr__(self):
    return "PhenotypeTerm(phenotype_id={0}, feature={1}, "\
            "disease_models={2})".format(
              self.phenotype_id, self.feature, self.disease_models
              )

