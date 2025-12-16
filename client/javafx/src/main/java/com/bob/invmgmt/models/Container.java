/*
 * represents a container which may contain a sample or other containers.  NEVER BOTH!!!
 */
package com.bob.invmgmt.models;

import java.util.List;
import java.util.Objects;

public class Container implements Cloneable {
	
	protected Long id;
	// the container's unique barcode
	protected String barcode;
	// the container type - freezer, rack, vial, etc. 
	protected String container_type;
	// where it is located IN ITS PARENT, not the full location from freezer down to vial.
	protected String position;
	// the unique id of the lot, as well as the lot name and corresponding reagent name.
	// lots are production runs, like you see on a bottle of aspirin.  a container can
	// only contain a LOT of something, not just a REAGENT.
	protected Long lot_id;
	protected String lot;
	protected String reagent;
	// how much and the unit of measure
	protected Double amount;
	protected String unit;
	// same for the concentration
	protected Double concentration;
	protected String concentration_unit;

	// the child containers of this container.  ex: shelves in a freezer.
	protected List<Container> containers;

	public Container(Long id, String barcode, String container_type, String position, Long lot_id, String lot,
			String reagent, Double amount, String unit, Double concentration, String concentration_unit,
			List<Container> containers) {
		super();
		this.id = id;
		this.barcode = barcode;
		this.container_type = container_type;
		this.position = position;
		this.lot_id = lot_id;
		this.lot = lot;
		this.reagent = reagent;
		this.amount = amount;
		this.unit = unit;
		this.concentration = concentration;
		this.concentration_unit = concentration_unit;
		this.containers = containers;
	}
	
	// do i really need to explain the rest?????
	public Container() {
		super();
	}

	public Long getId() {
		return id;
	}

	public void setId(Long id) {
		this.id = id;
	}

	public String getBarcode() {
		return barcode;
	}

	public void setBarcode(String barcode) {
		this.barcode = barcode;
	}

	public String getContainer_type() {
		return container_type;
	}

	public void setContainer_type(String container_type) {
		this.container_type = container_type;
	}

	public Long getLot_id() {
		return lot_id;
	}

	public void setLot_id(Long lot_id) {
		this.lot_id = lot_id;
	}

	public String getLot() {
		return lot;
	}

	public void setLot(String lot) {
		this.lot = lot;
	}

	public String getReagent() {
		return reagent;
	}

	public void setReagent(String reagent) {
		this.reagent = reagent;
	}

	public Double getAmount() {
		return amount;
	}

	public void setAmount(Double amount) {
		this.amount = amount;
	}

	public String getUnit() {
		return unit;
	}

	public void setUnit(String unit) {
		this.unit = unit;
	}

	public Double getConcentration() {
		return concentration;
	}

	public void setConcentration(Double concentration) {
		this.concentration = concentration;
	}

	public String getConcentration_unit() {
		return concentration_unit;
	}

	public void setConcentration_unit(String concentration_unit) {
		this.concentration_unit = concentration_unit;
	}

	public List<Container> getContainers() {
		return containers;
	}

	public void setContainers(List<Container> containers) {
		this.containers = containers;
	}

	public String getPosition() {
		return position;
	}

	public void setPosition(String position) {
		this.position = position;
	}

	@Override
	public String toString() {
		return "Container [id=" + id + ", barcode=" + barcode + ", container_type=" + container_type + ", position="
				+ position + ", lot_id=" + lot_id + ", lot=" + lot + ", reagent=" + reagent + ", amount=" + amount
				+ ", unit=" + unit + ", concentration=" + concentration + ", concentration_unit=" + concentration_unit
				+ ", containers=" + containers + "]";
	}
	
	@Override
    public Container clone() throws CloneNotSupportedException {
        return (Container) super.clone(); //To change body of generated methods, choose Tools | Templates.
    }

	@Override
	public int hashCode() {
		return Objects.hash(amount, barcode, concentration, concentration_unit, container_type, containers, id, lot,
				lot_id, position, reagent, unit);
	}

	@Override
	public boolean equals(Object obj) {
		if (this == obj)
			return true;
		if (obj == null)
			return false;
		if (getClass() != obj.getClass())
			return false;
		Container other = (Container) obj;
		return Objects.equals(amount, other.amount) && Objects.equals(barcode, other.barcode)
				&& Objects.equals(concentration, other.concentration)
				&& Objects.equals(concentration_unit, other.concentration_unit)
				&& Objects.equals(container_type, other.container_type) && Objects.equals(containers, other.containers)
				&& Objects.equals(id, other.id) && Objects.equals(lot, other.lot)
				&& Objects.equals(lot_id, other.lot_id) && Objects.equals(position, other.position)
				&& Objects.equals(reagent, other.reagent) && Objects.equals(unit, other.unit);
	}
}
