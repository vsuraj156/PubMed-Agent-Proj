from Bio import Entrez
import json

Entrez.email = "varunsuraj@college.harvard.edu"

def search_pubmed(query: str, max_results: int = 5) -> dict:
    """
    Search PubMed for medical literature.
    Returns titles, abstracts, and citation info.
    """
    try:
        handle = Entrez.esearch(
            db="pubmed",
            term=query,
            retmax=max_results,
            sort="relevance"
        )

        search_results = Entrez.read(handle)
        pmids = search_results['IdList']

        if not pmids:
            return {"results": [], "count": 0, "query": query}
        
        handle = Entrez.efetch(
            db="pubmed",
            id=pmids,
            rettype="abstract",
            retmode="xml"
        )

        articles = Entrez.read(handle)

        results = []
        for article in articles['PubmedArticle']:
            try:
                medline = article['MedlineCitation']
                article_data = medline['Article']

                abstract = ""
                if 'Abstract' in article_data:
                    abstract_parts = article_data['Abstract']['AbstractText']
                    abstract = ' '.join([str(part) for part in abstract_parts])
                pub_date = article_data['Journal']['JournalIssue'].get('PubDate', {})
                year = pub_date.get('Year', 'N/A')

                authors = []
                if 'AuthorList' in article_data:
                    for author in article_data['AuthorList'][:3]:
                        last = author.get('LastName', '')
                        init = author.get('Initials', '')
                        if last:
                            authors.append(f"{last} {init}")
                
                pmid = str(medline['PMID'])
                results.append({
                    'pmid': pmid,
                    'title': str(article_data['ArticleTitle']),
                    'abstract': abstract,
                    'journal': str(article_data['Journal']['Title']),
                    'year': year,
                    'authors': authors,
                    'url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                })
            except Exception as e:
                print(f"Error parsing article: {e}")
                continue
        
        return {
            "results": results,
            "count": len(results),
            "query": query
        }
    except Exception as e:
        return {"error": str(e), "query": query}


def search_clinical_guidelines(condition: str, max_results: int = 5) -> dict:
    """
    Search specifically for clinical guidelines and systematic reviews.
    """
    # Add filters for high-quality evidence
    query = f"{condition} AND (guideline[PT] OR systematic review[PT] OR meta-analysis[PT])"
    return search_pubmed(query, max_results)


def search_recent_research(topic: str, years: int = 5, max_results: int = 5) -> dict:
    """
    Search for recent research on a topic.
    """
    from datetime import datetime
    current_year = datetime.now().year
    start_year = current_year - years
    
    query = f"{topic} AND {start_year}:{current_year}[DP]"
    return search_pubmed(query, max_results)


# Tool definitions for Anthropic API
pubmed_search_tool = {
    "name": "search_pubmed",
    "description": "Search PubMed for medical and biomedical research articles. Returns article titles, abstracts, authors, journal, and publication year. Use for general medical literature searches.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query for medical literature. Can include medical terms, conditions, treatments, etc. Example: 'sepsis treatment elderly', 'diabetes management guidelines'"
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of articles to return (default: 5, recommended max: 10 for quality)"
            }
        },
        "required": ["query"]
    }
}

clinical_guidelines_tool = {
    "name": "search_clinical_guidelines",
    "description": "Search specifically for clinical practice guidelines, systematic reviews, and meta-analyses. Use this when you need evidence-based treatment recommendations or established clinical protocols.",
    "input_schema": {
        "type": "object",
        "properties": {
            "condition": {
                "type": "string",
                "description": "Medical condition or clinical question. Example: 'hypertension', 'postoperative pain management'"
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of guidelines to return"
            }
        },
        "required": ["condition"]
    }
}

recent_research_tool = {
    "name": "search_recent_research",
    "description": "Search for recent research published within the last N years. Use this to find cutting-edge findings or latest developments in a medical topic.",
    "input_schema": {
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "Research topic or medical subject"
            },
            "years": {
                "type": "integer",
                "description": "How many years back to search (default: 5)"
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of articles to return"
            }
        },
        "required": ["topic"]
    }
}

# Tool mapping for agent
TOOL_MAPPING = {
    "search_pubmed": search_pubmed,
    "search_clinical_guidelines": search_clinical_guidelines,
    "search_recent_research": search_recent_research
}