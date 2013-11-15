import igraph
dg = igraph.Graph(directed=True)
dg.add_vertices(7)
dg.add_edges([(1,0),(2,0),(4,2),(3,1),(5,3),(5,0),(6,0),(6,5),(6,4)])
topo_order = dg.topological_sorting(mode = 'IN')

longest_path = [0] * len(topo_order)

print topo_order

#sg = dg.induced_subgraph([0,1,2,7],implementation='create_from_scratch')


for v in topo_order:
    for w in dg.vs[v].neighbors(mode = 'IN'):
        longest_path[w.index] = max(longest_path[w.index], 1 + longest_path[v])

#print longest_path