'use client'

import {useState}  from 'react';

export interface PickListResultProps {
    pickData?: any;
    setShowMode?: Function;
  }
  
  export default function PickListResult({pickData, setShowMode}) {
    let [showAvailable,setShowAvailable] = useState(true),
        [showUnavailable,setShowUnavailable] = useState(true);
    let availableSamplesExist = pickData.available != null && pickData.available.length > 0,
        unavailableSamplesExist = pickData.unavailable != null && pickData.unavailable.length > 0
  
      return (
        <div className="main-panel">
            {/* we never get here if there are no available samples.  an alert is given in that case. */}
            <div hidden={!(showAvailable && availableSamplesExist)}>
                <table className="pickListTable">
                    <caption>Available Samples</caption>
                    <thead>
                        <tr>
                            <th>Reagent</th>
                            <th>Requested<br/>Amount (uL)</th>
                            <th>Barcode</th>
                            <th>Location</th>
                            <th>Container<br/>Amount(uL)</th>
                            <th>Conc. (uM)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {pickData.available?.map((row) => (
                            <tr key={row.id} className="pickListTableRow">
                                <td>{row.reagent}</td>
                                <td>{row.requested_amount}</td>
                                <td>{row.barcode}</td>
                                <td>{row.position}</td>
                                <td>{row.amount}</td>
                                <td>{row.concentration}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
            <br/>
            <div hidden={!(showUnavailable && unavailableSamplesExist)}>
                <table className="pickListTable">
                    <caption>Unavailable Samples</caption>
                    <thead>
                        <tr>
                        <th>Reagent</th>
                        <th>Requested<br/>Amount (uL)</th>
                        <th>Requested<br/>Conc. (uM)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {pickData.unavailable?.map((row) => (
                            <tr key={row.id} className="pickListTableRow">
                                <td>{row.reagent}</td>
                                <td>{row.amount}</td>
                                <td>{row.concentration}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
            <p className="buttonRow">
                <button className="normalButton" onClick={() => setShowMode('request')}>Back to Request</button>
                <span hidden={!(availableSamplesExist && unavailableSamplesExist)}>
                    <button className="normalButton" onClick={() => setShowAvailable(!showAvailable)}>Toggle Available</button>
                    <button className="normalButton" onClick={() => setShowUnavailable(!showUnavailable)}>Toggle Unavailable</button>
                </span>
            </p>
          </div>
      );
  }