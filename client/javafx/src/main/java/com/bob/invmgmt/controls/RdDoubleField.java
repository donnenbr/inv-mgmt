/*
 * a text field which supports floating point values.  it adds support for minimum and maximum value
 * for validation.
 */
package com.bob.invmgmt.controls;

public class RdDoubleField extends RdBaseTextField {
	
	private double minValue = Double.MIN_VALUE;
	private double maxValue = Double.MAX_VALUE;

	public RdDoubleField() {
		super();
	}

	public RdDoubleField(String text) {
		super(text);
	}

	public double getMinValue() {
		return minValue;
	}

	public void setMinValue(double minValue) {
		if (minValue > maxValue) {
			throw new RuntimeException("Minimum value cannot be > maximum value");
		}
		this.minValue = minValue;
	}

	public double getMaxValue() {
		return maxValue;
	}

	public void setMaxValue(double maxValue) {
		if (maxValue < minValue) {
			throw new RuntimeException("Maximum value cannot be < minimum value");
		}
		this.maxValue = maxValue;
	}
	
	public boolean validate() {
		// check basic validation and only continue if it passes
		boolean valid = super.validate();
		if (valid) {
			// now check if the value is a legit double and fits within the min and max values if they
			// are defined
			String val = getValue();
			if (val != null && val.length() > 0) {
				try {
					double dval = Double.valueOf(val);
					if (dval < minValue) {
						StringBuilder errMsg = new StringBuilder(getName() + " must be >= " + minValue);
						if (maxValue < Double.MAX_VALUE) {
							errMsg.append(" and <= " + maxValue);
						}
						addError(errMsg.toString());
					}
					if (dval > maxValue) {
						StringBuilder errMsg = new StringBuilder(getName() + " must be ");
						if (minValue > Double.MIN_VALUE) {
							errMsg.append(">= " + minValue + " and ");
						}
						errMsg.append("<= " + maxValue);
						addError(errMsg.toString());
					}
				}
				catch (Exception ex) {
					// assume bad double
					StringBuilder errMsg = new StringBuilder(getName() + " must be an integer value");
					if (minValue> Double.MIN_VALUE) {
						errMsg.append(" >= " + minValue);
					} 
					if (maxValue < Double.MAX_VALUE) {
						if (minValue > Double.MIN_VALUE) {
							errMsg.append(" and ");
						}
						errMsg.append("<= " + maxValue);
					}
					addError(errMsg.toString());
				}
			}
		}
		return getErrors().size() == 0;
	}
}
