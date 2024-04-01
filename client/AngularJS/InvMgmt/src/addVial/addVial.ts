import { Component } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators, AbstractControl } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { HttpService } from '../app/http-service.'
import { HttpErrorResponse } from  '@angular/common/http';
import { serverError, getFormErrors, displayAlert, displayConfirmation } from '../app/app.utils';


@Component({
  selector: 'add-vial',
  standalone: true,
  templateUrl: './addVial.html',
  styleUrls: ['../app/app.component.scss'],
  imports: [ ReactiveFormsModule, CommonModule ],
  providers: [
    HttpService
  ]
})


export class AddVial {

  constructor(private httpService: HttpService) { }

  // these things could be configurable.  must5 be Input to pass to html template
  MIN_BARCODE_LENGTH = 8;
  MIN_AMOUNT = 1
  MAX_AMOUNT = 750
  MIN_CONCENTRATION = 1
  MAX_CONCENTRATION = 100
  AMOUNT_UNIT = 'uL'
  CONCENTRATION_UNIT = 'uM'

    // using a form group instead of individual formcontrols lets us handle the entire form as an object, especially to
    // see if it is valid (as opposed to checking each form control)
   dataForm = new FormGroup({
    barcode : new FormControl(null, [Validators.required, Validators.minLength(this.MIN_BARCODE_LENGTH)]),
    lot : new FormControl(null, [Validators.required]),
    // null will allow the value to come back as a NUMBER!!!  any int initial value will do.  if you supply a string
    // and don't change the value, a string is what will be returned.  change it and you get an int.
    amount : new FormControl(null, [Validators.required, Validators.min(this.MIN_AMOUNT), Validators.max(this.MAX_AMOUNT)]),
    amount_unit : new FormControl(this.AMOUNT_UNIT),
    concentration : new FormControl(null, [Validators.required, Validators.min(this.MIN_CONCENTRATION), Validators.max(this.MAX_CONCENTRATION)]),
    concentration_unit : new FormControl(this.CONCENTRATION_UNIT),
  });
  
   // only way I know to link a form control "name" to a friendly field name (like a lasbel) for error generation
   fieldNames:any = {
    barcode: 'Barcode',
    lot: 'Lot Name',
    amount: 'Amount',
    concentration: 'Concentration'
   };

  onSubmit() {
    let errors = getFormErrors(this.fieldNames, this.dataForm);
    if (errors.length) {
        // let s = "Please fix the following errors:\n\n" + errors.join("\n");
        // alert(s);
        displayAlert("Please fix the following errors:", errors);
    }
    else {
      // save the data.  the request returns an observable which we have to subscribe to to get the result
      this.httpService.addVial(this.dataForm.value).subscribe( {
        // like extJS ajax success
        next: (resp: any) => {
          if (resp.success === true) {
            displayAlert("Vial successfully added!", null);
          }
          else {
            alert("Unknown success value returned " + resp.success);
          }
        },
        // like extJS ajax failure
        error: (errorResponse: HttpErrorResponse) => {
          console.log("** error occurred");
          console.dir(errorResponse);
          // for a {success, data} return, this will be in error
          // for anything else, we'll get status and statusText
          serverError("Add vial failed", errorResponse);
        }
      });
    }
  }
}