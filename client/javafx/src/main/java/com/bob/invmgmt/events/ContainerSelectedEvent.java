/*
 * 	an event signaling that a container in the child container table in the Search module has
 * 	been selected.  we pass the barcode in the event (not the container because it must be 
 * 	serializable) and let the event handler deal with it.
 * 
 *  these events are the way child panels communicate with their parents.  for instance, 
 *  this allows the child container panel to signal a container selection so the parent can
 *  fetch the container info and, if needed, switch to the sample container panel.  
 */
package com.bob.invmgmt.events;

import javafx.event.Event;
import javafx.event.EventType;

public class ContainerSelectedEvent  extends Event {
	public static final EventType<ContainerSelectedEvent> EVENT_TYPE = new EventType<>(Event.ANY, "CONTAINER_SELECTED_EVENT");
	private String barcode;
	// because the class is serializable
	private static final long serialVersionUID = 1L;
	
    public ContainerSelectedEvent(String barcode) {
        super(EVENT_TYPE);
        this.barcode = barcode;
    }
    
    public String getBarcode() {
    	return barcode;
    }
}
