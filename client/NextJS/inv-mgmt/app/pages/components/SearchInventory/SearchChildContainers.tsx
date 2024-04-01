'use_client'

export interface SearchChildContainersProps {
    selectedContainer?: any;
    setSelectedBarcode?: Function;
  }

export default function SearchChildContainers({selectedContainer, setSelectedBarcode}) {

    function containerIsParent() {
        return selectedContainer != null && selectedContainer.containers != undefined;
    }

    function containerHasChildren() {
        return (selectedContainer != null && selectedContainer.containers != undefined && selectedContainer.containers.length > 0);
    }

    function tableRowClicked(cont:any) {
        console.log("*** you clicked " + cont);
        if (cont?.barcode) {
            setSelectedBarcode(cont.barcode);
        }
    }
    
    return (
        <div hidden={!containerIsParent()}>
            <div hidden={containerHasChildren()}>
                <h1>There are no child containers</h1>
            </div>    
            <div hidden={!containerHasChildren()}>
                <h3>Click on a row to see the contents of that container</h3>
                <table className="containerTable">
                    <colgroup>
                        <col width="100px"/>
                        <col width="150px"/>
                        <col width="100px"/>
                    </colgroup>
                    <thead>
                        <tr>
                            <th>Barcode</th>
                            <th>Container Type</th>
                            <th>Position</th>
                            <th>Reagent</th>
                        </tr>
                    </thead>
                    <tbody>
                        {selectedContainer?.containers?.map((cont) => (
                            <tr key={cont.id} className="containerTableRow" onClick={()=>tableRowClicked(cont)}>
                                <td>{(cont.barcode) ? cont.barcode : 'EMPTY'}</td>
                                <td>{cont.container_type}</td>
                                <td>{cont.position}</td>
                                <td>{cont.reagent}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    )
  }