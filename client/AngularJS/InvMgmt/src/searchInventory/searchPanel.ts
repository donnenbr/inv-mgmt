import { Component, Input, Output,  EventEmitter } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { HttpService } from '../app/http-service.'
import { HttpErrorResponse } from  '@angular/common/http';
import { serverError, getFormErrors, displayAlert, displayConfirmation } from '../app/app.utils';

@Component({
  selector: 'search-panel',
  standalone: true,
  templateUrl: './searchPanel.html',
  styleUrls: ['../app/app.component.scss'],
  imports: [ ReactiveFormsModule, CommonModule ],
  providers: [
    HttpService
  ]
})
export class SearchPanel {
  MIN_AMOUNT = 1
  MAX_AMOUNT = 750
  MIN_CONCENTRATION = 1
  MAX_CONCENTRATION = 100
  AMOUNT_UNIT = 'uL'
  CONCENTRATION_UNIT = 'uM'

  dataForm = new FormGroup({
    id: new FormControl(null),
    barcode: new FormControl(null, [Validators.required]),
    container_type: new FormControl(null),
    position: new FormControl(null),
    // in a perfect world, the sample info would be in a separate component.  it's really just some hidden fields and buttons.
    // if they are in a separtate compoent, the labels and fields will not line up with those for the barcode, container
    // type and position, which looks shitty.
    lot: new FormControl(null),
    amount : new FormControl(null, [Validators.required, Validators.min(this.MIN_AMOUNT), Validators.max(this.MAX_AMOUNT)]),
    unit: new FormControl(null),
    concentration : new FormControl(null, [Validators.required, Validators.min(this.MIN_CONCENTRATION), Validators.max(this.MAX_CONCENTRATION)]),
    concentration_unit: new FormControl(null),
    reagent: new FormControl(null)
  });
  fieldNames:any = {
    barcode: 'Barcode',
    amount: 'Amount',
    concentration: 'Concentration'
   };

   @Input() selectedBarcode = '';
   @Output() containerChange = new EventEmitter<string>();
   containerChanged(container: any) {
      console.log("*** emitting " + container.barcode);
    	this.containerChange.emit(container);
    }

  constructor(private httpService: HttpService) { }

  ngOnChanges(changes: any) {
    if (changes.selectedBarcode && changes.selectedBarcode.currentValue) {
      this.dataForm.reset();
      this.dataForm.patchValue({barcode:changes.selectedBarcode.currentValue});
      this.searchByBarcode();
    }
  }

  searchByBarcode() {
    // we only want to check the barcode
    if (this.dataForm.controls.barcode?.invalid) {
      displayAlert("Barcode must be entered", null);
    }
    else {
      let barcode = this.dataForm.value.barcode;
      // to shut TypeScript up
      if (!barcode)  return;
      this.httpService.searchContainer(barcode).subscribe( {
        // like extJS ajax success
        next: (resp: any) => {
          if (resp.success === true) {
            this.dataForm.reset();
            this.dataForm.patchValue(resp.data);
            this.containerChanged(resp.data);
          }
          else {
            alert("Unknown success value returned " + resp.success);
          }
        },
        // like extJS ajax failure
        error: (errorResponse: HttpErrorResponse) => {
          if (errorResponse.status == 404) {
            displayAlert("Barcode is invalid", null);
          }
          else {
            serverError("Search container failed", errorResponse);
          }
        }
      });
    }
  }

  updateContainer() {
    let errors = getFormErrors(this.fieldNames, this.dataForm);
    if (errors.length) {
        let s = "Please fix the following errors:\n\n" + errors.join("\n");
        alert(s);
    }
    else {
      this.httpService.updateVial(this.dataForm.value).subscribe( {
        // like extJS ajax success
        next: (resp: any) => {
          if (resp.success === true) {
            this.dataForm.reset();
            this.dataForm.patchValue(resp.data);
            displayAlert("Update successful!!", null);
          }
          else {
            alert("Unknown success value returned " + resp.success);
          }
        },
        // like extJS ajax failure
        error: (errorResponse: HttpErrorResponse) => {
          serverError("Update vial failed", errorResponse);
        }
      });
    }
  }

  deleteContainer() {
    displayConfirmation("Are you sure you want to delete the vial??", null, this, this._doDelete);
  }

  _doDelete() {
    this.httpService.deleteVial(this.dataForm.value).subscribe( {
      // like extJS ajax success
      next: (resp: any) => {
        if (resp.success === true) {
          this.dataForm.reset();
          // this.dataForm.patchValue(resp.data);
          displayAlert("Vial successfully deleted!!", null);
        }
        else {
          alert("Unknown success value returned " + resp.success);
        }
      },
      // like extJS ajax failure
      error: (errorResponse: HttpErrorResponse) => {
        serverError("Delete vial failed", errorResponse);
      }
    });
  }
    
}