/*
 * 	an event signaling that the Pick List module should generate a pick list based on the
 * 	request data.  we pass the request data in the event so the handler can deal with it.
 * 
 *  these events are the way child panels communicate with their parents.  for instance, 
 *  this allows the search panel to signal a request so the parent can fetch the pick list
 *   info and switch to the result panel.  
 */
package com.bob.invmgmt.events;

import javafx.event.Event;
import javafx.event.EventType;

import java.util.List;

import com.bob.invmgmt.models.PickListItem;
public class GeneratePickListEvent  extends Event {
	public static final EventType<GeneratePickListEvent> EVENT_TYPE = new EventType<>(Event.ANY, "GENERATE_PICK_LIST_EVENT");
	private List<PickListItem> requestData;
	// because the class is serializable
	private static final long serialVersionUID = 1L;
	
    public GeneratePickListEvent(List<PickListItem> requestData) {
        super(EVENT_TYPE);
        this.requestData = requestData;
    }
    
    public List<PickListItem> getRequestData() {
    	return this.requestData;
    }
}
