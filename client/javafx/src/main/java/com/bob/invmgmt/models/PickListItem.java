/*
 * class representing a single item from the pick list search table.  a list of these is sent
 * to the backend to perform the request.
 */
package com.bob.invmgmt.models;

import java.util.Objects;

public class PickListItem {
	
	// the line number displayed on the screen.  used by the backend when communicating errors so you
	// can fix them!
	private Integer lineNum;
	// the reagent requested.  we don't support specific lots because (like aspirin), it is assumed all
	// lots of a reagent are the same thing.
	private String reagent;
	// the amount and concentration requested, with assumed units of measure.
	private Integer amount;
	private Double concentration;
	
	public PickListItem(Integer lineNum, String reagent, Integer amount, Double concentration) {
		super();
		this.lineNum = lineNum;
		this.reagent = reagent;
		this.amount = amount;
		this.concentration = concentration;
	}
	
	public PickListItem() {
		this(null, null, null, null);
	}

	public Integer getLineNum() {
		return lineNum;
	}

	public void setLineNum(Integer lineNum) {
		this.lineNum = lineNum;
	}

	public String getReagent() {
		return reagent;
	}

	public void setReagent(String reagent) {
		this.reagent = reagent;
	}

	public Integer getAmount() {
		return amount;
	}
	
	public void setAmount(Integer amount) {
		this.amount = amount;
	}

	public Double getConcentration() {
		return concentration;
	}
	
	public void setConcentration(Double concentration) {
		this.concentration = concentration;
	}
	
	public String toString() {
		return String.format("PickListItem [lineNum=%d, reagent=%s, amount=%d, concentration=%f]",
				lineNum, reagent, amount, concentration);
	}

	@Override
	public int hashCode() {
		return Objects.hash(amount, concentration, lineNum, reagent);
	}

	@Override
	public boolean equals(Object obj) {
		if (this == obj)
			return true;
		if (obj == null)
			return false;
		if (getClass() != obj.getClass())
			return false;
		PickListItem other = (PickListItem) obj;
		return Objects.equals(amount, other.amount) && Objects.equals(concentration, other.concentration)
				&& Objects.equals(lineNum, other.lineNum) && Objects.equals(reagent, other.reagent);
	}
}
