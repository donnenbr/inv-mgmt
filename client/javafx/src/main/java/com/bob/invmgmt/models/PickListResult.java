/*
 * class representing the data returned by the backend for a pick list request.  two lists of
 * items, one for those which are available and one for those which are not. 
 */
package com.bob.invmgmt.models;

import java.util.List;
import java.util.Objects;

public class PickListResult {
	// nuff said
	List<PickListResultItem> available;
	List<PickListResultItem> unavailable;

	public PickListResult() {
		super();
	}

	public List<PickListResultItem> getAvailable() {
		return available;
	}

	public void setAvailable(List<PickListResultItem> available) {
		this.available = available;
	}

	public List<PickListResultItem> getUnavailable() {
		return unavailable;
	}

	public void setUnavailable(List<PickListResultItem> unavailable) {
		this.unavailable = unavailable;
	}

	@Override
	public String toString() {
		return "PickListResult [available=" + available + ", unavailable=" + unavailable + "]";
	}

	@Override
	public int hashCode() {
		return Objects.hash(available, unavailable);
	}

	@Override
	public boolean equals(Object obj) {
		if (this == obj)
			return true;
		if (obj == null)
			return false;
		if (getClass() != obj.getClass())
			return false;
		PickListResult other = (PickListResult) obj;
		return Objects.equals(available, other.available) && Objects.equals(unavailable, other.unavailable);
	}
}
