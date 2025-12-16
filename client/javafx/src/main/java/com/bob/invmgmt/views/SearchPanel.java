package com.bob.invmgmt.views;

import javafx.scene.Node;
import javafx.scene.layout.StackPane;
import javafx.scene.control.Label;
import javafx.scene.control.Button;
import javafx.geometry.Pos;
import javafx.event.ActionEvent;
import javafx.event.EventHandler;

import javafx.scene.control.Separator;
import javafx.geometry.Orientation;

import com.bob.invmgmt.controls.*;
import com.bob.invmgmt.utils.Utils;
import com.bob.invmgmt.Constants;
import com.bob.invmgmt.events.ContainerSelectedEvent;

import com.bob.invmgmt.controllers.SearchController;

public class SearchPanel extends RdVBox {
	
	private RdStringField barcode;
	private Label containerType;
	private Button searchBtn;
	private Label errorLbl;
	private StackPane detailPane;
	private SampleContainerPanel samplePanel;
	private ParentContainerPanel parentPanel;
	
	private SearchController panelController;

	public SearchPanel() {
		super();
		try {
			initialize();
		}
		catch (Exception ex) {
			System.out.println("*** initialization error " + ex);
		}
	}
	
	private void initialize() throws Exception {
		this.setId("searchInventory");
		
		panelController = new SearchController(this);
		
		barcode = (RdStringField)Utils.createField("str", "barcode", null, true);
		barcode.setId(Constants.SEARCH_BARCODE);
		// no focus change handler for barcode.  we'll validate it when the search button is clicked
		containerType = new Label();
		containerType.setId(Constants.SEARCH_CONTAINER_TYPE);
		searchBtn = new Button("Search!");
		searchBtn.getStyleClass().add("small-button");
		errorLbl = new Label();
		errorLbl.setId(Constants.SEARCH_ERROR_LABEL);
		errorLbl.getStyleClass().add("error-message");
		errorLbl.setAlignment(Pos.TOP_LEFT);
		errorLbl.setVisible(false);
		
        searchBtn.setOnAction(new EventHandler<ActionEvent>() {
            public void handle(ActionEvent e)
            {
                panelController.doSearch();
            }
        });
        
        // also allow search when ENTER is typed in the search field
        barcode.setOnAction(new EventHandler<ActionEvent>() {
            public void handle(ActionEvent e)
            {
                panelController.doSearch();
            }
        });
		
		RdFieldGrid searchGrid = new RdFieldGrid();
		searchGrid.addOneRow(new Node [] {new Label("Barcode:"), barcode, searchBtn});
		searchGrid.addOneRow(new Node [] {new Label("Container Type:"), containerType});
		
		// we'll use a stack pane so we can easily flip between what's displayed on the bottom - errors, container detail,
		// or child container list
		detailPane = new StackPane();
		detailPane.setId(Constants.SEARCH_DETAIL_PANE);
		detailPane.setAlignment(Pos.BASELINE_CENTER);
		samplePanel = new SampleContainerPanel();
		samplePanel.setId(Constants.SEARCH_SAMPLE_CONTAINER_PANEL);
		samplePanel.setVisible(false);
		parentPanel = new ParentContainerPanel();
		parentPanel.setId(Constants.SEARCH_PARENT_CONTAINER_PANEL);
		parentPanel.setVisible(false);
		detailPane.getChildren().addAll(errorLbl, samplePanel, parentPanel);
		Separator sep = new Separator();
        sep.setOrientation(Orientation.HORIZONTAL);
        this.getChildren().addAll(searchGrid, sep, detailPane);
        
        this.addEventHandler(ContainerSelectedEvent.EVENT_TYPE, event -> {
        	event.consume();
            barcode.setText(event.getBarcode());
            panelController.doSearch();
        });
	}
}
