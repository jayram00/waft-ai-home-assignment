# Helper kept minimal – logic lives in Router.network()
def to_cytoscape(graph):
    return {
        "elements": {
            "nodes": [{"data": n} for n in graph.get("nodes", [])],
            "edges": [{"data": e} for e in graph.get("edges", [])],
        }
    }
