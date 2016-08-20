# -*- coding: utf-8 -*-
import codecs
from distutils.spawn import find_executable
import os.path
import subprocess
import shutil
from tempfile import NamedTemporaryFile, mkdtemp

from scout.exc import (ExecutableNotFoundError, SinglePedigreeError,
                       MadelineIncompatibleError)


def find_exe(exe_path):
    if exe_path:
        exe_path = os.path.abspath(exe_path)
        if not os.path.exists(exe_path):
            raise ExecutableNotFoundError()
    else:
        # expect to find in $PATH
        exe_path = find_executable('madeline2')
        if exe_path is None:
            raise ExecutableNotFoundError()
    return exe_path


def make_svg(ped_family, family_id, madeline_exe=None):
    """Run and process madeline."""
    madeline_exe = find_exe(madeline_exe)
    external_individuals = external_ped(ped_family.individuals)
    ped_family.families[family_id].individuals = external_individuals
    svg_content = run_madeline(ped_family, exe=madeline_exe)
    return svg_content


def run_madeline(ped, exe):
    """Run Madeline and capture the output."""
    output_dir = mkdtemp()
    output_prefix = "{}/madeline".format(output_dir)
    out_path = "{}.xml".format(output_prefix)

    if not any([ind.has_parents for ind in ped.individuals.values()]):
        raise MadelineIncompatibleError("madeline needs connected individuals")

    madeline_ped_lines = list(ped.to_madeline())
    if len(madeline_ped_lines) == 2:
        raise SinglePedigreeError("can't generate pedigree with single"
                                  "individual")

    # write the input to a temp file
    with NamedTemporaryFile('r+w') as in_file:
        madeline_content = '\n'.join(madeline_ped_lines)
        in_file.write(madeline_content)
        in_file.flush()

        subprocess.call([exe, '--color', '--outputprefix',
                         output_prefix, in_file.name])

    with codecs.open(out_path, 'r') as output:
        svg_content = output.read()

    shutil.rmtree(output_dir)
    return svg_content


def map_sample_ids(ped_individuals):
    """Map between internal and external sample ids."""
    id_mapping = {ind_id: (ind.extra_info.get('display_name') or ind_id)
                  for ind_id, ind in ped_individuals.items()}
    return id_mapping


def external_ped(ped_individuals):
    """Convert and fill out 'ped' with external ids."""
    id_mapping = map_sample_ids(ped_individuals)

    external_individuals = {}
    for individual_id, individual in ped_individuals.items():
        external_id = id_mapping.get(individual_id)
        individual.individual_id = external_id
        individual.mother = id_mapping.get(individual.mother, '0')
        individual.father = id_mapping.get(individual.father, '0')
        # all individuals in the pedigree have been sequenced
        individual.consultand = 'Yes'
        external_individuals[external_id] = individual

    return external_individuals
