from mcp.server.fastmcp import FastMCP
import os
import glob
from typing import List, Dict
from src.config import DOCS_DIR

# Initialize FastMCP
mcp = FastMCP("langchain-docs")

DOCS_DIR = str(DOCS_DIR)

# Global cache for documents
DOCS_CACHE: List[Dict] = []

def load_docs():
    """Load all markdown files into memory."""
    global DOCS_CACHE
    if DOCS_CACHE:
        return
        
    print(f"Loading docs from {DOCS_DIR}...")
    files = glob.glob(os.path.join(DOCS_DIR, "*.md"))
    
    for filepath in files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                
            filename = os.path.basename(filepath)
            
            # Extract title (simple heuristic)
            title = filename.replace(".md", "").replace("_", " ").title()
            lines = content.split('\n')
            for line in lines[:20]:
                if line.startswith("title: "):
                    title = line.replace("title: ", "").strip()
                    break
                elif line.startswith("# "):
                    title = line.replace("# ", "").strip()
                    break
            
            # Remove Frontmatter for searching
            searchable_content = content
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) > 2:
                    searchable_content = parts[2]
            
            DOCS_CACHE.append({
                'path': filepath,
                'filename': filename,
                'title': title,
                'content': content,
                'searchable_content': searchable_content.lower()
            })
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            
    print(f"Loaded {len(DOCS_CACHE)} documents.")

def search_docs(query: str, limit: int = 5) -> List[str]:
    """
    Search the in-memory cache.
    """
    # Ensure docs are loaded
    load_docs()
    
    query = query.lower().strip()
    terms = query.split()
    results = []
    
    for doc in DOCS_CACHE:
        score = 0
        
        # Title Matches
        if query in doc['title'].lower():
            score += 20
        
        # Exact Phrase Match
        if query in doc['searchable_content']:
            score += 10
            
        # Term Matches
        for term in terms:
            count = doc['searchable_content'].count(term)
            score += count
            
        if score > 0:
            results.append((score, doc))
            
    # Sort by score desc
    results.sort(key=lambda x: x[0], reverse=True)
    
    # Format output
    output = []
    for score, doc in results[:limit]:
        # Create snippet
        # Find first occurrence of query term
        content = doc['content'] # Original content
        search_lower = doc['searchable_content']
        
        idx = -1
        # Try to find phrase first
        idx = search_lower.find(query)
        # Fallback to first term
        if idx == -1 and terms:
            idx = search_lower.find(terms[0])
            
        # 200 chars context
        start = max(0, idx - 200)
        end = min(len(content), idx + 800)
        snippet = "..." + content[start:end] + "..." if idx != -1 else content[:1000]
        
        output.append(f"## {doc['title']} (Score: {score})\nSource: {doc['filename']}\n\n{snippet}\n")
        
    return output

@mcp.tool()
def query_docs(query: str) -> str:
    """
    Search the LangChain Python documentation for a given query.
    Returns the top 5 relevant documentation snippets with source references.
    Example queries: "how to use output parser", "LangChain expression language", "chain of thought".
    """
    matches = search_docs(query)
    if not matches:
        return "No documentation found for that query."
    
    return "\n---\n".join(matches)

if __name__ == "__main__":
    # Load docs eagerly when running as script
    load_docs()
    mcp.run()
