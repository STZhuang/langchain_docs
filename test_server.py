from src.server import query_docs

def test_tool():
    print("Testing query_docs tool...")
    
    # Test 1: Basic Query
    q = "how to create a custom tool"
    print(f"\nQuery: {q}")
    result = query_docs(q)
    print(f"Result length: {len(result)}")
    print(f"Result snippet: {result[:200]}...")
    
    # Test 2: No results
    q = "xyz123notfound"
    print(f"\nQuery: {q}")
    result = query_docs(q)
    print(f"Result: {result}")

if __name__ == "__main__":
    test_tool()
