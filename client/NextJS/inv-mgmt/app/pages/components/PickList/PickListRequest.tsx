'use_client'

import {useState} from 'react';

import HttpService from '@/app/httpService';
import {serverError, displayAlert} from '@/app/appUtils';
import {MIN_AMOUNT,MAX_AMOUNT,MIN_CONCENTRATION,MAX_CONCENTRATION,
    AMOUNT_UNIT,CONCENTRATION_UNIT} from '@/app/constants';
import Alert from '@/app/pages/components/Modal/Alert/Alert';

// sample reagents:
    /*
    Child_X10000015-8
    Child_X10000017-8
    Child_X10000051-6
    Child_X10000101-7
    Child_X10000104-7
    Child_X10000164-9
    Child_X10000181-3
    Child_X10000254-8
    Child_X10000262-5
    Child_X10000304-9
    Child_X10000386-5
    Child_X10000535-2
    Child_X10000543-9
    Child_X10000649-5
    Child_X10000762-5
    Child_X10000892-2
    Child_X10000900-5
    Child_X10000914-2
    Child_X10001118-9
    Child_X10001221-2
    Child_X10001224-2
    Child_X10001393-7
    Child_X10001493-3
    Child_X10001541-4
    Child_X10001694-5
    Child_X10001704-8
    Child_X10001721-2
    Child_X10001741-6
    Child_X10001776-7
    Child_X10001806-4
*/

export interface PickListRequestProps {
  httpService?: HttpService;
  setPickData?: Function;

}

export default function PickListRequest({httpService,setPickData}) {
    function createEmptyFormData() {
        let data = [];
        for (let i = 1; i <= 10; ++i) {
            data.push({line_number: i, reagent: undefined, amount: undefined, concentration: undefined});
        }
        return data;
    }

    const emptyData = createEmptyFormData();
    const [formData,setFormData] = useState(createEmptyFormData());
    const [showModal,setShowModal] = useState(false),
          [dialogInfo,setDialogInfo] = useState({});


    // how you have to deal with arrays used in state
    function updateFormData(idx: number, field: string, value: any) {
        // first copy the form data into a new array
        let temp = [...formData];
        // set the value of the specified row
        temp[idx][field] = value;
        // now replace the form data
        setFormData(temp);
    }

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
        setShowModal(true);
      }

    function validateRows() {
        let errors: [] = [];
        formData.forEach((row,idx) => {
            let reagent = row.reagent,
                amount = row.amount,
                concentration = row.concentration;
            if (reagent) {
                reagent = reagent.trim();
            }
            console.log(idx,reagent,amount,concentration);
            // at this point amount and concentration CANNOT be zero!!
            if (reagent || amount || concentration) {
                // if blanked out, amount and concentration will be '', not null or undefined
                if (!reagent || !amount  || !concentration) {
                    errors.push('Data is incomplete on line ' + row.line_number);
                }
            }
        });
        return errors;
    }

    function unloadValues() {
        let valueArray: [] = [];
        formData.forEach((row,idx) => {
            let reagent = row.reagent,
                amount = row.amount,
                concentration = row.concentration;
            if (reagent) {
                reagent = reagent.trim();
            }
            if (reagent) { // paranoid
                let record = { reagent: reagent, amount: amount, concentration: concentration, lineNum: row.line_number };
                valueArray.push(record);
            }
        });
        return valueArray;
      }

    function doRequest(event) {
        event.preventDefault();
        let frm = document.getElementById('picklist-form'),
            // validate the amount and concentration values
            valid = frm.reportValidity();
        if (valid) {
            // form is valid as far as values.  now validate each row for completeness
            let errors = validateRows();
            if (errors.length > 0) {
                displayAlertDialog("Please fix the following errors:", errors);
                return;
            }
            // so far so good
            let values = unloadValues();
            if (values.length < 1) {
                displayAlertDialog("No values were entered !!!");
                return;
            }
            let response = httpService.pickList(values);
            response.then((result) => {
                try {
                    let jsonData = JSON.parse(result.text);
                    if (jsonData.success) {
                        let resultData = jsonData.data;
                        console.log(resultData);
                        let available_samples = jsonData.data.available,
                            unavailable_samples = jsonData.data.unavailable;
                        if (available_samples == null || unavailable_samples == null) {
                            console.dir(jsonData);
                            displayAlertDialog("Did not get back lists of available and unavailable samples");
                          }
                          else {
                            if (available_samples.length < 1) {
                              displayAlertDialog("No samples were available");
                            }
                            else {
                                setPickData(jsonData.data);
                            }
                          }
                    }
                    else {
                        displayAlertDialog("Pick list request failed", jsonData.errors); 
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

    // NOTE - the fporm is rendered EVERY time we press a key in the input fields!!!  looks like no way to stop it.
    // we need to use a state var to retain the values for when we return to the request.  using onBlur does not work.
    // maybe put the state var in the parent?????
    return (
        <div>
        <form id='picklist-form' onSubmit={(e) => doRequest(e)}>
            <table className="requestTable">
                <thead>
                    <tr>
                        <th></th>
                        <th>Reagent</th>
                        <th>Amount {AMOUNT_UNIT}</th>
                        <th>Concentration {CONCENTRATION_UNIT}</th>
                    </tr>
                </thead>
                <tbody>
                    {/* note - we use map here because it returns the array of the html rendering */}
                    {formData.map((row,idx) => (
                        <tr key={row.line_number}>
                            <td>{row.line_number}</td>
                            <td>
                                <input type="text" value={row.reagent}
                                    onChange={(e) => updateFormData(idx, "reagent", e.target.value)}
                                />
                            </td>
                            <td>
                                <input type="number" className="no-spinners" min={MIN_AMOUNT} max={MAX_AMOUNT}
                                    value={row.amount}
                                    onChange={(e) => updateFormData(idx, "amount", e.target.value)}
                                />
                            </td>
                            <td>
                            <input type="number" className="no-spinners" min={MIN_CONCENTRATION} max={MAX_CONCENTRATION}
                                    value={row.concentration}
                                    onChange={(e) => updateFormData(idx, "concentration", e.target.value)}
                                />
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
            <br/>
            <p className="importantMessage">For any line, all fields are required</p>
            <p className="buttonRow">
                <button className="normalButton" type="submit">Request</button>
            </p>
        </form>
        <Alert dialogInfo={dialogInfo} showModal={showModal} setShowModal={setShowModal}/>
        </div>
    );
}