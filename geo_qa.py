import rdflib
import requests
import lxml.html
import sys
from rdflib import Literal, XSD


prefix = "https://en.wikipedia.org"


def ontology(path):
    print("in ontology")
    url = "https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)"
    res = requests.get(url)
    doc = lxml.html.fromstring(res.content)

    g = rdflib.Graph()

    table = "/descendant::table[position() = 2]"
    countries_urls = doc.xpath(table + "//tr/td[position() = 1]/descendant::span/descendant::a[position() = 1]/@href")
    countries_urls += doc.xpath(table + "//tr[position() = 191]/td[position() = 1]/i/a[position() = 1]/@href")
    for i in range(len(countries_urls)):
        get_country_info(g, prefix + countries_urls[i])

    g.serialize(path, format="nt", encoding='utf-8')
    sorted(g)
    print("finished")


def get_country_info(g, url):
    res = requests.get(url)
    doc = lxml.html.fromstring(res.content)
    infobox = "/descendant::table[contains(@class, 'infobox')][position() = 1]"

    country_name = doc.xpath("//h1[@class='firstHeading'][position() = 1]/text()")[0]
    name = rdflib.URIRef("http://example.org/" + country_name.lower().split(" (")[0].replace(" ", "_"))
    is_a = rdflib.URIRef("http://example.org/is_a")
    country = rdflib.URIRef("http://example.org/country")
    g.add((name, is_a, country))

    get_president(g, name, doc, infobox)
    get_prime_minister(g, name, doc, infobox)
    get_population(g, name, doc, infobox)
    get_area(g, name, doc, infobox)
    get_government(g, name, doc, infobox)
    get_capital(g, name, doc, infobox)


def get_president(g, country, doc, infobox):
    president = rdflib.URIRef("http://example.org/president")
    president_name = doc.xpath(infobox + "//tr/th/div/a[text()='President']/../../../td/descendant::a[position() = 1]/text()")
    if president_name:
        name = rdflib.URIRef("http://example.org/" + president_name[0].lower().strip().replace(" ", "_"))
        g.add((country, president, name))
        url = doc.xpath(infobox + "//tr/th/div/a[text()='President']/../../../td/a/@href")
        if url:
            get_entity(g, prefix + url[0], name)


def get_prime_minister(g, country, doc, infobox):
    prime_minister = rdflib.URIRef("http://example.org/prime_minister")
    pm_name = doc.xpath(infobox + "//tr/th/div/a[text()='Prime Minister']/../../../td//a/text()")
    if not pm_name:
        pm_name = doc.xpath(infobox + "//tr/th/div/span/a[text()='Prime Minister']/../../../../td//a/text()")
    if not pm_name:
        pm_name = doc.xpath(infobox + "//tr/th/div/a[contains(text(),'Prime Minister')]/../../../td//a/text()")
    if pm_name:
        name = rdflib.URIRef("http://example.org/" + pm_name[0].lower().strip().replace(" ", "_"))
        g.add((country, prime_minister, name))
        url = doc.xpath(infobox + "//tr/th/div/a[text()='Prime Minister']/../../../td//a/@href")
        if not url:
            url = doc.xpath(infobox + "//tr/th/div/span/a[text()='Prime Minister']/../../../../td//a/@href")
        if not url:
            url = doc.xpath(infobox + "//tr/th/div/a[contains(text(),'Prime Minister')]/../../../td//a/@href")
        if url:
            get_entity(g, prefix + url[0], name)


def get_population(g, country, doc, infobox):
    population = rdflib.URIRef("http://example.org/population")
    position = len(doc.xpath(infobox + "/tbody/tr/th/a[text()='Population']/../../preceding-sibling::*")) + 1
    population_name = doc.xpath(infobox + "/tbody/tr[position() = " + str(position + 1) + "]/td/text()")
    if not population_name:
        position = len(doc.xpath(infobox + "/tbody/tr/th[text()='Population']/../preceding-sibling::*")) + 1
        population_name = doc.xpath(infobox + "/tbody/tr[position() = " + str(position + 1) + "]/td/text()")
    if not population_name:
        population_name = doc.xpath(infobox + "/tbody/tr/th[text()='Population']/../td/text()")
    if population_name:
        name = Literal(population_name[0].split(" (")[0].strip(), datatype=XSD.integer)
        g.add((country, population, name))


