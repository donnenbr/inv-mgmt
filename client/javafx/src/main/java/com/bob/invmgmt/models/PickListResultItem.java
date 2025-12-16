/* 
 * class representing a single result returned by the backend for a single pick list item.
 * all info is in the container class (as you would pick a container to fulfill the request),
 * plus the requested amount. 
 */
package com.bob.invmgmt.models;

import java.util.Objects;

public class PickListResultItem extends Container {
	
	private Double requested_amount;

	public PickListResultItem() {
		super();
	}

	public Double getRequested_amount() {
		return requested_amount;
	}

	public void setRequested_amount(Double requested_amount) {
		this.requested_amount = requested_amount;
	}

	@Override
	public int hashCode() {
		final int prime = 31;
		int result = super.hashCode();
		result = prime * result + Objects.hash(requested_amount);
		return result;
	}

	@Override
	public boolean equals(Object obj) {
		if (this == obj)
			return true;
		if (!super.equals(obj))
			return false;
		if (getClass() != obj.getClass())
			return false;
		PickListResultItem other = (PickListResultItem) obj;
		return Objects.equals(requested_amount, other.requested_amount);
	}

	@Override
	public String toString() {
		return "Container [id=" + id + ", barcode=" + barcode + ", container_type=" + container_type + ", position="
				+ position + ", lot_id=" + lot_id + ", lot=" + lot + ", reagent=" + reagent + ", amount=" + amount
				+ ", unit=" + unit + ", concentration=" + concentration + ", concentration_unit=" + concentration_unit
				+ ", containers=" + containers + ", requested_amount=" + requested_amount + "]";
	}
}
