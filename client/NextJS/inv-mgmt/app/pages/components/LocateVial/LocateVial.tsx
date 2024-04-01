'use_client'

import {useState}  from 'react';

import HttpService from '@/app/httpService';
import Alert from '@/app/pages/components/Modal/Alert/Alert';

export interface LocateVialProps {
  httpService?: HttpService;
}

export default function LocateVial({httpService}) {

  const [formData, setFormData] = useState({
    barcode: "",
    parent_barcode: "",
    position: ""
  });

  let [showModal,setShowModal] = useState(false),
  [dialogInfo,setDialogInfo] = useState({});

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

  function submitLocateVial(event) {
    event.preventDefault();
    console.log(formData);

    let response = httpService.locateVial(formData);
    response.then((result) => {
      console.log(result);
      try {
        let jsonData = JSON.parse(result.text);
        if (jsonData.success) {
          displayAlertDialog("Vial successfully located!!!");
        }
        else {
          displayAlertDialog("Locate vial failed", jsonData.errors); 
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
        <form id="addVialForm" method='POST' onSubmit={(e) => submitLocateVial(e)}>
            <table>
                <tr>
                    <td className="formFieldLabel">
                        <label htmlFor="addvial-barcode">Barcode:</label></td>
                    <td className="formField">
                        <input type="text" name="barcode" 
                          onChange={(e) => setFormData({...formData, barcode: e.target.value})} required />
                    </td>
                </tr>
                <tr>
                    <td className="formFieldLabel">Parent Barcode:</td>
                    <td className="formField">
                        <input type="text" name="parent_barcode" 
                          onChange={(e) => setFormData({...formData, parent_barcode: e.target.value})} required/>
                    </td>
                </tr>
                <tr>
                    <td className="formFieldLabel">Position:</td>
                    <td className="formField">
                        <input type="text" name="position" 
                          onChange={(e) => setFormData({...formData, position: e.target.value})} required/>
                    </td>
                </tr>
            </table>
            <p className="importantMessage">ALL Fields are required</p>
            <button className="normalButton" type="submit">Locate</button>
        </form>
        <Alert dialogInfo={dialogInfo} showModal={showModal} setShowModal={setShowModal}/>
    </div>
  )
}
