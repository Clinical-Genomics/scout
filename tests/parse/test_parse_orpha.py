from xml.etree.ElementTree import fromstring

from scout.parse.orpha import (
    get_orpha_diseases_product6,
)


def test_get_orpha_diseases_product6():
    # GIVEN a xml-tree
    tree = fromstring(
        """
     <Disorder id="183">
      <OrphaCode>637</OrphaCode>
      <ExpertLink lang="en">http://www.orpha.net/consor/cgi-bin/OC_Exp.php?lng=en&amp;Expert=637</ExpertLink>
      <Name lang="en">Full NF2-related schwannomatosis</Name>
      <DisorderType id="21394">
        <Name lang="en">Disease</Name>
      </DisorderType>
      <DisorderGroup id="36547">
        <Name lang="en">Disorder</Name>
      </DisorderGroup>
      <DisorderGeneAssociationList count="1">
        <DisorderGeneAssociation>
          <SourceOfValidation>20301380[PMID]</SourceOfValidation>
          <Gene id="16543">
            <Name lang="en">NF2, moesin-ezrin-radixin like (MERLIN) tumor suppressor</Name>
            <Symbol>NF2</Symbol>
            <SynonymList count="3">
              <Synonym lang="en">ACN</Synonym>
              <Synonym lang="en">BANF</Synonym>
              <Synonym lang="en">SCH</Synonym>
            </SynonymList>
            <GeneType id="25993">
              <Name lang="en">gene with protein product</Name>
            </GeneType>
            <ExternalReferenceList count="3">
              <ExternalReference id="31793">
                <Source>Genatlas</Source>
                <Reference>NF2</Reference>
              </ExternalReference>
              <ExternalReference id="31791">
                <Source>HGNC</Source>
                <Reference>7773</Reference>
              </ExternalReference>
              <ExternalReference id="31790">
                <Source>OMIM</Source>
                <Reference>607379</Reference>
              </ExternalReference>
            </ExternalReferenceList>
            <LocusList count="1">
              <Locus id="16727">
                <GeneLocus>22q12.2</GeneLocus>
                <LocusKey>1</LocusKey>
              </Locus>
            </LocusList>
          </Gene>
          <DisorderGeneAssociationType id="17949">
            <Name lang="en">Disease-causing germline mutation(s) in</Name>
          </DisorderGeneAssociationType>
          <DisorderGeneAssociationStatus id="17991">
            <Name lang="en">Assessed</Name>
          </DisorderGeneAssociationStatus>
        </DisorderGeneAssociation>
      </DisorderGeneAssociationList>
    </Disorder>"""
    )

    # WHEN parsing the tree
    result = get_orpha_diseases_product6(tree)
    disease = result["ORPHA:637"]

    # THEN assert disease with correct contents was returned
    assert len(result) == 1
    assert disease["description"] == "Full NF2-related schwannomatosis"
    assert disease["orpha_code"] == 637
    assert disease["hgnc_ids"] == {"7773"}
