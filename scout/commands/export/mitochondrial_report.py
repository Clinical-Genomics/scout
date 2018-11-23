import os
import click
import logging
import datetime

from xlsxwriter import Workbook

from scout.constants import MT_EXPORT_HEADER
from scout.export.variant import export_mt_variants

LOG = logging.getLogger(__name__)

@click.command('mt_report', short_help='Mitochondrial variants Excel report')
@click.option('--case-id',
              help='Case id to search for'
)
@click.option('--outpath',
              help='Path to output file'
)
@click.pass_context
def mt_report(context, case_id, outpath=None):
    """Export all mitochondrial variants for a collaborator and a case

        Args:
            adapter(MongoAdapter)
            case_id(str)
            outpath(str) : path to output file

        Returns:
            zipped_file_path(str): path to created zip file,
                containing a file for each sample in the case
    """
    LOG.info('exporting mitochondrial variants for case "{}"'.format(case_id))

    adapter = context.obj['adapter']
    query = {'chrom':'MT'}

    case_obj = adapter.case(case_id=case_id)
    samples = case_obj.get('individuals')

    if not case_obj:
        LOG.warning('Could not find a scout case with id "{}". No report was created.'.format(case_id))
        context.abort()

    mt_variants = list(adapter.variants(case_id=case_id, query=query, nr_of_variants= -1, sort_key='position'))
    if not mt_variants:
        LOG.warning('There are no MT variants associated to case {} in database!'.format(case_id))
        context.abort()

    today = datetime.datetime.now().strftime('%Y-%m-%d')
    # get document lines for each of the cases's individuals
    # Write excel document for each sample in case
    for sample in samples:
        sample_id = sample['individual_id']
        sample_lines = export_mt_variants(variants=mt_variants, sample_id=sample_id)
        LOG.info(str(sample['individual_id'])+'--->'+str(sample_lines))

        # set up outfolder
        if not outpath:
            outpath = str(os.getcwd())

        # set up document name
        document_name = '.'.join([case_obj['display_name'], sample_id, today]) + '.xlsx'
        workbook = Workbook(os.path.join(outpath,document_name))
        Report_Sheet = workbook.add_worksheet()

        # Write the column header
        row = 0
        for col,field in enumerate(MT_EXPORT_HEADER):
            Report_Sheet.write(row,col,field)

        # Write variant lines
        for row, line in enumerate(sample_lines,1): # each line becomes a row in the document
            for col, field in enumerate(line): # each field in line becomes a cell
                Report_Sheet.write(row,col,field)
        workbook.close()
