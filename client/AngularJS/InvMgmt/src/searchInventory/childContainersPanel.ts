import { Component, Input, Output,  EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'search-child-containers',
  standalone: true,
  templateUrl: './childContainersPanel.html',
  styleUrls: ['../app/app.component.scss'],
  imports: [ CommonModule ],
})
export class SearchChildContainersPanel {

   @Input() displayedContainer: any = null;
   // the current container
   _childContainers: any = null;

   @Output() containerSelected = new EventEmitter<string>();
    tableRowClicked(barcode: string) {
      if (barcode) {
    	  this.containerSelected.emit(barcode);
      }
    }

  constructor() { }

  ngOnChanges(changes: any) {
    // currentValue can be null the first time thru
    if (changes.displayedContainer && changes.displayedContainer.currentValue &&
      changes.displayedContainer.currentValue.containers) {
      this._childContainers = changes.displayedContainer.currentValue.containers;
    }
    else {
      this._childContainers = null;
    }
  }    
}