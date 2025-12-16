/*
 * main panel for the pick list functionality.  it simply wraps the search and result panels, displaying
 * either as needed.
 */

package com.bob.invmgmt.views;

import javafx.scene.layout.VBox;
import javafx.scene.layout.StackPane;

import com.bob.invmgmt.events.GeneratePickListEvent;
import com.bob.invmgmt.events.PickListSearchEvent;

import com.bob.invmgmt.controllers.PickListController;
import com.bob.invmgmt.utils.Utils;
import com.bob.invmgmt.Constants;

public class PickListPanel extends VBox {
	
	private StackPane sp ;
	private PickListSearchPanel searchPnl;
	private PickListResultPanel resultPnl;
	private PickListController panelController;
	
	public PickListPanel() {
		super();
		try {
			initialize();
		}
		catch (Exception ex) {
			System.out.println("*** initialization error " + ex);
		}
	}

	private void initialize() throws Exception {
		this.setId("pickList");
		
		panelController = new PickListController(this);
		sp = new StackPane();
		sp.setId(Constants.PICKLIST_STACK_PANE);
		
		searchPnl = new PickListSearchPanel(panelController);
		searchPnl.setId(Constants.PICKLIST_SEARCH_PANEL);
		resultPnl = new PickListResultPanel(panelController);
		resultPnl.setId(Constants.PICKLIST_RESULT_PANEL);
		sp.getChildren().addAll(searchPnl, resultPnl);
		
		this.getChildren().add(sp);
		
		this.addEventHandler(GeneratePickListEvent.EVENT_TYPE, event -> {
        	event.consume();
        	
        	panelController.handleGeneratePickListEvent(this, event.getRequestData());   	
		});
		
		this.addEventHandler(PickListSearchEvent.EVENT_TYPE, event -> {
        	event.consume();
        	Utils.displaySpackPaneChild(sp, searchPnl);
        });
		
		Utils.displaySpackPaneChild(sp, searchPnl);
	}
}
