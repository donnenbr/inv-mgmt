/*
 * an event signaling that the user wants to return to the pick list search panel.  like the other events
 * it is used to communicate this from the result panel to the parent panel so it can switch child panels.
 * 
 *  we may have been able to do this directly in the controller since all pick list panels share the same
 *  controller.  however, this is consistent with our other uses of events.
 */
package com.bob.invmgmt.events;

import javafx.event.Event;
import javafx.event.EventType;

public class PickListSearchEvent  extends Event {
	public static final EventType<PickListSearchEvent> EVENT_TYPE = new EventType<>(Event.ANY, "PICK_LIST_SEARCH_EVENT");
	// because the class is serializable
	private static final long serialVersionUID = 1L;
	
    public PickListSearchEvent() {
        super(EVENT_TYPE);
    }
}
