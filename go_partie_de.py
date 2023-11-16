from owlready2 import *
 
default_world.set_backend(filename = "quadstore.sqlite3")
go = get_ontology("http://purl.obolibrary.org/obo/go.owl#").load()
obo = go.get_namespace("http://purl.obolibrary.org/obo/")
default_world.save()
 
def mon_rendu(entity):
    return "%s:%s" % (entity.name, entity.label.first())
set_render_func(mon_rendu)
 
with obo:
    class GO_0005575(Thing):
        @classmethod
        def sous_parties(self):
            resultats = list(self.BFO_0000051)
            resultats.extend(self.inverse_restrictions(obo.BFO_0000050))
            return resultats
         
        @classmethod
        def sous_parties_transitives(self):
            resultats = set()
            for descendant in self.descendants():
                resultats.add(descendant)
                for sous_partie in descendant.sous_parties():
                    resultats.update(sous_partie.sous_parties_transitives())
            return resultats
          
        @classmethod
        def super_parties(self):
            resultats = list(self.BFO_0000050)
            resultats.extend(self.inverse_restrictions(obo.BFO_0000051))
            return resultats
          
        @classmethod
        def super_parties_transitives(self):
            resultats = set()
            for ancetre in self.ancestors():
                if not issubclass(ancetre, GO_0005575): continue 
                resultats.add(ancetre)
                for super_partie in ancetre.super_parties():
                    if issubclass(ancetre, GO_0005575):
                        resultats.update(super_partie.super_parties_transitives())
            return resultats
