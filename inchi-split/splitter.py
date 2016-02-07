
import re
from collections import namedtuple

# this is almost a validating expression, it could certainly be simpler by just using [^/]* inside the groups
inchiLayers=(
r"(InChI=1S?)",
r"(/[a-zA-Z0-9\.]*)", # formula
r"(/c[0-9\(\)\-\,;]*)?", # skeleton
r"(/h[0-9,\-\H\(\);]*)?", # hydrogens
r"(/q[\-\+0-9;]*)?", # charge
r"(/p[\-\+0-9,;]*)?", # protonation
r"(/b[\-\+0-9,\?;]*)?", # stereo_bond
r"(/t[\-\+0-9,\?;]*)?", #stereo_tet  FIX: probably could be tightened up
r"(/m[\-\+0-9,;]*)?", #stereo_m    FIX: probably could be tightened up
r"(/s[\-\+0-9,;]*)?", #stereo_s    FIX: probably could be tightened up
r"(/i[\-\+0-9,;]*)?", #isotope
r"(/b[\-\+0-9,\?;]*)?", #isotope_stereo_bond
r"(/t[\-\+0-9,\?;]*)?", #isotope_stereo_tet  FIX: probably could be tightened up
r"(/m[\-\+0-9,;]*)?", #isotope_stereo_m    FIX: probably could be tightened up
r"(/s[\-\+0-9,;]*)?", #isotope_stereo_s    FIX: probably could be tightened up
r"(/f/h[0-9,\-\H\(\);]*)?", # fixed_h
r"(/i[\-\+0-9,;]*)?", #fixedh_isotope
r"(/b[\-\+0-9,\?;]*)?", #fixedh_stereo_bond
r"(/t[\-\+0-9,\?;]*)?", #fixedh_stereo_tet  FIX: probably could be tightened up
r"(/m[\-\+0-9,;]*)?", #fixedh_stereo_m    FIX: probably could be tightened up
r"(/s[\-\+0-9,;]*)?", #fixedh_stereo_s    FIX: probably could be tightened up

)
coreExpr=re.compile(''.join(inchiLayers))
Layers=namedtuple("Layers",['start','formula','skeleton','hydrogens','charge','protonation','stereo_bond','stereo_tet','stereo_m','stereo_s',
                            'isotope','isotope_stereo_bond','isotope_stereo_tet','isotope_stereo_m','isotope_stereo_s',
                            'fixedh','fixedh_isotope','fixedh_stereo_bond','fixedh_stereo_tet','fixedh_stereo_m','fixedh_stereo_s'])
