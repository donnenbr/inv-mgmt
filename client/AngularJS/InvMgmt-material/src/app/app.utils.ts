import { HttpErrorResponse } from  '@angular/common/http';
import { FormGroup, AbstractControl } from '@angular/forms';

import { CommonDialog } from '../dialogs/commonDialog';

/*
export function serverError(message:string, errorResponse: HttpErrorResponse) {
    console.log("*** in serverError");

    // effectively copied from the extjs version
    let errors = undefined;
    // response is assumed to be the response from either a model operation (add, update, delete)
    // or ajax call.  because of the different way errors can be returned, we look at responseJson
    // first.  if not, we look at responseText and try to convert THAT to json as that is what
    // is returned by the ajax calls.  if all else fails, we look at the status text.
    if (errorResponse) {
        if (errorResponse.error && errorResponse.error.errors) {
            errors = errorResponse.error.errors;
        }
    }
    if (!errors) {
        errors = [ errorResponse.statusText ];
    }
    let msg;
    if (Array.isArray(errors)) {
        msg = errors.join("\n"); 
    }
    else {
        msg = errors;
    }
    alert(message + ":\n\n" + msg);
}

export function getErrorsForField2(fieldName:string, field: AbstractControl) {
    if (field.errors) {
      if (field.errors['required']) {
        return fieldName + " is ABSOLUTELY required";
      }
      if (field.errors['minlength']) {
        return fieldName + " must be at least " + field.errors['minlength'].requiredLength + " characters";
      }
      if (field.errors['maxlength']) {
        return fieldName + " must be at most " + field.errors['maxlength'].requiredLength + " characters";
      }
      if (field.errors['min']) {
        return fieldName + " must be at least " + field.errors['min'].min;
      }
      if (field.errors['max']) {
        return fieldName + " must be at most " + field.errors['max'].max;
      }
    }
    return null;
  }

  function getErrorsForField(fieldName:string, field: AbstractControl, errorArr: string[]) {
    if (field.errors) {
      if (field.errors['required']) {
        errorArr.push(fieldName + " is required");
      }
      if (field.errors['minlength']) {
        errorArr.push(fieldName + " must be at least " + field.errors['minlength'].requiredLength + " characters");
      }
      if (field.errors['maxlength']) {
        errorArr.push(fieldName + " must be at most " + field.errors['maxlength'].requiredLength + " characters");
      }
      if (field.errors['min']) {
        errorArr.push(fieldName + " must be at least " + field.errors['min'].min);
      }
      if (field.errors['max']) {
        errorArr.push(fieldName + " must be at most " + field.errors['max'].max);
      }
    }
  }

export function getFormErrors(fieldNames: any, formGrp: FormGroup) : string[] {
    let errors : string[] = [];
    if (!formGrp.valid) {
      for (let x in formGrp.controls) {
        let fld = formGrp.get(x);
        if (fld != null && fld.errors) {
          let fldName = fieldNames[x];
          getErrorsForField(fldName, fld, errors);
        }
      }
      // check for form group level validation
      if (formGrp.errors) {
        if (formGrp.errors['incompleteData']) {
          errors.push("Please enter all data fields");
        }
        else {
          console.dir(formGrp.errors);
          errors.push("Unknown form group error");
        }
      }
    }
    return errors;
}
*/

///////////////////////////////////////////////////////////////////////////////////

import { Injectable } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';

@Injectable({
  providedIn: 'root'
})

export class AppUtils {

  constructor(private dialog: MatDialog) {
    console.log("*** AppUtils - dialog " + dialog);
   }

   showDialog(title: string, errors: string[]) {
    this.dialog.open(CommonDialog, {
      width: '450px', data: { title: title, messages: errors } });
  }

  serverError(message:string, errorResponse: HttpErrorResponse) {
    console.log("*** in serverError");

    // effectively copied from the extjs version
    let errors = undefined;
    // response is assumed to be the response from either a model operation (add, update, delete)
    // or ajax call.  because of the different way errors can be returned, we look at responseJson
    // first.  if not, we look at responseText and try to convert THAT to json as that is what
    // is returned by the ajax calls.  if all else fails, we look at the status text.
    if (errorResponse) {
        if (errorResponse.error && errorResponse.error.errors) {
            errors = errorResponse.error.errors;
        }
    }
    if (!errors) {
        errors = [ errorResponse.statusText ];
    }
    this.showDialog(message, errors);
  }

  getFormErrors(fieldNames: any, formGrp: FormGroup) : string[] {
    let errors : string[] = [];
    if (!formGrp.valid) {
      for (let x in formGrp.controls) {
        let fld = formGrp.get(x);
        if (fld != null && fld.errors) {
          let fldName = fieldNames[x];
          this.getErrorsForField(fldName, fld, errors);
        }
      }
      // check for form group level validation
      if (formGrp.errors) {
        if (formGrp.errors['incompleteData']) {
          errors.push("Please enter all data fields");
        }
        else {
          console.dir(formGrp.errors);
          errors.push("Unknown form group error");
        }
      }
    }
    return errors;
  }

  private getErrorsForField(fieldName:string, field: AbstractControl, errorArr: string[]) {
    if (field.errors) {
      if (field.errors['required']) {
        errorArr.push(fieldName + " is required");
      }
      if (field.errors['minlength']) {
        errorArr.push(fieldName + " must be at least " + field.errors['minlength'].requiredLength + " characters");
      }
      if (field.errors['maxlength']) {
        errorArr.push(fieldName + " must be at most " + field.errors['maxlength'].requiredLength + " characters");
      }
      if (field.errors['min']) {
        errorArr.push(fieldName + " must be at least " + field.errors['min'].min);
      }
      if (field.errors['max']) {
        errorArr.push(fieldName + " must be at most " + field.errors['max'].max);
      }
    }
  }

  getErrorsForField2(fieldName:string, field: AbstractControl) {
    if (field.errors) {
      if (field.errors['required']) {
        return fieldName + " is ABSOLUTELY required";
      }
      if (field.errors['minlength']) {
        return fieldName + " must be at least " + field.errors['minlength'].requiredLength + " characters";
      }
      if (field.errors['maxlength']) {
        return fieldName + " must be at most " + field.errors['maxlength'].requiredLength + " characters";
      }
      if (field.errors['min']) {
        return fieldName + " must be at least " + field.errors['min'].min;
      }
      if (field.errors['max']) {
        return fieldName + " must be at most " + field.errors['max'].max;
      }
    }
    return null;
  }

}

