from mongoengine import (EmbeddedDocument, StringField, FloatField)

class PhenotypeTerm(EmbeddedDocument):
  hpo_id = StringField()
  feature = StringField()

  def __repr__(self):
    return "PhenotypeTerm(hpo_id={0}, feature={1})".format(
      self.hpo_id, self.feature
    )


class GeneList(EmbeddedDocument):
  list_id = StringField(required=True)
  version = FloatField(required=True)
  date = StringField(required=True)
  display_name = StringField()

  def __repr__(self):
    return "GeneList(list_id={0}, version={1}, date={2}, display_name={3})".format(
      self.list_id, self.version, self.date, self.display_name
    )