def extractLayers(inchi):
    """

    >>> tpl=extractLayers('InChI=1S/C16H20N4O3/c1-9(21)19-15(18-4)20-13-11-7-10(8-17)5-6-12(11)23-16(2,3)14(13)22/h5-7,13-14,22H,1-4H3,(H2,18,19,20,21)/t13?,14-/m0/s1')
    >>> tpl.start
    'InChI=1S'
    >>> tpl.formula
    'C16H20N4O3'
    >>> tpl.skeleton
    'c1-9(21)19-15(18-4)20-13-11-7-10(8-17)5-6-12(11)23-16(2,3)14(13)22'
    >>> tpl.hydrogens
    'h5-7,13-14,22H,1-4H3,(H2,18,19,20,21)'
    >>> tpl.charge
    ''
    >>> tpl.protonation
    ''
    >>> tpl.stereo_bond
    ''
    >>> tpl.stereo_tet
    't13?,14-'
    >>> tpl.stereo_m
    'm0'
    >>> tpl.stereo_s
    's1'
    >>> tpl.isotope
    ''
    >>> tpl.fixedh
    ''

    Charge layers:
        From [O-]CCCC[NH3+]
    >>> tpl = extractLayers('InChI=1S/C4H10NO/c5-3-1-2-4-6/h1-5H2/q-1/p+1')
    >>> tpl.charge
    'q-1'
    >>> tpl.protonation
    'p+1'

    Stereochemistry:
        From [O-][C@H](Cl)/C=C/C=C(/CC(O)=N)CC(=O)N
    >>> tpl = extractLayers('InChI=1S/C9H12ClN2O3/c10-7(13)3-1-2-6(4-8(11)14)5-9(12)15/h1-3,7H,4-5H2,(H2,11,14)(H2,12,15)/q-1/b3-1+/t7-/m0/s1')
    >>> tpl.stereo_bond
    'b3-1+'
    >>> tpl.stereo_tet
    't7-'
    >>> tpl.stereo_m
    'm0'
    >>> tpl.stereo_s
    's1'

    Isotopes:
       From: [13CH3]O
    >>> tpl = extractLayers('InChI=1S/CH4O/c1-2/h2H,1H3/i1+1')
    >>> tpl.isotope
    'i1+1'
    >>> tpl.isotope_stereo_tet
    ''

    Isotope + stereo
       From: [13CH3]O[C@H](C)O
    >>> tpl = extractLayers('InChI=1S/C3H7ClO/c1-3(4)5-2/h3H,1-2H3/t3-/m1/s1/i2+1')
    >>> tpl.isotope
    'i2+1'
    >>> tpl.stereo_tet
    't3-'
    >>> tpl.isotope_stereo_tet
    ''

    Isotope causes stereo
       From: [13CH3][C@H](C)O
    >>> tpl = extractLayers('InChI=1S/C3H8O/c1-3(2)4/h3-4H,1-2H3/i1+1/t3-/m1/s1')
    >>> tpl.isotope
    'i1+1'
    >>> tpl.stereo_tet
    ''
    >>> tpl.isotope_stereo_tet
    't3-'

    Isotope causes stereo + standard stereo
        From: [13CH3][C@H](C)O[C@H](C)O
    >>> tpl = extractLayers('InChI=1S/C5H12O2/c1-4(2)7-5(3)6/h4-6H,1-3H3/t5-/m1/s1/i1+1/t4-,5-')
    >>> tpl.isotope
    'i1+1'
    >>> tpl.stereo_tet
    't5-'
    >>> tpl.isotope_stereo_tet
    't4-,5-'

    Fixed Hs and Isotopes
        From: O=C([18O])/C=C/C(=[18O])O
    >>> tpl = extractLayers('InChI=1/C4H3O4/c5-3(6)1-2-4(7)8/h1-2H,(H,5,6)/b2-1+/i5+2,7+2/f/h5H/i6+2,7+2')
    >>> tpl.isotope
    'i5+2,7+2'
    >>> tpl.fixedh_isotope
    'i6+2,7+2'

    Fixed Hs causes stereo_bond
        From: F[C@H](Cl)/C=C/C=C(/CC(O)=N)CC(=O)N
    >>> tpl = extractLayers('InChI=1/C9H12ClFN2O2/c10-7(11)3-1-2-6(4-8(12)14)5-9(13)15/h1-3,7H,4-5H2,(H2,12,14)(H2,13,15)/b3-1+/t7-/m0/s1/f/h12,14H,13H2/b3-1+,6-2-,12-8?')
    >>> tpl.fixedh
    'f/h12,14H,13H2'
    >>> tpl.fixedh_stereo_bond
    'b3-1+,6-2-,12-8?'

    Fixed Hs causes stereo
        From: C[C@H](Cl)[C@H](/CC(O)=N)CC(=O)N
    >>> tpl = extractLayers('InChI=1/C7H13ClN2O2/c1-4(8)5(2-6(9)11)3-7(10)12/h4-5H,2-3H2,1H3,(H2,9,11)(H2,10,12)/t4-/m0/s1/f/h9,11H,10H2/t4-,5+')
    >>> tpl.fixedh
    'f/h9,11H,10H2'
    >>> tpl.fixedh_stereo_tet
    't4-,5+'

    Disconnected parts + Fixed Hs causes stereo_bond + isotopes cause stereo
        From: [13CH3][C@H](C)O[C@H](C)O.F[C@H](Cl)/C=C/C=C(/CC(O)=N)CC(=O)N
    >>> tpl = extractLayers('InChI=1/C9H12ClFN2O2.C5H12O2/c10-7(11)3-1-2-6(4-8(12)14)5-9(13)15;1-4(2)7-5(3)6/h1-3,7H,4-5H2,(H2,12,14)(H2,13,15);4-6H,1-3H3/b3-1+;/t7-;5-/m01/s1/i;1+1/t;4-,5-/f/h12,14H,13H2;/b3-1+,6-2-,12-8?;')
    >>> tpl.stereo_bond
    'b3-1+;'
    >>> tpl.isotope
    'i;1+1'
    >>> tpl.isotope_stereo_tet
    't;4-,5-'
    >>> tpl.fixedh_stereo_bond
    'b3-1+,6-2-,12-8?;'

    Edge cases:
    >>> tpl=extractLayers('InChI=1S/H2/h1H')
    >>> tpl.start
    'InChI=1S'
    >>> tpl.formula
    'H2'
    >>> tpl.skeleton
    ''
    >>> tpl.hydrogens
    'h1H'
    >>> tpl=extractLayers('InChI=1S/H')
    >>> tpl.start
    'InChI=1S'
    >>> tpl.formula
    'H'
    >>> tpl.skeleton
    ''
    >>> tpl.hydrogens
    ''

    """
    match = coreExpr.match(inchi)
    if not match:
        return None
    gps = list(match.groups())
    res = []
    for e in gps:
        if not e:
            res.append('')
        elif e[0]=='/':
            res.append(e[1:])
        else:
            res.append(e)

    return Layers(*res)

if __name__=='__main__':
    import doctest
    doctest.testmod()
