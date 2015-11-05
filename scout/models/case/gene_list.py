from mongoengine import (Document,ListField, StringField, FloatField)

class GenePanel(Document):
  institute = StringField(required=True)
  panel_name = StringField(required=True)
  version = FloatField(required=True)
  date = StringField(required=True)
  display_name = StringField()
  genes = ListField(StringField)

  def __repr__(self):
    return "GeneList(list_id={0}, version={1}, date={2}, display_name={3})".format(
      self.list_id, self.version, self.date, self.display_name
    )
