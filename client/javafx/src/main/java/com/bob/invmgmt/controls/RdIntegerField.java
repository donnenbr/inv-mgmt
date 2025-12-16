/*
 * a text field which supports integer values.  it adds support for minimum and maximum value
 * for validation.
 */
package com.bob.invmgmt.controls;

public class RdIntegerField extends RdBaseTextField {
	
	private int minValue = Integer.MIN_VALUE;
	private int maxValue = Integer.MAX_VALUE;

	public RdIntegerField() {
		super();
	}

	public RdIntegerField(String text) {
		super(text);
	}

	public int getMinValue() {
		return minValue;
	}

	public void setMinValue(int minValue) {
		if (minValue > maxValue) {
			throw new RuntimeException("Minimum value cannot be > maximum value");
		}
		this.minValue = minValue;
	}

	public int getMaxValue() {
		return maxValue;
	}

	public void setMaxValue(int maxValue) {
		if (maxValue < minValue) {
			throw new RuntimeException("Maximum value cannot be < minimum value");
		}
		this.maxValue = maxValue;
	}
	
	public boolean validate() {
		// check basic validation and only continue if it passes
		boolean valid = super.validate();
		if (valid) {
			// now check if the value is a legit integer and fits within the min and max values if they
			// are defined
			String val = getValue();
			if (val != null && val.length() > 0) {
				try {
					int ival = Integer.valueOf(val);
					if (ival < minValue) {
						StringBuilder errMsg = new StringBuilder(getName() + " must be >= " + minValue);
						if (maxValue < Integer.MAX_VALUE) {
							errMsg.append(" and <= " + maxValue);
						}
						addError(errMsg.toString());
					}
					if (ival > maxValue) {
						StringBuilder errMsg = new StringBuilder(getName() + " must be ");
						if (minValue > Integer.MIN_VALUE) {
							errMsg.append(">= " + minValue + " and ");
						}
						errMsg.append("<= " + maxValue);
						addError(errMsg.toString());
					}
				}
				catch (Exception ex) {
					// assume bad int
					StringBuilder errMsg = new StringBuilder(getName() + " must be an integer value");
					if (minValue> Integer.MIN_VALUE) {
						errMsg.append(" >= " + minValue);
					} 
					if (maxValue < Integer.MAX_VALUE) {
						if (minValue > Integer.MIN_VALUE) {
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
