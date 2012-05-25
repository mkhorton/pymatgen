#!/usr/bin/python
import unittest
import os

from pymatgen.io.feffio import Header, Feff_tags, FeffLdos, FeffPot, Xmu
from pymatgen.core.lattice import Lattice
from pymatgen.core.structure import Composition, Structure
from numpy import array
from pymatgen.io.cifio import CifParser, CifWriter
from pymatgen.util.io_utils import file_open_zip_aware

import pymatgen

test_dir = os.path.join(os.path.dirname(os.path.abspath(pymatgen.__file__)), '..', 'test_files')

class  HeaderTest(unittest.TestCase):

    header_string = """* This FEFF.inp file generated by pymatgen, www.materialsproject.org
TITLE cif file name:  CoO19128.cif
TITLE Structure Summary:  Co2 O2
TITLE Reduced formula:  CoO
TITLE space group: (P 1), space number  (1)
TITLE abc:  3.297078   3.297078   5.254213
TITLE angles: 90.000000  90.000000 120.000000
TITLE sites: 4
* 1 Co     0.666666     0.333332     0.496324
* 2 Co     0.333333     0.666667     0.996324
* 3 O     0.666666     0.333332     0.878676
* 4 O     0.333333     0.666667     0.378675"""
    
    def test_init(self):
        filepath = os.path.join(test_dir, 'HEADER')
        header = pymatgen.io.feffio.Header.from_file(filepath)
        self.assertEqual(HeaderTest.header_string.splitlines(), header.splitlines(),"Failed to read HEADER file")

    def test_from_string(self):
        struc_from_header = pymatgen.io.feffio.Header.from_string(HeaderTest.header_string)
        self.assertEqual(struc_from_header.composition.reduced_formula, "CoO", "Failed to generate structure from HEADER string")

    def test_get_string(self):
        cif_file=os.path.join(test_dir, 'CoO19128.cif')
        r=pymatgen.io.cifio.CifParser(cif_file)
        structure=r.get_structures()[0]
        h=pymatgen.io.feffio.Header(structure,cif_file)
        head=h.get_string()
        self.assertEqual(head.splitlines()[1].split()[-1], HeaderTest.header_string.splitlines()[1].split()[-1], "Failed to generate HEADER from structure")
        
class  FeffAtomsTest(unittest.TestCase):



    def test_init(self):
        
        filepath = os.path.join(test_dir, 'ATOMS')
        atoms=pymatgen.io.feffio.FeffAtoms.from_file(filepath)
        self.assertEqual(atoms.splitlines()[3].split()[4], 'O', "failed to read ATOMS file")

    def test_get_string(self):

        struc=pymatgen.io.feffio.Header.from_string(HeaderTest.header_string)
        central_atom='O'
        a=pymatgen.io.feffio.FeffAtoms(struc, central_atom)
        atoms=a.get_string()
        self.assertEqual(atoms.splitlines()[3].split()[4], central_atom, "failed to create ATOMS string")

        
class  Feff_tagsTest(unittest.TestCase):

    def test_init(self):
        filepath = os.path.join(test_dir, 'PARAMETERS')
        parameters = pymatgen.io.feffio.Feff_tags.from_file(filepath)
        parameters["RPATH"] = 10
        self.assertEqual(parameters["COREHOLE"], "Fsr", "Failed to read PARAMETERS file")
        self.assertEqual(parameters["LDOS"], [-30., 15., .1], "Failed to read PARAMETERS file")
    def test_diff(self):
        filepath1 = os.path.join(test_dir, 'PARAMETERS')
        parameters1 = pymatgen.io.feffio.Feff_tags.from_file(filepath1)
        filepath2 = os.path.join(test_dir, 'PARAMETERS.2')
        parameters2 = pymatgen.io.feffio.Feff_tags.from_file(filepath2)
        self.assertEqual(pymatgen.io.feffio.Feff_tags(parameters1).diff(parameters2), {'Different': {}, 'Same': {'CONTROL': [1, 1, 1, 1, 1, 1], 'SCF': [4.5, 0, 30, 0.2, 1], 'EXCHANGE': [0, 0.0, 0.0, 2], 'S02': [0.0], 'COREHOLE': 'Fsr', 'FMS': [7.5, 0], 'XANES': [3.7, 0.04, 0.1], 'EDGE': 'K', 'PRINT': [1, 0, 0, 0, 0, 0], 'LDOS': [-30.0, 15.0, 0.1]}})
    def test_to_dict_and_from_dict(self):
        file_name = os.path.join(test_dir, 'PARAMETERS')
        d = pymatgen.io.feffio.Feff_tags.from_file(file_name)
        tags = pymatgen.io.feffio.Feff_tags(d).to_dict
        tags2 = pymatgen.io.feffio.Feff_tags.from_dict(d)
        self.assertEqual(tags, tags2, "Parameters do not match to and from dictionary values")

class  FeffPotTest(unittest.TestCase):

    def test_init(self):
        filepath = os.path.join(test_dir, 'POTENTIALS')
        feffpot = pymatgen.io.feffio.FeffPot.from_file(filepath)
        d, dr = pymatgen.io.feffio.FeffPot.from_string(feffpot)
        self.assertEqual(d['Co'], 1, "Wrong symbols read in for FeffPot")

class FeffLdosTest(unittest.TestCase):

    filepath1 = os.path.join(test_dir, 'feff.inp')
    filepath2 = os.path.join(test_dir, 'ldos')
    l=pymatgen.io.feffio.FeffLdos(filepath1,filepath2)

    def test_init(self):

        efermi=FeffLdosTest.l.efermi
        self.assertEqual(str(efermi), '-11.44', "Did not read correct Fermi energy from ldos test file")

    def test_complete_dos(self):

        complete_dos=FeffLdosTest.l.complete_dos
        self.assertEqual(complete_dos.to_dict['spd_dos']['S']['efermi'],float('-11.44'), "Failed to construct complete_dos dictionary properly")


class XmuTest(unittest.TestCase):

    def test_init(self):
        filepath1 = os.path.join(test_dir, 'xmu.dat')
        filepath2 = os.path.join(test_dir, 'feff.inp')
        x=pymatgen.io.feffio.Xmu(filepath1, filepath2)
        self.assertEqual(x.to_dict['atom'], 'O', "failed to form absorption dictionary")


if __name__ == '__main__':
    unittest.main()

