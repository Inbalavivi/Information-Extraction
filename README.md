
# Information-Extraction

### Description:

An information extraction system to answer natural language questions about geography using ontologies, XPATH, SPARQL and HTML
as part of the course "Web Data Management". The data is collected from: https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations

The system consists of two main parts:
1. Construction of the ontology - Information Extraction on Wikipedia pages.
2. Answer natural language questions- The program translates the question into a SPARQL query and return the answers based on the ontology we built.

<img src="https://github.com/Inbalavivi/Information-Extraction/blob/2dcbf476b9be6e6f5d621e17ef2e541eeb6e1d1c/ontology.PNG" width="400" height="400">

### Questions' Format:

All questions will be in English and will include one of the following 9 structures:
1. Who is the president of < country >?
2. Who is the prime minister of < country >?
3. What is the population of < country >?
4. What is the area of < country >?
5. What is the government of < country >?
6. What is the capital of < country >?
7. When was the president of < country > born?
8. When was the prime minister of < country > born?
9. Who is < entity >? 

### Execution Instructions:

To create the ontology run:

```html
python geo_qa.py create ontology.nt
```

To ask a question run:

```html
python geo_qa.py question “<natural language question string>”
```

In question state the program will recieve a question in natural language, print the answer to the screen and stop it's run.
