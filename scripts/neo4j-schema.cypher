// CoResearcher OS - Neo4j Knowledge Graph Schema
// Run against Neo4j database to initialize the schema

// === Constraints ===
CREATE CONSTRAINT paper_id IF NOT EXISTS FOR (p:Paper) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT author_id IF NOT EXISTS FOR (a:Author) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT institution_id IF NOT EXISTS FOR (i:Institution) REQUIRE i.id IS UNIQUE;
CREATE CONSTRAINT concept_id IF NOT EXISTS FOR (c:Concept) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT claim_id IF NOT EXISTS FOR (c:Claim) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT hypothesis_id IF NOT EXISTS FOR (h:Hypothesis) REQUIRE h.id IS UNIQUE;
CREATE CONSTRAINT experiment_id IF NOT EXISTS FOR (e:Experiment) REQUIRE e.id IS UNIQUE;

// === Indexes for full-text search ===
CREATE INDEX paper_title_index IF NOT EXISTS FOR (p:Paper) ON (p.title);
CREATE INDEX paper_doi_index IF NOT EXISTS FOR (p:Paper) ON (p.doi);
CREATE INDEX paper_keywords_index IF NOT EXISTS FOR (p:Paper) ON (p.keywords);
CREATE INDEX author_name_index IF NOT EXISTS FOR (a:Author) ON (a.name);
CREATE INDEX author_orcid_index IF NOT EXISTS FOR (a:Author) ON (a.orcid);
CREATE INDEX concept_name_index IF NOT EXISTS FOR (c:Concept) ON (c.name);
CREATE INDEX claim_text_index IF NOT EXISTS FOR (c:Claim) ON (c.text);
CREATE INDEX hypothesis_text_index IF NOT EXISTS FOR (h:Hypothesis) ON (h.text);

// === Full-text search indexes ===
CREATE FULLTEXT INDEX paper_fulltext IF NOT EXISTS FOR (p:Paper) ON EACH [p.title, p.abstract];
CREATE FULLTEXT INDEX concept_fulltext IF NOT EXISTS FOR (c:Concept) ON EACH [c.name, c.description];
CREATE FULLTEXT INDEX claim_fulltext IF NOT EXISTS FOR (c:Claim) ON EACH [c.text];

// === Node properties documentation ===
// :Paper { id, title, abstract, doi, pmid, arxivId, year, journal, volume, issue, pages, url, pdfUrl, citations, keywords, fields, language, processedAt, embedding }
// :Author { id, name, orcid, email, hIndex, affiliations, fields, paperCount }
// :Institution { id, name, ror, country, type, fields }
// :Concept { id, name, description, ontology, ontologyId, synonyms, category, embedding }
// :Claim { id, text, confidence, evidence, evidenceType, status, extractedFrom, extractionMethod, tags, embedding }
// :Hypothesis { id, text, status, confidence, generatedBy, testedBy, tags }
// :Experiment { id, name, description, design, results, conclusion, status, reproducibility, tags }

// === Relationship types ===
// (p:Paper)-[:CITES { context, citationCount, citationIntent }]->(p:Paper)
// (p:Paper)-[:AUTHORED_BY]->(a:Author)
// (a:Author)-[:AFFILIATED_WITH]->(i:Institution)
// (p:Paper)-[:MENTIONS]->(c:Concept)
// (p:Paper)-[:PRODUCES]->(cl:Claim)
// (cl:Claim)-[:SUPPORTS|CONTRADICTS { strength, evidence, method }]->(cl:Claim)
// (cl:Claim)-[:DERIVES_FROM]->(p:Paper)
// (h:Hypothesis)-[:TESTS]->(e:Experiment)
// (e:Experiment)-[:VALIDATES|INVALIDATES]->(h:Hypothesis)
// (p:Paper)-[:USES]->(d:Dataset)

RETURN 'Neo4j schema initialized successfully' AS result;