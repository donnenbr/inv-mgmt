import { Component, Output,  EventEmitter } from '@angular/core';
import { FormControl, FormGroup, FormArray, ReactiveFormsModule, ValidatorFn, 
          AbstractControl, ValidationErrors } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { HttpService } from '../app/http-service.'
import { HttpErrorResponse } from  '@angular/common/http';

import { AppUtils } from '../app/app.utils';

// sample reagents:
    /*
    Child_X10000015-8
    Child_X10000017-8
    Child_X10000051-6
    Child_X10000101-7
    Child_X10000104-7
    Child_X10000164-9
    Child_X10000181-3
    Child_X10000254-8
    Child_X10000262-5
    Child_X10000304-9
    Child_X10000386-5
    Child_X10000535-2
    Child_X10000543-9
    Child_X10000649-5
    Child_X10000762-5
    Child_X10000892-2
    Child_X10000900-5
    Child_X10000914-2
    Child_X10001118-9
    Child_X10001221-2
    Child_X10001224-2
    Child_X10001393-7
    Child_X10001493-3
    Child_X10001541-4
    Child_X10001694-5
    Child_X10001704-8
    Child_X10001721-2
    Child_X10001741-6
    Child_X10001776-7
    Child_X10001806-4
*/

@Component({
  selector: 'pick-list-request',
  standalone: true,
  templateUrl: './request.html',
  styleUrls: ['../app/app.component.scss'],
  imports: [CommonModule, ReactiveFormsModule]
})
export class PickListRequest {

  constructor(private httpService: HttpService, private appUtils: AppUtils) {
  
   }

  @Output() resultChange = new EventEmitter<any>();
   resultChanged(data: any) {
      console.log("*** emitting " + data);
    	this.resultChange.emit(data);
    }

  MIN_AMOUNT = 1
  MAX_AMOUNT = 750
  MIN_CONCENTRATION = 1
  MAX_CONCENTRATION = 100
  AMOUNT_UNIT = 'uL'
  CONCENTRATION_UNIT = 'uM'

  // NOTE - this baby fires EVERY TIME you type into the fields!!  dataForm.valid is just a status and does not call
  // a function to get it.
  dataRowValidator: ValidatorFn = ( ctrl: AbstractControl): ValidationErrors | null => {
    let reagent = ctrl.get("reagent")?.value,
        amount = ctrl.get("amount")?.value,
        concentration = ctrl.get("concentration")?.value;
    if (reagent) {
      reagent = reagent.trim();
    }
    if (reagent || amount != null || concentration != null) {
      if (!(reagent && amount && concentration)) {
        return {incompleteData: true, reagent: reagent, amount: amount, concentration: concentration};
      }
    }
    return null;
  }

  // the dataArray must be defined a a property accessible to the html file for the ngFor loop.  ie, in its own variable.
  dataArray = new FormArray(this.makeInputControls(), null, null);
  /* can also be done with an empty array which is populated in ngOnInit() like this
      dataArray = new FormArray(<any>[], null, null);
  */
  // there MUST be a form group at the top!!!
  dataForm = new FormGroup({
    rows: this.dataArray
  });

  fieldNames:any = {
    reagent: 'Reagent',
    amount: 'Amount',
    concentration: 'Concentration'
   };

  makeInputControls() {
    let arr = [];
    for (let i = 1; i <= 10; ++i) {
      let fg = new FormGroup({
        reagent: new FormControl(null),
        amount: new FormControl(null),
        unit: new FormControl(this.AMOUNT_UNIT),
        concentration: new FormControl(null),
        concentration_unit: new FormControl(this.CONCENTRATION_UNIT)
      }, {validators: this.dataRowValidator});
      // must also add form group level validator since reagent, amount,concentration may all be null for
      // empty lines.  if any one is set, they ALL must be set
      arr.push(fg);
    }
    return arr;
  }

  unloadValues() {
    let valueArray = <any>[];
    this.dataArray.controls.forEach((fg:FormGroup,idx,arr) => {
      let reagent = fg.get("reagent")?.value,
          amount = fg.get("amount")?.value,
          concentration = fg.get("concentration")?.value;
      console.log("*** reagent " + reagent + ", " + amount + ", " + concentration);
      if (reagent != null) {
        reagent = reagent.trim();
        if (reagent.length) {
          let record = { reagent: reagent, amount: amount, concentration: concentration, lineNum: idx+1 };
				  valueArray.push(record);
        }
      }
    });
    return valueArray;
  }

  doRequest() {
    if (!this.dataForm.valid) {
      let errors: string[] = [];
      this.dataArray.controls.forEach((fg:FormGroup,idx,arr) => {
        // console.log("*** form grp " + fg + ", line " + fg.get("lineNumber")?.value + ", errors " + fg.errors);
        let errs = this.appUtils.getFormErrors(this.fieldNames, fg);
        if (errs.length > 0) {
            errors.push("Line " + (idx+1) + " : ");
            errs.forEach((msg) => { errors.push("   " + msg)});
        }
      });
      if (errors) {
        this.appUtils.showDialog("Please fix the following errors", errors);
      }
    }
    else {
      // this.dataArray.controls.forEach((fg:FormGroup) => { console.dir(fg.value) });
      let values = this.unloadValues();
      if (values.length) {
        this.httpService.pickList(values).subscribe( {
          // like extJS ajax success
          next: (resp: any) => {
            if (resp.success === true) {
              let available_samples = resp.data?.available,
                  unavailable_samples = resp.data?.unavailable;
              if (available_samples == null || unavailable_samples == null) {
                console.dir(resp);
                alert("Did not get back lists of available and unavailable samples");
              }
              else {
                if (available_samples.length < 1) {
                  alert("No samples were available");
                }
                else {
                  this.resultChanged(resp.data);
                }
              }
            }
            else {
              alert("Unknown success value returned " + resp.success);
            }
          },
          // like extJS ajax failure
          error: (errorResponse: HttpErrorResponse) => {
            this.appUtils.serverError("Pick list failed", errorResponse);
          }
        });
      }
      else {
        this.appUtils.showDialog("No values were entered !!!", []);
      }
    }
  }
}
