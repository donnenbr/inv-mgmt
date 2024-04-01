import { HttpErrorResponse } from  '@angular/common/http';
import { FormControl, FormGroup, ReactiveFormsModule, Validators, AbstractControl } from '@angular/forms';

// the special angular attribute automatically applied to the app's elements.  we need this for the alert dialog.
// we'll define it here so we only have to get it once.
let _anguralAttribute: string;

export function serverError(message:string, errorResponse: HttpErrorResponse) {

    console.log("*** serverError resp " + errorResponse);
    console.log("*** serverError resp.error " + errorResponse.error);
    console.log("*** serverError resp.error.errors" + errorResponse.error.errors);
   
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
    if (!Array.isArray(errors)) {
        errors = [errors];
    }
    displayAlert(message, errors);
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

// plow thru the divs looking for the special angular attribute.  we only look for it once.
function getAngularAttribute() : string {
  if (!_anguralAttribute) {
    console.log("*** getting AngularAttribute");
    let divs = document.getElementsByTagName("div");
    for (let i = 0; i < divs.length; ++i) {
      let elem = divs[i];
      elem.getAttributeNames().forEach((attr:string) => {
        if (attr.startsWith("_ngcontent")) {
          _anguralAttribute = attr;
        }
      });
      if (_anguralAttribute) {
        break;
      }
    }
  }

  return _anguralAttribute;
}

export function displayAlert(title: string, messages: string[]|null|string) {
  let attr:string = getAngularAttribute();

  // what is going on here.
  // when everything gets built by angular, each element (<div>, <button>, etc.) is automatically assigned
  // a special attribute in the format _ngcontent-c<SOMETHING>.  this attribute is also applied to the 
  // classes defined in the css so only those elements with that attribute get the class applied.  if we just
  // create elements for our dislog and apply our css classes to them, the classes will NOT take effect!!!
  // we have 2 options:
  //    1 - use styles, but that means copying values from our nice css classes
  //    2 - find the special angular attribute and apply it to those elements we create here for which we want
  //        to apply css classes.  we chose that to avoid duplication.

  // the main dialog element.  give it a nice border, etc.
  let wrapper= document.createElement('div');
  wrapper.setAttribute(attr, "");
  wrapper.setAttribute("class", "dialog");
  // the contents of the dialog (text, controls, etc)
  let content = '<div style="margin:20px;">' +
      // the title
      "<span class='dialogTitle' " + attr + ">" + title + "</span>";
  // add any messages (text content) if supplied.  no styling.
  if (messages) {
    if (!Array.isArray(messages)) {
      messages = [ messages ];
    }
    messages.forEach((msg,arr,idx) => {
      content += msg + "<br/>";
    });
  }
  content += "</div>";
  wrapper.innerHTML = content;
  // button area.  we need to access the button so it will close the dialog.
  var btnArea = document.createElement("p");
  btnArea.setAttribute("style", "text-align:center");
  // the button
  var btn = document.createElement('button');
  btn.setAttribute("class", "normalButton");
  btn.setAttribute(attr, "");
  btn.innerHTML="Continue";
  btnArea.appendChild(btn);
  // another button with our custom handler
  /*
  var btn2 = document.createElement('button');
  btn2.setAttribute("style", "background-color: lightblue; color:white; font-size:12pt; padding:10px; margin-left:50px;")
  btn2.addEventListener("click", this.clicktest);
  btn2.innerHTML="Click my ass!!!";
  btnArea.appendChild(btn2);
  */
  // add button area to dialog
  wrapper.appendChild(btnArea);
  // create the modal dialog and rock & roll.
  let modal = new PlainModal(wrapper, {
    closeButton: btn,
    overlayBlur: 5
  });
  // another way to set the options
  /*
  modal.closeButton = btn;
  modal.dragHandle = wrapper.firstChild;
  modal.overlayBlur = 3;
  */
  modal.open();
}

export function displayConfirmation(title: string, messages: string[]|null|string, caller: any, yesHandler: any) {
  let attr:string = getAngularAttribute();

  let wrapper= document.createElement('div');
  wrapper.setAttribute(attr, "");
  wrapper.setAttribute("class", "dialog");
  let content = '<div style="margin:20px;">' +
      "<span class='dialogTitle' " + attr + ">" + title + "</span><br/><br/>";
  if (messages) {
    if (!Array.isArray(messages)) {
      messages = [ messages ];
    }
    messages.forEach((msg,arr,idx) => {
      content += msg + "<br/>";
    });
  }
  content += "</div>";
  wrapper.innerHTML = content;
  var btnArea = document.createElement("p");
  btnArea.setAttribute("style", "text-align:center");
  var noBtn = document.createElement('button');
  noBtn.setAttribute("class", "normalButton");
  noBtn.setAttribute("style", "margin-right:20px");
  noBtn.setAttribute(attr, "");
  noBtn.innerHTML="No";
  btnArea.appendChild(noBtn);
  //
  var yesBtn = document.createElement('button');
  // we'll add the listener later becase we want to close the modal when the button is clicked.
  yesBtn.setAttribute("class", "normalButton");
  yesBtn.setAttribute("style", "margin-left:20px");
  yesBtn.setAttribute(attr, "");
  yesBtn.innerHTML="Yes";
  btnArea.appendChild(yesBtn);
  //
  wrapper.appendChild(btnArea);
  // create the modal dialog and rock & roll.
  let modal = new PlainModal(wrapper, {
    closeButton: noBtn,
    overlayBlur: 5
  });
  // now that we have the modal, add the event listener to the Yes button
  // SUPER IMPORTANT NOTE - if we just called yesHandler, it would execute in this environment, not that
  // of the caller and would not have access to things like the httpService.  the following executes
  // the yesHandler in the caller's environment.
  yesBtn.addEventListener("click", function() { modal.close(); yesHandler.call(caller);}); 
  
  modal.open();
}


