# Fichier site_rencontre.py
from owlready2 import *
from go_partie_de import *
  
from flask import Flask, request
app = Flask(__name__)
  
import mygene
mg = mygene.MyGeneInfo()
  
def chercher_proteine(nom_proteine):
    r = mg.query('name:"%s"' % nom_proteine, fields = "go.CC.id",species = "human", size = 1)
    if not "go" in r["hits"][0]: return set()
  
    cc = r["hits"][0]["go"]["CC"]
    if not isinstance(cc, list): cc = [cc]
  
    sites = set()
    for dico in cc:
        id_go = dico["id"]
        terme_go = obo[id_go.replace(":", "_")]
        if terme_go: sites.add(terme_go)
    
    return sites
  
def intersection_semantique(sites1, sites2):
    sous_parties1 = set()
    for site in sites1:
        sous_parties1.update(site.sous_parties_transitives())
    
    sous_parties2 = set()
    for site in sites2:
        sous_parties2.update(site.sous_parties_transitives())
    
    sites_communs = sous_parties1 & sous_parties2
  
    cache = { site : site.sous_parties_transitives()for site in sites_communs }
  
    sites_communs_sans_sous_parties = set()
    for site in sites_communs:
        for site2 in sites_communs:
            if (not site2 is site) and (site in cache[site2]): break
        else:
            sites_communs_sans_sous_parties.add(site)
  
    return sites_communs_sans_sous_parties
  
@app.route('/')
def page_saisie():
    html  = """
<html><body>
  <form action="/resultat">
    Protéine 1: <input type="text" name="prot1"/><br/><br/>
    Protéine 2: <input type="text" name="prot2"/><br/><br/>
    <input type="submit"/>
  </form>
</body></html>"""
    return html
  
@app.route('/resultat')
def page_resultat():
    prot1 = request.args.get("prot1", "")
    prot2 = request.args.get("prot2", "")
  
    sites1 = chercher_proteine(prot1)
    sites2 = chercher_proteine(prot2)
  
    sites_communs = intersection_semantique(sites1, sites2)
  
    html  = """<html><body>"""
    html += """<h3>Site de la protéine 1 (%s)</h3>""" % prot1
    if sites1:
        html += "<br/>".join(sorted(str(site) for site in sites1))
    else:
        html += "(Aucun)<br/>"
  
    html += """<h3>Site de la protéine 2 (%s)</h3>""" % prot2
    if sites2:
        html += "<br/>".join(sorted(str(site) for site in sites2))
    else:
        html += "(Aucun)<br/>"
  
    html += """<h3>Sites de rencontre possibles</h3>"""
    if sites_communs:
        html += "<br/>".join(sorted(str(site) for site in sites_communs))
    else:
        html += "(Aucun)<br/>"
    
    html += """</body></html>"""
    return html
  
import werkzeug.serving
werkzeug.serving.run_simple("localhost", 5000, app)
