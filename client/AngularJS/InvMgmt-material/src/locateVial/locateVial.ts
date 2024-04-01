import { Component, Input } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators, AbstractControl } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { HttpService } from '../app/http-service.'
import { HttpErrorResponse } from  '@angular/common/http';
import { AppUtils} from '../app/app.utils';

import {MatInputModule} from '@angular/material/input';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatButtonModule} from '@angular/material/button';

@Component({
  selector: 'locate-vial',
  standalone: true,
  templateUrl: './locateVial.html',
  styleUrls: ['../app/app.component.scss'],
  imports: [ ReactiveFormsModule, CommonModule, MatButtonModule, MatFormFieldModule, MatInputModule ]
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

  constructor(private httpService: HttpService, private appUtils: AppUtils) { }

  getFieldErrors(fieldName:string, field: AbstractControl) {
    return this.appUtils.getErrorsForField2(fieldName, field);
   }

  onSubmit() {
    if (! this.dataForm.invalid) {
      this.httpService.locateVial(this.dataForm.value).subscribe( {
        // like extJS ajax success
        next: (resp: any) => {
          if (resp.success === true) {
            this.appUtils.showDialog("Success!",["Vial successfully located!"]);
          }
          else {
            alert("Unknown success value returned " + resp.success);
          }
        },
        // like extJS ajax failure
        error: (errorResponse: HttpErrorResponse) => {
          this.appUtils.serverError("Locate vial failed", errorResponse);
        }
      });
    }
  }  
}