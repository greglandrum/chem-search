"""
Encapsulate reading and formatting of SureChEMBL
"""

from Sdf import Sdf
import json
import os, os.path
import rdkit.Chem

class Surechembl(Sdf):
    def __init__(self, path):
        Sdf.__init__(self, path)

    def mol_to_dict(self, mol):
        """
        Capture all the information from a SureChEMBL molecule into a dictionary

        mol_to_dict( (Surechembl)self, (rdkit.Chem.Mol)mol) -> dict
        """
        props = set(mol.GetPropNames())
        # All the properties defined in the molecule, as-is
        d = {p.lower() : self.cast(mol.GetProp(p)) for p in props}
        d['id'] = 'https://www.surechembl.org/chemical/' + mol.GetProp('ID')

        smiles = []
        # Attempt normalization; this may fail if there are ... oddities ...
        # in the molecule.
        rdkit_mol = rdkit.Chem.MolFromSmiles(rdkit.Chem.MolToSmiles(mol)) # Canonicalizes
        if rdkit_mol is not None:
            d['rdkit_smiles'] = rdkit.Chem.MolToSmiles(rdkit_mol)
            smiles.append(d['rdkit_smiles'])
        if smiles:
            d['smiles'] = list(set(smiles))

        return d

def test_mol_to_dict():
    mols = Surechembl(path="resources/surechembl-test-data.sdf*")
    for mol in mols:
        print(json.dumps(mol))

if __name__ == "__main__":
    test_mol_to_dict()
