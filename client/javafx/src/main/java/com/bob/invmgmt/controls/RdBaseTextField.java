/*
 * base class for an extended text field giving properties for required and validation
 * the name is used simply to format the error messages since there is no link to an 
 * associated label, which would not look right anyway. 
 * 
 */
package com.bob.invmgmt.controls;

import javafx.scene.control.TextField;

import java.util.List;
import java.util.ArrayList;

public class RdBaseTextField extends TextField {
	
	private boolean required = false;
	// to give the field a human readable name in the error messages.  to allow different fields on 
	// different screens to have the same name even tho the ids must be unique.
	private String name = null;
	private String value = null;
	private List<String> errors = new ArrayList<>();

	public RdBaseTextField() {
		super();
	}

	// like the javafx text field, with a default value
	public RdBaseTextField(String text) {
		super(text);
	}

	public boolean isRequired() {
		return required;
	}

	public void setRequired(boolean required) {
		this.required = required;
	}
	
	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

	// get a list of errors post validation
	public List<String> getErrors() {
		return this.errors;
	}
	
	// get the string value, pre-trimmed to remove white space.
	public String getValue() {
		String txt = this.getText();
		if (txt != null) {
			value = txt.trim();
		}
		return value;
	}

	// add an error message to the error list (duh!!!)
	protected void addError(String errorMessage) {
		if (errorMessage != null) {
			errors.add(errorMessage);
		}
	}

	// validate the field, only testing for required by default.
	public boolean validate() {
		errors.clear();
		if (this.required) {
			String val = this.getText();
			if (val != null) {
				val = val.trim();
			}
			if (val == null || val.length() < 1) {
				errors.add(this.getName() + " is requred");
			}
		}
		return this.errors.size() == 0;
	}

}
