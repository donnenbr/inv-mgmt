import { Component, Input } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { HttpService } from '../app/http-service.'
import { HttpErrorResponse } from  '@angular/common/http';
import { serverError, getFormErrors, displayAlert } from '../app/app.utils';

@Component({
  selector: 'locate-vial',
  standalone: true,
  templateUrl: './locateVial.html',
  styleUrls: ['../app/app.component.scss'],
  imports: [ ReactiveFormsModule, CommonModule ],
  providers: [
    HttpService
  ]
})
export class LocateVial {
  @Input() MIN_BARCODE_LENGTH = 8;

  dataForm = new FormGroup({
    barcode : new FormControl(null, [Validators.required, Validators.minLength(this.MIN_BARCODE_LENGTH)]),
    parent_barcode : new FormControl(null, [Validators.required, Validators.minLength(this.MIN_BARCODE_LENGTH)]),
    position : new FormControl(null, [Validators.required])
   });
   // only way I know to link a form control "name" to a friendly field name (like a lasbel) for error generation
   fieldNames:any = {
    barcode: 'Vial barcode',
    parent_barcode: 'Rack barcode',
    position: 'Position'
   };

   constructor(private httpService: HttpService) { }

  onSubmit() {
    let errors = getFormErrors(this.fieldNames, this.dataForm);
    if (errors.length) {
        displayAlert("Please fix the following errors", errors);
    }
    else {
      this.httpService.locateVial(this.dataForm.value).subscribe( {
        // like extJS ajax success
        next: (resp: any) => {
          if (resp.success === true) {
            displayAlert("Vial successfully located!", null);
          }
          else {
            alert("Unknown success value returned " + resp.success);
          }
        },
        // like extJS ajax failure
        error: (errorResponse: HttpErrorResponse) => {
          serverError("Locate vial failed", errorResponse);
        }
      });
    }
  }  
}