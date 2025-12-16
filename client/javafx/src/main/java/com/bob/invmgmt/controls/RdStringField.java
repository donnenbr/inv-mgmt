/*
 * a text field with support for minimum and maximum length for validation.
 */
package com.bob.invmgmt.controls;

public class RdStringField extends RdBaseTextField {
	
	private int minLength = 0;
	private int maxLength = Integer.MAX_VALUE;

	public RdStringField() {
		super();
	}

	public RdStringField(String text) {
		super(text);
	}

	public int getMinLength() {
		return minLength;
	}

	public void setMinLength(int minLength) {
		if (minLength > maxLength) {
			throw new RuntimeException("Minimum length cannot be > maximum length");
		}
		this.minLength = minLength;
	}

	public int getMaxLength() {
		return maxLength;
	}

	public void setMaxLength(int maxLength) {
		if (maxLength < minLength) {
			throw new RuntimeException("Maximum length cannot be < minimum length");
		}
		this.maxLength = maxLength;
	}
	
	public boolean validate() {
		// check basic validation and only continue if it passes
		boolean valid = super.validate();
		if (valid) {
			// now check if the value fits within the min and max length values if they are defined
			String val = getValue();
			if (val != null) {
				if (val.length() < minLength) {
					addError(getName() + " must be at least " + minLength + " characters");
				}
				if (val.length() > maxLength) {
					addError(getName() + " must be at most " + maxLength + " characters");
				}
			}
		}
		return getErrors().size() == 0;
	}
}
