import './App.css';
import data from "./result.json";
import Collapsible from 'react-collapsible';

const anumLink = (anum, includeName = true) => {
  const url = `https://oeis.org/${anum}`
  return <>
    <a href={url} target="_blank" onClick={event => {
      event.stopPropagation();
    }}>{anum}</a>
    {
      includeName && <>
        :&nbsp;
        {data.sequences[anum].name}
      </>
    }

  </>;
}

const TermsTable = ({terms, anums}) =>
  <>
    <p>
      Cells shaded in grey indicate that the term exists somewhere
      in the sequence indicated by the column.
    </p>
    <table>
      <thead>
      <tr>
        <th/>
        {anums.map(anum => <th key={anum}>{anum}</th>)}
      </tr>
      </thead>
      <tbody>
      {terms.map((term, termIndex) => <tr key={termIndex}>
        <th>{term}</th>
        {anums.map(anum => <td key={anum}
                               className={data.sequences[anum].terms.indexOf(term) === -1 ? "" : "highlight-cell"}/>)}
      </tr>)}
      </tbody>
    </table>
  </>

const App = () => (
  <div className="App">
    <h1>OEIS explorer</h1>
    <p>
      This is a tool for exploring two different kinds of relationships between sequences
      in the <a href="https://oeis.org/">OEIS</a>: mentions (links) of other sequences on a sequence's page,
      and large numbers that appear in multiple different sequences.
    </p>
    <p>
      Below is a list of groups of sequences. The groups connect sequences that have some large terms in common.
      You can see all the terms that appear in at least two of the sequences by clicking on 'Common terms'
      which will expand to show a table.
    </p>
    <p>
      Groups are divided into subgroups. All the sequences in a subgroup are related to each other according
      mentions in the OEIS. This is used an indication that the relationship between these sequences is
      already known by some people.
    </p>
    <p>
      On the other hand, sequences in different subgroups don't have a path between them in the OEIS,
      or any such path is quite obscure. The fact that they share some common terms could mean:
    </p>
    <ul>
      <li>Some links should be added to the OEIS pages</li>
      <li>Some undiscovered mathematics connects these sequences and should be researched</li>
      <li>An amusing mathematical coincidence with no deeper meaning</li>
    </ul>
    <p>
      You can also click on a sequence name to learn more about the sequence, including how it relates to
      other sequences both in terms of OEIS mentions and common terms.
    </p>
    <p>
      The source code for this page can be found <a href="https://github.com/alexmojaki/oeis-explorer">here</a>.
    </p>
    {data.groups.map((group, groupIndex) =>
      <div className="panel" key={groupIndex}>
        {group.subgroups.map((subgroup, subgroupIndex) =>
          <div className="panel" key={subgroupIndex}>
            {subgroup.nodes.map((seq) =>
              <Collapsible trigger={anumLink(seq.anum)} key={seq.anum} lazyRender>
                {
                  seq.paths.length > 0 &&
                  <>
                    <h3>Nearest nodes:</h3>
                    <p>
                      Sequences are treated as nodes in a graph, with an edge connecting them
                      if the OEIS page of one sequence mentions the other somewhere.
                      The graph is not connected, so each group is divided into subgroups
                      according to the connected component of the graph containing those nodes.
                    </p>
                    <p>
                      The graph is undirected, so two nodes being connected doesn't necessarily mean that you can start
                      on one page and click links until you reach the other page.
                    </p>
                    <p>
                      This list shows the shortest distance in the graph from this sequence
                      to all the other sequences in this subgroup.
                      Click on a sequence to see the intermediate nodes on one of the shortest paths to it.
                    </p>
                    {seq.paths.map((path) =>
                      <details key={path.anum}>
                        <summary>
                          {path.path.length} node(s) in between: {anumLink(path.anum)}
                        </summary>
                        <ul>
                          {
                            path.path.map((pathAnum, pathItemIndex) =>
                              <li key={pathItemIndex}>
                                {anumLink(pathAnum)}
                              </li>
                            )
                          }
                        </ul>

                      </details>
                    )}
                  </>
                }
                {
                  seq.neighbours.length > 0 &&
                  <>
                    <h3>All neighbours</h3>
                    <p>
                      These are all the neighbours of this sequence in the graph,
                      i.e. all the sequences either mentioned directly in this sequence's
                      page or that mention this sequence in their own page.
                    </p>
                    {
                      <ul>
                        {
                          seq.neighbours.map((neighbour, neighbourIndex) =>
                            <li key={neighbourIndex}>
                              {anumLink(neighbour)}
                            </li>
                          )
                        }
                      </ul>
                    }
                  </>
                }
                <h3>Terms:</h3>
                <p>
                  This table shows all the terms at the start of this sequence that are mentioned
                  directly in the OEIS page. The page may have a link to more terms in a b-file.
                </p>
                <TermsTable terms={data.sequences[seq.anum].terms} anums={group.group}/>
              </Collapsible>
            )}
            {/*
            // Too expensive!
            {
              subgroup.on_shortest_paths.length > 0 &&
              <Collapsible trigger="Other related sequences:" lazyRender>
                <p>
                  Sequences that appear on a shortest path between any two nodes in this subgroup:
                </p>
              </Collapsible>
            }
            */}
          </div>
        )}
        <Collapsible trigger="Common terms:" lazyRender>
          <p>
            This shows all terms that appear in at least two sequences in this group, in increasing order.
          </p>
          <TermsTable terms={group.common_terms} anums={group.group}/>
        </Collapsible>
      </div>
    )}
  </div>
);

export default App;
