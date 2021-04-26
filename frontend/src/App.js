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

const TermsTable = ({terms, anums}) => <table>
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


const App = () => (
  <div className="App">
    {data.groups.map((group, groupIndex) =>
      <div className="panel" key={groupIndex}>
        {group.subgroups.map((subgroup, subgroupIndex) =>
          <div className="panel" key={subgroupIndex}>
            {subgroup.map((seq) =>
              <Collapsible trigger={anumLink(seq.anum)} key={seq.anum} lazyRender>
                {
                  seq.paths.length > 0 &&
                  <>
                    <h3>Nearest nodes:</h3>
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
                <h3>Terms:</h3>
                <TermsTable terms={data.sequences[seq.anum].terms} anums={group.group}/>
              </Collapsible>
            )}
          </div>
        )}
        <Collapsible trigger="Common terms:" lazyRender>
          <TermsTable terms={group.common_terms} anums={group.group}/>
        </Collapsible>
      </div>
    )}
  </div>
);

export default App;
