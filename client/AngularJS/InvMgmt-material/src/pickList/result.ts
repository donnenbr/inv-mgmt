import { Component, Input, Output,  EventEmitter} from '@angular/core';
import { CommonModule } from '@angular/common';


@Component({
    selector: 'pick-list-result',
    standalone: true,
    templateUrl: './result.html',
    styleUrls: ['../app/app.component.scss'],
    imports: [CommonModule]
  })

  export class PickListResult {
    @Input() resultData: any = null;

    @Output() returnToRequest = new EventEmitter<any>();
    displayRequest() {
    	this.returnToRequest.emit(true);
    }

    constructor() { }

    availableSamples: any = null;
    unavailableSamples:any = null;

    showAvailable = true;
    showUnavailable = true;

    ngOnChanges(changes: any) {
        if (changes && changes.resultData && changes.resultData.currentValue) {
            this.availableSamples = changes.resultData.currentValue.available;
            this.unavailableSamples = changes.resultData.currentValue.unavailable;
            console.log(this.availableSamples)
            // reset these 
            this.showAvailable = true;
            this.showUnavailable = true;
        }
    }  
    
    returnToRequestClicked() {
        this.displayRequest();
    }

    toggleAvailableClicked() {
        this.showAvailable = !this.showAvailable;
    }

    toggleUnavailableClicked() {
        this.showUnavailable = !this.showUnavailable;
    }
  }