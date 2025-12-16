/* 
 * class representing the data sent to the backend to locate a container.
 */
package com.bob.invmgmt.models;

import java.util.Objects;

public class LocateContainer {
	
	// the barcode of the container to be located
	private String barcode;
	// same for the parent container
	private String parent_barcode;
	// the position within the parent
	private String position;
	
	public LocateContainer() {
		super();
	}

	public LocateContainer(String barcode, String parent_barcode, String position) {
		super();
		this.barcode = barcode;
		this.parent_barcode = parent_barcode;
		this.position = position;
	}

	public String getBarcode() {
		return barcode;
	}

	public void setBarcode(String barcode) {
		this.barcode = barcode;
	}

	public String getParent_barcode() {
		return parent_barcode;
	}

	public void setParent_barcode(String parent_barcode) {
		this.parent_barcode = parent_barcode;
	}

	public String getPosition() {
		return position;
	}

	public void setPosition(String position) {
		this.position = position;
	}

	@Override
	public int hashCode() {
		return Objects.hash(barcode, parent_barcode, position);
	}

	@Override
	public boolean equals(Object obj) {
		if (this == obj)
			return true;
		if (obj == null)
			return false;
		if (getClass() != obj.getClass())
			return false;
		LocateContainer other = (LocateContainer) obj;
		return Objects.equals(barcode, other.barcode) && Objects.equals(parent_barcode, other.parent_barcode)
				&& Objects.equals(position, other.position);
	}
}
