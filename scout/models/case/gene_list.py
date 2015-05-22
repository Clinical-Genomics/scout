from mongoengine import (EmbeddedDocument, StringField, FloatField)

class GeneList(EmbeddedDocument):
  list_id = StringField(required=True)
  version = FloatField(required=True)
  date = StringField(required=True)
  display_name = StringField()

  def __repr__(self):
    return "GeneList(list_id={0}, version={1}, date={2}, display_name={3})".format(
      self.list_id, self.version, self.date, self.display_name
    )
