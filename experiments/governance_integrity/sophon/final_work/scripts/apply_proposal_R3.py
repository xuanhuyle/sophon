#!/usr/bin/env python3
"""R3 proposal: on a copy of the AFTER tree (G2 + commit 9bb43d710094), give the DROM BNC and CIPAV rate rules a date variation
(date >= 07/2024) derived from D756-5 (1/6 | 1/3, 1/2, 2/3, rounded UP to 0,1) x D613-4 v.LEGIARTI000049624068 (BNC 23,1 %, CIPAV 23,2 %).
usage: python3 -I work/scripts/apply_proposal_R3.py <tree_root_containing_modele-social>"""
import sys, re
root = sys.argv[1]
p = f"{root}/modele-social/règles/dirigeant/auto-entrepreneur/exonérations.publicodes"
s = open(p, encoding='utf-8').read()
def block(name, target, vals_old, vals_new, base_old, base_new, frac1):
    note = (f"      note: |\n        D756-5 (LEGIARTI000034726710): {frac1} du taux de base jusqu'à la fin du 7e trimestre civil, 1/2 jusqu'à la fin de la 3e année civile, 2/3 ensuite, arrondi au dixième supérieur.\n"
            f"        Taux de base D613-4 : {base_old} % jusqu'au 30/06/2024 (LEGIARTI000046714712), {base_new} % depuis le 01/07/2024 (LEGIARTI000049624068).\n")
    def var(o, n): return (f"            variations:\n              - si: date >= 07/2024\n                alors: {n}%\n              - sinon: {o}%\n")
    return (f"    {name}:\n      remplace: {target}\n{note}      variations:\n"
            f"        - si: première période\n          alors:\n{var(vals_old[0], vals_new[0])}"
            f"        - si: seconde période\n          alors:\n{var(vals_old[1], vals_new[1])}"
            f"        - sinon:\n{var(vals_old[2], vals_new[2])}")
new_bnc = block("taux service BNC", "cotisations et contributions . cotisations . service BNC . taux", ("3.60", "10.60", "14.10"), ("3.90", "11.60", "15.40"), "21,1", "23,1", "1/6")
new_cipav = block("taux CIPAV", "cotisations et contributions . cotisations . cotisations CIPAV . taux", ("7.10", "10.60", "14.20"), ("7.80", "11.60", "15.50"), "21,2", "23,2", "1/3")
pat_bnc = re.compile(r"    taux service BNC:\n      remplace: cotisations et contributions \. cotisations \. service BNC \. taux\n      variations:\n(?:        .*\n|          .*\n)+?(?=\n)", re.M)
pat_cipav = re.compile(r"    taux CIPAV:\n      remplace: cotisations et contributions \. cotisations \. cotisations CIPAV \. taux\n      variations:\n(?:        .*\n|          .*\n)+?(?=\n)", re.M)
s2, n1 = pat_bnc.subn(new_bnc, s); s3, n2 = pat_cipav.subn(new_cipav, s2)
assert n1 == 1 and n2 == 1, (n1, n2)
open(p, 'w', encoding='utf-8').write(s3)
print("patched", p, n1, n2)
