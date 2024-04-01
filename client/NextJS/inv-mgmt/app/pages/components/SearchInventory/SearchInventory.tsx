'use client'

import {useState}  from 'react';

import HttpService from '@/app/httpService';
import SearchPanel from "./SearchPanel";
import SearchChildContainers from './SearchChildContainers';

export interface SearchInventoryProps {
  httpService?: HttpService;
}

export default function SearchInventory({httpService}) {
  
  const [selectedContainer, setSelectedContainer] = useState(null);
  const [selectedBarcode, setSelectedBarcode] = useState(null);

  return (
    <div className="main-panel">
      <SearchPanel httpService={httpService} selectedBarcode={selectedBarcode} setSelectedContainer={setSelectedContainer}/>
      <SearchChildContainers selectedContainer={selectedContainer} setSelectedBarcode={setSelectedBarcode}/>
    </div>
  )
}
