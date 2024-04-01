'use client'

import {useState}  from 'react';

import HttpService from '@/app/httpService';
import {MIN_BARCODE_LENGTH,MIN_AMOUNT,MAX_AMOUNT,MIN_CONCENTRATION,MAX_CONCENTRATION,
    AMOUNT_UNIT,CONCENTRATION_UNIT} from '@/app/constants';
import Alert from '@/app/pages/components/Modal/Alert/Alert';

export interface AddVialProps {
  httpService?: HttpService;
}

export default function AddVial({httpService}) {

  let [showModal,setShowModal] = useState(false),
      // we'll pack all dialog info (title and messages) in one object so we don't have so many params to pass.
      // this will become important in the Confirm
      [dialogInfo,setDialogInfo] = useState({});

  const [formData, setFormData] = useState({
    barcode: "",
    lot: "",
    amount: 0,
    amount_unit: AMOUNT_UNIT,
    concentration: 0,
    concentration_unit: CONCENTRATION_UNIT
  });

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
  

  function submitAddVial(event: any) {
    console.log("*** event " + event);
    event.preventDefault();

    // it seems the form is only submitted if valid, so we only get here if the form ins valid
    let response = httpService.addVial(formData);
    response.then((result) => {
      console.log(result);
      try {
        let jsonData = JSON.parse(result.text);
        if (jsonData.success) {
          displayAlertDialog("Vial successfully added!!!");
        }
        else {
          displayAlertDialog("Add vial failed", jsonData.errors); 
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

  return (
    <div className="main-panel">
        <form id="addVialForm" method='POST' onSubmit={(e) => submitAddVial(e)}>
            <table>
                <tr>
                    <td className="formFieldLabel">
                        <label htmlFor="addvial-barcode">Barcode (min {MIN_BARCODE_LENGTH} chars):</label></td>
                    <td className="formField">
                        <input type="text" id="addVial-barcode" name="barcode" minLength={MIN_BARCODE_LENGTH} 
                          onChange={(e) => setFormData({...formData, barcode: e.target.value})}
                          required />
                    </td>
                </tr>
                <tr>
                    <td className="formFieldLabel">Lot name:</td>
                    <td className="formField">
                        <input type="text" name="lot" onChange={(e) => setFormData({...formData, lot: e.target.value})}
                          required/>
                    </td>
                </tr>
                <tr>
                    <td className="formFieldLabel">Amount ({AMOUNT_UNIT}):</td>
                    <td className="formField">
                        <input type="number" className="no-spinners" name="amount" min={MIN_AMOUNT} max={MAX_AMOUNT} 
                          onChange={(e) => setFormData({...formData, amount: parseFloat(e.target.value)})}
                            required /> 
                        <input type="hidden" name="amount_unit" value="{AMOUNT_UNIT}" />
                    </td>
                </tr>
                <tr>
                    <td className="formFieldLabel">Concentration ({CONCENTRATION_UNIT}):</td>
                    <td className="formField">
                        <input type="number" className="no-spinners" min={MIN_CONCENTRATION} max={MAX_CONCENTRATION}
                          onChange={(e) => setFormData({...formData, concentration: parseFloat(e.target.value)})}
                            name="concentration" required />
                        <input type="hidden" name="concentration_unit" value="{CONCENTRATION_UNIT}"/>
                    </td>
                </tr>
            </table>
            <p className="importantMessage">ALL Fields are required</p>
            <button className="normalButton" type="submit">Save It</button>
        </form>
        <Alert dialogInfo={dialogInfo} showModal={showModal} setShowModal={setShowModal}/>
    </div>
  )
}
