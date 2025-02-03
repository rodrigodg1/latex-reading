from flask import Flask, render_template, request, jsonify
import bibtexparser
import re
import requests
import subprocess
import ollama
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

bib_database = None

@app.route('/', methods=['GET', 'POST'])
def index():
    global bib_database
    tex_content_html = ""
    citation_details = {}
    error_message = None

    if request.method == 'POST':
        bib_file = request.files['bib_file']
        tex_file = request.files['tex_file']

        if not bib_file or not tex_file:
            error_message = "Please upload both a .bib and a .tex file."
        else:
            try:
                bib_str = bib_file.read().decode('utf-8')
                bib_database = bibtexparser.loads(bib_str)

                tex_str = tex_file.read().decode('utf-8')
                tex_content_html = process_tex_content(tex_str, bib_database)

            except Exception as e:
                error_message = f"Error processing files: {e}"
                bib_database = None  # Reset bib_database on error

    return render_template('index.html',
                           tex_content_html=tex_content_html,
                           citation_details=citation_details,
                           error_message=error_message)

def process_tex_content(tex_str, bib_database):
    """Processes LaTeX content, finds citations, and creates clickable links."""
    citation_pattern = r"\\cite\{([^}]+)\}"
    citation_details_map = {}
    last_pos = 0
    html_parts = []

    for match in re.finditer(citation_pattern, tex_str):
        citation_keys_str = match.group(1)
        citation_keys = [key.strip() for key in citation_keys_str.split(',')] # Handle multiple keys

        # Add text before the citation
        html_parts.append(tex_str[last_pos:match.start()])

        citation_links_html = []
        for key in citation_keys:
            citation_links_html.append(f'<a href="#" class="citation-link" data-citation-key="{key}" style="color: blue; text-decoration: underline;">{key}</a>')

        html_parts.append(f'\\cite{{{" ".join(citation_links_html)}}}') # Reconstruct \cite with links
        last_pos = match.end()

    # Add remaining text after last citation
    html_parts.append(tex_str[last_pos:])

    return "".join(html_parts)


@app.route('/get_citation_detail/<path:citation_key>')
def get_citation_detail(citation_key):
    global bib_database
    print(f"get_citation_detail route called for key: {citation_key}") # Debug print

    if not bib_database:
        print("bib_database is None. Returning error.") # Debug print
        return jsonify({'error': 'No BibTeX file loaded.'}), 400

    details = _fetch_citation_details(citation_key, bib_database)
    if details:
        print(f"Citation details found for key: {citation_key}: {details}") # Debug print
        return jsonify({'citation_info': details})
    else:
        print(f"Citation details NOT found for key: {citation_key}") # Debug print
        return jsonify({'error': 'Citation information not found for key: ' + citation_key}), 404


import requests
import re

def _fetch_citation_details(citation_key, bib_database):
    """Retrieves citation details from bib_database for a given key and fetches citation count and abstract summary using DOI if selected."""
    print(f"_fetch_citation_details called for key: {citation_key}") # Debug print
    if bib_database and bib_database.entries:
        print(f"bib_database has entries. Searching for key: {citation_key}") # Debug print
        for entry in bib_database.entries:
            if entry['ID'] == citation_key:
                print(f"Found matching entry for key: {citation_key}. Entry ID: {entry['ID']}") # Debug print
                doi = entry.get('doi', 'N/A')
                title = entry.get('title', 'N/A')
                year = entry.get('year', 'N/A')
                author = entry.get('author', 'N/A')
                journal = entry.get('journal', 'N/A')
                citation_count = "N/A"
                #abstract_summary = "N/A"
                
                # Fetch citation count only if verification is enabled and DOI is available
                if  doi != 'N/A':
                    citation_count = _fetch_citation_count(doi)
                    abstract_summary = _fetch_abstract_summary(doi)
                    #abstract_summary_llm = _summarize_text_llm(abstract_summary)
                    
                
                details = {
                    "doi": doi,
                    "title": title,
                    "year": year,
                    "author": author,
                    "journal": journal,
                    "citation_count": citation_count,
                    "abstract_summary": abstract_summary,
                   # "abstract_summary_llm": abstract_summary_llm
                }
                print(f"Returning details: {details}") # Debug print
                return details
        print(f"No matching entry found for key: {citation_key} in bib_database entries.") # Debug print
    else:
        print("bib_database is None or has no entries.") # Debug print
    return None

