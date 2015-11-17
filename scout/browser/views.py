# -*- coding: utf-8 -*-
from flask import abort, Blueprint, jsonify, redirect, request

from ..extensions import store
from ..range import send_file_partial

browser = Blueprint('browser', __name__, template_folder='templates')


@browser.route('/remote/static', methods=['OPTIONS', 'GET'])
def remote_static():
  """Stream *large* static files with special requirements."""
  file_path = request.args.get('file')

  range_header = request.headers.get('Range', None)
  if not range_header and file_path.endswith('.bam'):
    return abort(500)

  new_resp = send_file_partial(file_path)
  return new_resp


@browser.route('/<institute_id>/<case_id>/<variant_id>/igv.xml')
def igv_init(institute_id, case_id, variant_id):
  """Redicect user to start an IGV session based on a variant."""
  case_model = store.case(institute_id, case_id)
  variant = store.variant(document_id=variant_id)

  # sanity check to see if there's any reason to launch IGV
  #if variant is None:
  #  return jsonify(error='Variant not found'), 406

  # figure out where the variant/indel ends
  #variant_end = variant.position + len(variant.alternative) - 1

  # compose URL
  #igv_url = build_igv_url(variant.chromosome, variant.position, variant_end,
  #                        case.vcf_file, case.bam_files)

  sessionXml ="""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
  <Session genome="hg19" hasGeneTrack="true" hasSequenceTrack="true" locus="{chr}:{start_bp}-{stop_bp}" version="8">
      <Resources>
          <Resource path="http://localhost:5000/remote/static/home/vagrant/pybamview/examples/example_2sample.sorted.bam"/>
          <Resource path="http://localhost:5000/remote/static/vagrant/tests/vcf_examples/1/1_500.selected.vcf"/>
      </Resources>
      <Panel height="96" name="DataPanel" width="1131">
          <Track SQUISHED_ROW_HEIGHT="4" altColor="0,0,178" autoScale="false" clazz="org.broad.igv.track.FeatureTrack" color="0,0,178" colorMode="GENOTYPE" displayMode="EXPANDED" featureVisibilityWindow="1994000" fontSize="10" id="http://localhost:5000/api/v1/static/99_sorted_pmd_rreal_brecal_vrecal_BOTH.vcf" name="99_sorted_pmd_rreal_brecal_vrecal_BOTH.vcf" renderer="BASIC_FEATURE" sortable="false" visible="true" windowFunction="count"/>
      </Panel>
      <Panel height="6067" name="Panel1390472597613" width="1131">
          <Track altColor="0,0,178" autoScale="true" color="175,175,175" colorScale="ContinuousColorScale;0.0;10.0;255,255,255;175,175,175" displayMode="COLLAPSED" featureVisibilityWindow="-1" fontSize="10" id="http://localhost:5000/api/v1/static/99-1-1A.130815_BD26W2ACXX_indexAAGGACAC.lane4_sorted_pmd.bam_coverage" name="99-1-1A.130815_BD26W2ACXX_indexAAGGACAC.lane4_sorted_pmd.bam Coverage" showReference="false" snpThreshold="0.2" sortable="true" visible="true">
              <DataRange baseline="0.0" drawBaseline="false" flipAxis="false" maximum="10.0" minimum="0.0" type="LINEAR"/>
          </Track>
          <Track altColor="0,0,178" autoScale="false" color="0,0,178" displayMode="EXPANDED" featureVisibilityWindow="-1" fontSize="10" id="http://localhost:5000/api/v1/static/99-1-1A.130815_BD26W2ACXX_indexAAGGACAC.lane4_sorted_pmd.bam" name="99-1-1A.130815_BD26W2ACXX_indexAAGGACAC.lane4_sorted_pmd.bam" showSpliceJunctions="false" sortable="true" visible="true">
              <RenderOptions colorByTag="" colorOption="UNEXPECTED_PAIR" flagUnmappedPairs="false" groupByTag="" maxInsertSize="1000" minInsertSize="50" shadeBasesOption="QUALITY" shadeCenters="true" showAllBases="false" sortByTag=""/>
          </Track>
      </Panel>
      <Panel height="65" name="FeaturePanel" width="1131">
          <Track altColor="0,0,178" autoScale="false" color="0,0,178" displayMode="COLLAPSED" featureVisibilityWindow="-1" fontSize="10" id="Reference sequence" name="Reference sequence" sortable="false" visible="true"/>
          <Track altColor="0,0,178" autoScale="false" clazz="org.broad.igv.track.FeatureTrack" color="0,0,178" displayMode="COLLAPSED" featureVisibilityWindow="-1" fontSize="10" height="35" id="hg19_genes" name="RefSeq Genes" renderer="BASIC_FEATURE" sortable="false" visible="true" windowFunction="count"/>
      </Panel>
      <PanelLayout dividerFractions="0.166383701188455,0.8811544991511036"/>
      <HiddenAttributes>
          <Attribute name="NAME"/>
          <Attribute name="DATA FILE"/>
          <Attribute name="DATA TYPE"/>
      </HiddenAttributes>
  </Session>
  """.format(chr='chr1', start_bp='9900', stop_bp='10100')

  return sessionXml

  return redirect(igv_url)
