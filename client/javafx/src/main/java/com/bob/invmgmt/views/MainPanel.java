package com.bob.invmgmt.views;

// run with mvn clean compile javafx:run

import javafx.scene.layout.VBox;
import javafx.scene.control.TabPane;
import javafx.scene.control.Tab;
import javafx.scene.control.TabPane.TabClosingPolicy;

// VBox will cause the panel to take up the full width of the scene.  Pane does not.
public class MainPanel extends VBox {
	public MainPanel() {
		super();
		
		TabPane tp = new TabPane();
		tp.setTabClosingPolicy(TabClosingPolicy.UNAVAILABLE);
		Tab tab = new Tab("Add Vial");
		tab.setContent(new AddVialPanel());
		tp.getTabs().add(tab);
		
		tab = new Tab("Search");
		tab.setContent(new SearchPanel());
		tp.getTabs().add(tab);
		
		tab = new Tab("Locate Vial");
		tab.setContent(new LocateVialPanel());
		tp.getTabs().add(tab);
		
		tab = new Tab("Pick List");
		tab.setContent(new PickListPanel());
		tp.getTabs().add(tab);
		
		this.getChildren().add(tp);
	}
}
