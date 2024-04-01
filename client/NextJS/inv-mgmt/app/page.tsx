'use client'

import Script from 'next/script'

import { useState, useEffect, useRef } from 'react';

import AddVial from '@/app/pages/components/AddVial/AddVial';
import LocateVial from '@/app/pages/components/LocateVial/LocateVial';
import SearchInventory from '@/app/pages/components/SearchInventory/SearchInventory';
import PickList from '@/app/pages/components/PickList/PickList';

import HttpService from './httpService';

export default function Home() {
  let currentStatus = useRef("the default status value");
  const [status, setStatus] = useState(currentStatus.current);
  const [selectedPanel, setSelectedPanel] = useState("add vial");

  useEffect( () => {
    console.log("*** useEffect - " + status);
    if (status !== currentStatus.current) {
      console.log("*** status has changed!!!");
      currentStatus.current = status;
    }
 }, [status]);

 function showPanel(panelName:string) {
    setSelectedPanel(panelName);
  }

  const httpService = new HttpService();

  return (
    <main className="main-panel">
      <Script src="./scripts/plain-modal.min.js" 
        strategy="beforeInteractive"
        onLoad={()=>console.log("*** loaded")}
        onError={()=>console.log("*** ERROR")}
        onReady={()=>console.log("*** READY")}
      />
      <div className="content">
        <div id="button-panel">
          <button className="tabPanelButton" onClick={() => showPanel('add vial')}>Add New Vial</button>
          <button className="tabPanelButton" onClick={() => showPanel('search inventory')}>Search Inventory</button>
          <button className="tabPanelButton" onClick={() => showPanel('locate vial')}>Locate Vial</button>
          <button className="tabPanelButton" onClick={() => showPanel('pick list')}>Pick List</button>
        </div>
        <hr className="tabPanelBlank"/>
      </div>
      <div id="main-panel">
        <div hidden={selectedPanel != 'add vial'}>
          <AddVial httpService={httpService}/>
        </div>
        <div hidden={selectedPanel != 'search inventory'}>
          <SearchInventory httpService={httpService}/>
        </div>
        <div hidden={selectedPanel != 'locate vial'}>
          <LocateVial httpService={httpService}/>
        </div>
        <div hidden={selectedPanel != 'pick list'}>
          <PickList httpService={httpService}/>
        </div>
      </div>
    </main>
  );
}
