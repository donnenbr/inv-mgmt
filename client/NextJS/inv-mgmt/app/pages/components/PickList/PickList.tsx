'use_client'

import {useState, useEffect} from 'react';

import HttpService from '@/app/httpService';

import PickListRequest from "./PickListRequest";
import PickListResult from "./PickListResult";

export interface PickListProps {
  httpService?: HttpService;
}

export default function PickList({httpService}) {

  const [pickData,setPickData] = useState({
      available: null,
      unavailable: null
  });
  const [showMode,setShowMode] = useState('request');

  useEffect( () => {
    console.log("*** pick data useeffect " + pickData);
    if (pickData != null && pickData.available != null && pickData.unavailable != null) {
        console.log(pickData);
        // console.log("*** data has changed - avail " + pickData.available + "unavail " + pickData.unavailable);
        // setPickData({...pickData, available: pickData.available, unavailable:pickData.unavailable});
        setShowMode('result');
    }
 }, [pickData]);

  return (
    <div className="main-panel">
      <div hidden={showMode=='result'} >
        <PickListRequest httpService={httpService} setPickData={setPickData}/>
      </div>
      <div hidden={showMode=='request'} >
        <PickListResult pickData={pickData} setShowMode={setShowMode}/>
      </div>
    </div>
  )
}