def get_area(g, country, doc, infobox):
    area = rdflib.URIRef("http://example.org/area")
    position = len(doc.xpath(infobox + "/tbody/tr/th/a[contains(text(), 'Area')]/../../preceding-sibling::*"))
    area_name = doc.xpath(infobox + "/tbody/tr[position() = " + str(position + 2) + "]/td/text()")
    if not area_name:
        position = len(doc.xpath(infobox + "/tbody/tr/th[contains(text(), 'Area')]/../preceding-sibling::*"))
        area_name = doc.xpath(infobox + "/tbody/tr[position() = " + str(position + 2) + "]/td/text()")
    if not area_name:
         area_name = doc.xpath(infobox + "/tbody/tr/th[contains(text(), 'Area')]/../td/text()")
    if area_name:
        name = Literal(area_name[0].split("&nbsp")[0].replace(u'\xa0', u' ').strip().split(" ")[0], datatype=XSD.integer)
        g.add((country, area, name))


def get_government(g, country, doc, infobox):
    government = rdflib.URIRef("http://example.org/government")

    government_name = doc.xpath(infobox + "//tr/th/a[text()='Government']/../../td/a/text()") + \
                      doc.xpath(infobox + "//tr/th/a[text()='Government']/../../td//a/text()") + \
                      doc.xpath(infobox + "//tr/th[text()='Government']/../td/a/text()") + \
                      doc.xpath(infobox + "//tr/th[text()='Government']/../td//a/text()") +\
                      doc.xpath(infobox +"//tr[.//*[text()='Government']]/td/text()") +\
                      doc.xpath(infobox + "//tr[.//*[text()='Government']]/td/a/text()") 
                   
    for gov in government_name:
        if gov!=" " and gov[0] != '[' and gov[0]!="\n" and gov[0] != '(':
            if gov[-1]==" ":
                gov=gov[:-1]
            if gov[0]==" ":
                gov=gov[1:]
            name = rdflib.URIRef("http://example.org/" + gov.lower().strip().replace(" ", "_"))
            g.add((country, government, name))
    

def get_capital(g, country, doc, infobox):
    capital = rdflib.URIRef("http://example.org/capital")
    capital_name = doc.xpath(infobox + "//tr/th[text()='Capital']/../td/a[position() = 1]/text()")
    if not capital_name:
        capital_name = doc.xpath(infobox + "//tr/th[text()='Capital']/../td/a[position() = 2]/text()")
    if not capital_name:
        capital_name = doc.xpath(infobox + "//tr/th[text()='Capital']/../td/descendant::a[position() = 1]/text()")
    if not capital_name or capital_name[0].lower()=="city-state":
        capital_name = doc.xpath(infobox + "//tr/th[text()='Capital']/../td/text()")
    if not capital_name:
        capital_name = doc.xpath(infobox + "//tr/th[text()='Capital']/../td/span/b/text()")
    if not capital_name:
        capital_name = doc.xpath(infobox + "//tr/th[contains(text(),'Capital')]/../td/a/text()")
    if capital_name and capital_name[0][0] != '[':
        name = rdflib.URIRef("http://example.org/" + capital_name[0].lower().strip().split(" (")[0].replace(" ", "_"))
        g.add((country, capital, name))


def get_entity(g, url, name):
    res = requests.get(url)
    doc = lxml.html.fromstring(res.content)
    infobox = "/descendant::table[contains(@class, 'infobox')][position() = 1]"
    birth_date = doc.xpath(infobox + "//tr//td//span[@class='bday']//text()")
    if birth_date:
        dob = Literal(birth_date[0], datatype=XSD.date)
        birth_date = rdflib.URIRef("http://example.org/birth_date")
        g.add((name, birth_date, dob))
    is_a = rdflib.URIRef("http://example.org/is_a")
    entity = rdflib.URIRef("http://example.org/entity")
    g.add((name, is_a, entity))



def query(file, query):
    g = rdflib.Graph()
    g.parse(file, format="nt")
    res = g.query(query)
    return list(res)

def allQueriesQ2():
    print("query_1\n")
    q1 = "SELECT distinct ?p where {?p <http://example.org/is_a> <http://example.org/entity>. ?c <http://example.org/is_a> <http://example.org/country>. ?c <http://example.org/prime_minister> ?p.}"
    res = query("ontology.nt", q1)
    print("Number of Prime Ministers:", len(res))

    print("\nquery_2\n")
    q2 = "SELECT distinct ?c where {?c <http://example.org/is_a> <http://example.org/country>.}"
    res = query("ontology.nt", q2)
    print("Number of countries:", len(res))

    print("\nquery_3\n")
    q3= "SELECT distinct ?c where {?c <http://example.org/is_a> <http://example.org/country>. ?c <http://example.org/government> ?t. FILTER (regex(lcase(str(?t)),'republic')). }"
    res = query("ontology.nt", q3)
    print("Number of republics:", len(res))

    print("\nquery_4\n")
    q4 = "SELECT distinct ?c where {?c <http://example.org/is_a> <http://example.org/country>. ?c <http://example.org/government> ?t. FILTER (regex(lcase(str(?t)),'monarchy')).}"
    res = query("ontology.nt", q4)
    print("Number of monarchies:", len(res))


