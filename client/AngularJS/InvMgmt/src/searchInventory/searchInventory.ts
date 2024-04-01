import { Component, Input } from '@angular/core';
import { SearchPanel } from './searchPanel';
import { SearchChildContainersPanel } from './childContainersPanel';
import { CommonModule } from '@angular/common';


@Component({
  selector: 'search-inventory',
  standalone: true,
  templateUrl: './searchInventory.html',
  imports: [ SearchPanel, SearchChildContainersPanel, CommonModule ],
  styleUrls: ['../app/app.component.scss']
})
export class SearchInventory {
  selectedBarcode = '';
  displayedContainer: any = null;

  num_rows = 20;

  containerChanged(container:any) {
    console.log("*** search inventory - containerChanged called");
    console.dir(container);
    this.displayedContainer = container;
  }

  containerSelected(barcode:any) {
    console.log("*** search inventory - container selected " + barcode);
    this.selectedBarcode = barcode;
  }

}