def _fetch_citation_count(doi):
    """Fetches citation count from external API using DOI."""
    try:
        url = f"https://api.crossref.org/works/{doi}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('message', {}).get('is-referenced-by-count', 'N/A')
    except requests.RequestException as e:
        print(f"Error fetching citation count: {e}")
    return "N/A"

def _fetch_abstract_summary(doi):
    """Fetches the research abstract and summarizes it using LLM API."""
    try:
        url = f"https://api.semanticscholar.org/v1/paper/{doi}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            abstract = data.get('abstract', 'N/A')
            if abstract != 'N/A':
                #return _summarize_text(abstract)
                return abstract
    except requests.RequestException as e:
        print(f"Error fetching abstract: {e}")
    return "N/A"



# def _summarize_text_llm(text):
#     """Summarizes the given text using a local Ollama model inside Docker."""
#     try:
#         ollama_host = os.getenv("OLLAMA_HOST", "http://ollama:11434")  # Connect to Ollama container

#         # Check if the model is available before running
#         available_models = ollama.list()
#         if not any(model["name"] == "deepseek-r1:14b" for model in available_models["models"]):
#             print("Error: Model 'deepseek-r1:14b' is not available. Make sure it is pulled.")
#             return "N/A"

#         response = ollama.chat(
#             model="deepseek-r1:14b",
#             messages=[{"role": "user", "content": f"Summarize the following research abstract:\n{text}"}]
#         )
#         return response["message"].get("content", "N/A").strip()
#     except Exception as e:
#         print(f"Error summarizing text with Ollama (deepseek-r1:14b): {e}")
#     return "N/A"

def remove_tex_comments(tex_str):
    """Removes all LaTeX comments from the .tex file content."""
    return re.sub(r'%.*', '', tex_str)




def process_tex_content(tex_str, bib_database):
    """Processes LaTeX content, removes comments, finds citations, and creates clickable links with different colors for citation commands."""
    tex_str = remove_tex_comments(tex_str)  # Remove comments
    citation_styles = {
        r"(\\cite)\{([^}]+)\}": "color: blue;",
        r"(\\citep)\{([^}]+)\}": "color: blue;",
        r"(\\citet)\{([^}]+)\}": "color: blue;",
        r"(\\citeauthor)\{([^}]+)\}": "color: blue;",
        r"(\\citeyear)\{([^}]+)\}": "color: blue;",
        r"(\\citealp)\{([^}]+)\}": "color: blue;"
    }
    
    last_pos = 0
    html_parts = []
    matches = []
    
    for pattern in citation_styles.keys():
        for m in re.finditer(pattern, tex_str):
            matches.append((m, pattern))
    
    matches.sort(key=lambda x: x[0].start())  # Ensure order of matches
    
    for match, pattern in matches:
        citation_command = match.group(1)  # Extract the citation command (e.g., \citep)
        citation_keys_str = match.group(2)
        citation_keys = [key.strip() for key in citation_keys_str.split(',')]  # Handle multiple keys
        citation_style = citation_styles[pattern]
    
        # Add text before the citation
        html_parts.append(tex_str[last_pos:match.start()])
    
        citation_links_html = []
        for key in citation_keys:
            citation_links_html.append(f'<a href="#" class="citation-link" data-citation-key="{key}" style="{citation_style} text-decoration: underline;">{key}</a>')
    
        html_parts.append(f'<span style="{citation_style}">{citation_command}</span>' + f'{{{" ".join(citation_links_html)}}}')  # Reconstruct with styled citation command
        last_pos = match.end()
    
    # Add remaining text after last citation
    html_parts.append(tex_str[last_pos:])
    
    return "".join(html_parts)

















if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)