def get_relation(q_list,q_list_len):
    relations_types=["president","prime","population","area","government","capital"]
    found = False
    for relation in relations_types:
        for i in range (2,q_list_len):
            if (str(q_list[i])).lower()==relation:
                res=relation
                found=True
                break
    if found==False:
        res="no_relation"
    if res=="prime":
        res="prime_minister"
    return res


def get_entity_uri(q_list,start_index,last_index):
    entity_list=[q_list[i] for i in range(start_index,last_index)]
    entity = ""
    for i,word in enumerate(entity_list):
        if i == 0:
            entity = entity +word.lower()
        else:
            entity= entity+"_"+word.lower()
    if entity[-1] == '?':
        entity = entity[:-1]
    entity_uri = "http://example.org/" + entity
    return entity_uri


def question(q):
    q_list=q.split(" ")
    q_list_len=len(q_list)
    relation=get_relation(q_list,q_list_len)
    if relation!="no_relation":
        relation_uri="http://example.org/" + relation.replace(" ", "_")
    
    #question 1 & 2 & 9
    if "who" in q_list[0].lower():
        if relation=="no_relation":
            entity_uri = get_entity_uri(q_list,2,q_list_len)
            q_primeMinister="SELECT ?c where {?c <http://example.org/is_a> <http://example.org/country>. ?c <http://example.org/prime_minister> <"+entity_uri+">.}"
            q_president="SELECT ?c where {?c <http://example.org/is_a> <http://example.org/country>. ?c <http://example.org/president> <"+entity_uri+">.}"
            res_primeMinister = query("ontology.nt", q_primeMinister)
            res_president = query("ontology.nt", q_president)
            if len(res_primeMinister)>0:
                for i in res_primeMinister:
                    print("prime minister of",i[0].title().split('/')[-1].replace("_", " "))
            if len(res_president)>0:
                for i in res_president:
                    print("president of",i[0].title().split('/')[-1].replace("_", " "))
            if len(res_primeMinister)==0 and len(res_president)==0:
                print("None")
        else:
            if relation == "president":
                entity_uri = get_entity_uri(q_list,5,q_list_len)
            if relation == "prime_minister":
                entity_uri = get_entity_uri(q_list,6,q_list_len)
            q = "SELECT ?x where {?x <http://example.org/is_a> <http://example.org/entity>. <"+ entity_uri+ "> <" + relation_uri +">  ?x. }"
            res = query("ontology.nt", q)
            if len(res)>0:
                print(res[0][0].title().split('/')[-1].replace("_", " ")) 
            else:
                 print("None")
        return

    #question 3 & 4 & 5 & 6
    if "what" in q_list[0].lower():
        entity_uri = get_entity_uri(q_list,5,q_list_len)
        q="SELECT ?x where { <" + entity_uri+ "> <" + relation_uri +">  ?x.}"
        res = query("ontology.nt", q)
        if len(res)>0:
            if relation=="area":
                print(res[0][0].title().split('/')[-1].replace("_", " "), " km2")
            else:
                for i in res:
                    print(i[0].title().split('/')[-1].replace("_", " "))
        else:
             print("None")
        return

    #question 7 & 8
    if "when" in q_list[0].lower():
        if relation=="president":
            entity_uri = get_entity_uri(q_list,5,q_list_len-1)
        if relation=="prime_minister":
            entity_uri = get_entity_uri(q_list,6,q_list_len-1)
        q="SELECT ?date where{<"+entity_uri+ "> <" +relation_uri +">  ?x. ?x <http://example.org/birth_date> ?date.}"
        res = query("ontology.nt", q)
        if len(res)>0:
            print(res[0][0].title().split('/')[-1].replace("_", " "))
        else:
             print("None")

    return


def test():
    q1 = "SELECT ?p where {?c <http://example.org/is_a> <http://example.org/country>. ?c <http://example.org/capital> ?p.}"
    res = query("ontology.nt", q1)
    print("Number of capitals:", len(res))
    for i in res:
        print (i[0],"\n")


def main(args):
    if args[1] == "create":
        ontology(args[2])

    if args[1] == "question":
        argument=args[2].replace('"', '')
        question(argument)

main(sys.argv)
