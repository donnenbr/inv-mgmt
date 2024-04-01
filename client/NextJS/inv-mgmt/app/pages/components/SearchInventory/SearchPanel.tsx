'use_client'

import {useState, useEffect}  from 'react';

import HttpService from '@/app/httpService';
import {MIN_AMOUNT,MAX_AMOUNT,MIN_CONCENTRATION,MAX_CONCENTRATION,
    AMOUNT_UNIT,CONCENTRATION_UNIT} from '@/app/constants';
import Alert from '@/app/pages/components/Modal/Alert/Alert';
import Confirm from '@/app/pages/components/Modal/Confirm/Confirm';


export interface SearchPanelProps {
  httpService?: HttpService;
  selectedBarcode?: string|null;
  setSelectedContainer?: Function;
}

export default function SearchPanel({httpService, selectedBarcode, setSelectedContainer}) {
    // to be filled in when we load a vial
    type FormDataType = {
        id: number|null,
        search_barcode: string|null,
        barcode: string|null,
        container_type: string|null,
        location: string|null,
        reagent: string|null,
        lot: string|null,
        amount: string|number|null,
        amount_unit: string|null,
        concentration: string|number|null,
        concentration_unit: string|null
      }
    let formValues: FormDataType = {
        id: null,
        // the barcode used for search, which the user can change
        search_barcode: "",
        // that for the container.  we will ONLY change the amount and concentration and not the units.
        barcode: "",
        container_type: "",
        location: "",
        reagent: "",
        lot: "",
        amount: 0,
        amount_unit: AMOUNT_UNIT,
        concentration: 0,
        concentration_unit: CONCENTRATION_UNIT
    };
    const [formData, setFormData] = useState(formValues);

    let [showAlertModal,setShowAlertModal] = useState(false),
        [showConfirmModal,setShowConfirmModal] = useState(false),
        [dialogInfo,setDialogInfo] = useState({});


    var currentBarcode: string|null = null;
    const amountField = 'search-amount',
          concentrationField = 'search-concentration',
          searchBarcodeField = 'search-barcode';

    useEffect( () => {
        console.log("*** sel barcode useEffect - " + selectedBarcode + ", current " + currentBarcode);
        if (selectedBarcode !== null && selectedBarcode !== currentBarcode) {
            console.log("*** barcode has changed");
            setFormData({...formData, search_barcode: selectedBarcode});
            searchBarcode(selectedBarcode);
        }
     }, [selectedBarcode]);

    function displayAlertDialog(title: string, messages: [string]|string|null = null) {
        let dlgInfo = {title: title, messages: [""]}; 
        if (messages) {
          if (!Array.isArray(messages)) {
            messages = [messages];
          }
          dlgInfo.messages = messages;
        }
        else {
          dlgInfo.messages = [];
        }
        setDialogInfo(dlgInfo);
        setShowAlertModal(true);
    }

    function displayConfirmDialog(title: string, messages: [string]|string|null = null, yesHandler: Function|null = null) {
        // NOTE - the "caller" of the yes handler is the current "main" function.
        // there is no "this"
        let dlgInfo = {title: title, messages: [""], yesHandler: yesHandler, caller: SearchPanel}; 
        if (messages) {
          if (!Array.isArray(messages)) {
            messages = [messages];
          }
          dlgInfo.messages = messages;
        }
        else {
          dlgInfo.messages = [];
        }
        setDialogInfo(dlgInfo);
        setShowConfirmModal(true);
    }

    function updateContainer(event: any) {
        let frm = document.getElementById('searchPanelForm');
        if (frm.reportValidity()) {
            let vialData = {
                id: formData.id,
                container_type: formData.container_type,
                barcode: formData.barcode,
                lot: formData.lot,
                amount: formData.amount,
                amount_unit: formData.amount_unit,
                concentration: formData.concentration,
                concentration_unit: formData.concentration_unit
            };
            let response = httpService.updateVial(vialData);
            response.then((result) => {
                try {
                    let jsonData = JSON.parse(result.text);
                    if (jsonData.success) {
                        // nothing should change, but ...
                        let containerData = jsonData.data;
                        setFormData({...formData, 
                            id: containerData.id,
                            search_barcode: containerData.barcode,
                            barcode: containerData.barcode,
                            container_type: containerData.container_type,
                            location: containerData.position,
                            reagent: containerData.reagent,
                            lot: (containerData.lot == undefined ? "" : containerData.lot),
                            amount: (containerData.amount == null ? 0 : containerData.amount),
                            concentration: (containerData.concentration == null ? 0 : containerData.concentration),
                        });
                        setSelectedContainer(containerData);
                        displayAlertDialog("Update successful!!!");
                    }
                    else {
                        displayAlertDialog("Update vial failed", jsonData.errors); 
                    }
                }
                catch (ex) {
                    // can't use Promise.reject here (because of the resolutions???  no next step????)
                    // throw an exception
                    throw("Error code " + result.status + " : " + result.statusText);
                }
            })
            // upon reject, we end here!!!
            .catch((error: any) => {
                displayAlertDialog("An error occurred", error);
            });
        }
    }


    function deleteContainer(event) {
        console.log("*** current func " + SearchPanel);
        displayConfirmDialog("Do you really want to delete his container ???", "There ain't no going back!", doDelete);
        return;
    }

    function doDelete() {
        let response = httpService.deleteVial(formData.id);
        response.then((result) => {
            try {
                let jsonData = JSON.parse(result.text);
                if (jsonData.success) {
                    // we'll just leave everything.
                    displayAlertDialog("Vial successfully deleted !!!");
                }
                else {
                    displayAlertDialog("Delete vial failed", jsonData.errors); 
                }
            }
            catch (ex) {
                // can't use Promise.reject here (because of the resolutions???  no next step????)
                // throw an exception
                throw("Error code " + result.status + " : " + result.statusText);
            }
        })
        // upon reject, we end here!!!
        .catch((error: any) => {
            displayAlertDialog("An error occurred", error);
        });
    }

    function disableFieldValidation(frm: any, disabled: boolean) {
        try {
            frm[amountField].disabled = disabled;
            frm[concentrationField].disabled = disabled;
        }
        catch (exc) {
            alert(exc);
        }
    }

    // although rather obsessive, we do NOT want to validate the amount and concentration fields when
    // doing a search.  they'd only be validated when visible.  that "noformvalidate" or "formnovalidate"
    // shit does not seem to work, so we disable the fields during the search and reenable them when the
    // search is done.  we also use the form's reportValidity() function to do the validation as it 
    // also will flag the fields on the page!!!
    function doSearch(event: any) {
        event.preventDefault();
        let frm = document.getElementById('searchPanelForm');
        try {
            disableFieldValidation(frm, true);
            let valid = frm.reportValidity();
            console.log("*** valid " + valid);
            if (valid) {
                searchBarcode(formData.search_barcode);
            }
        }
        catch (exc) {
            displayAlertDialog("search failed", exc);
        }finally {
            disableFieldValidation(frm, false);
        }
    }
    function searchBarcode(barcode:string|null) {
        console.log("*** search barcode " + barcode);
        let response = httpService.getContainerByBarcode(barcode);
        response.then((result) => {
            if (result.status == 404) {
                // throw("Barcode is invalid");
                displayAlertDialog("That barcode is invalid!");
                return;
            }
            console.log(result);
            try {
                let jsonData = JSON.parse(result.text);
                console.log(jsonData);
                if (jsonData.success) {
                    let containerData = jsonData.data;
                    // NOTE - if a value comes back as null, the formData value WILL NOT CHANGE!!!
                    // dr bobby thinks that is because null is no value so nothing can be equal to, or not
                    // equal to, null.  so, we make them blanks.  note we use == to cover the bases of null or undefined.
                    setFormData({...formData, 
                        id: containerData.id,
                        search_barcode: containerData.barcode,
                        barcode: containerData.barcode,
                        container_type: containerData.container_type,
                        location: (containerData.position == null ? "" : containerData.position),
                        reagent: containerData.reagent,
                        lot: (containerData.lot == null ? "" : containerData.lot),
                        amount: (containerData.amount == null ? 0 : containerData.amount),
                        concentration: (containerData.concentration == null ? 0 : containerData.concentration),
                    });
                    setSelectedContainer(containerData);

                }
                else {
                    displayAlertDialog("Search failed", jsonData.errors); 
                }
            }
            catch (ex) {
                // can't use Promise.reject here (because of the resolutions???  no next step????)
                // throw an exception
                throw("Error code " + result.status + " : " + result.statusText);
            }
        })
        // upon reject, we end here!!!
        .catch((error: any) => {
            displayAlertDialog("An error occurred", error);
        });
    }
    
    // note that we just use the buttons' onClick event for everything and disable submission of the
    // form.  this is because submit would validate the fields BEFORE doSearch is called and would
    // validate fields we want to skip when searching.
    return (
        <div>
    <form id="searchPanelForm" onSubmit={(e) => {false}}>
        <table>
            {/* i am a comment for you */}
            <tr>
                <td className="formFieldLabel">Barcode:</td>
                <td className="formField">
                    <input type="text" id={searchBarcodeField} value={formData.search_barcode} 
                        onChange={(e) => setFormData({...formData, search_barcode: e.target.value})}
                        required/>
                </td>
                <td></td>
                <td>
                    <button className="normalButton" onClick={(e) => doSearch(e)}>Search</button>
                </td>
            </tr>
            <tr>
                <td className="formFieldLabel">Container Type:</td>
                <td className="formField">
                    <input type="text" readOnly id="search-container-type" value={formData.container_type}/>
                </td>
            </tr>
            <tr>
                <td className="formFieldLabel">Location:</td>
                <td className="formField">
                    <input type="text" readOnly id="search-location" value={formData.location}/>
                </td>
            </tr>
            <tr hidden={!formData.lot}>
                <td className="formFieldLabel">Reagent Name:</td>
                <td className="formField">
                    <input type="text" readOnly id="search-reagent" value={formData.reagent}/>
                </td>
            </tr>
            <tr hidden={!formData.lot}>
                <td className="formFieldLabel">Lot Name:</td>
                <td className="formField">
                    <input type="text" readOnly id="search-lot" value={formData.lot}/>
                </td>
            </tr>
            <tr hidden={!formData.lot}>
                <td className="formFieldLabel">Amount ({AMOUNT_UNIT}):</td>
                <td className="formField">
                    <input type="number" className="no-spinners" min={MIN_AMOUNT} max={MAX_AMOUNT}
                        required id={amountField} value={formData.amount} 
                        onChange={(e) => setFormData({...formData, amount: e.target.value})}
                    />
                    <input type="hidden" id="search-amount_unit" value="{AMOUNT_UNIT}"/>
                </td>
            </tr>
            <tr hidden={!formData.lot}>
                <td className="formFieldLabel">Concentration ({CONCENTRATION_UNIT}):</td>
                <td className="formField">
                    <input type="number" className="no-spinners" min={MIN_CONCENTRATION} max={MAX_CONCENTRATION} 
                        required id={concentrationField} value={formData.concentration} 
                        onChange={(e) => setFormData({...formData, concentration: e.target.value})}
                    />
                    <input type="hidden" id="search-concentration_unit" value="{CONCENTRATION_UNIT}"/>
                </td>
            </tr>
        </table>
    </form>
    <p hidden={!formData.lot} className="importantMessage">
        You can only change the amount and concentration.<br/>
        You cannot change the barcode.
    </p>
    <div hidden={!formData.lot} className="buttonRow">
        {/* you CANNOT do these actions if you changed the barcode after a search !!! */}
        <button className="normalButton" disabled={formData.barcode != formData.search_barcode}
            onClick={(e)=>updateContainer(e)}>Update</button>
        <span className="spacerSmall"/>
        <button className="normalButton" disabled={formData.barcode != formData.search_barcode} 
            onClick={(e) => deleteContainer(e)}>Delete</button>
    </div>
    <Alert dialogInfo={dialogInfo} showModal={showAlertModal} setShowModal={setShowAlertModal}/>
    <Confirm dialogInfo={dialogInfo} showModal={showConfirmModal} setShowModal={setShowConfirmModal}/>
</div>
    )
  }