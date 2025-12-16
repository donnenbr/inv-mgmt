package com.bob.invmgmt.views;

import javafx.scene.Node;
import javafx.scene.layout.HBox;
import javafx.scene.control.Label;
import javafx.scene.control.Button;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.event.ActionEvent;
import javafx.event.EventHandler;

import com.bob.invmgmt.controls.*;
import com.bob.invmgmt.utils.Utils;
import com.bob.invmgmt.models.Container;
import com.bob.invmgmt.Constants;
import com.bob.invmgmt.controllers.SearchController;

public class SampleContainerPanel extends  RdVBox {
	
	private RdIntegerField amount, concentration;
	// we'll use labels for these instead of readonly text fields because the position can be a bit long and
	// adjusting its width will make them all wider.
	private Label position;
	private Label reagentName;
	private Label lotName;
	private RdBaseTextField fields [];
	
	private Button updateBtn, deleteBtn;
	private Label errorLbl;
	
	private Container cntr;
	
	private SearchController panelController;
	
	public SampleContainerPanel() {
		super();
		try {
			initialize();
		}
		catch (Exception ex) {
			System.out.println("*** initialization error " + ex);
		}
	}
	
	private void initialize() throws Exception {
		this.setId("searchInventorySampleContainer");
		
		panelController = new SearchController(this);
		position = new Label();
		position.setId(Constants.SEARCH_SAMPLE_CONTAINER_POSITION);
		reagentName = new Label();
		reagentName.setId(Constants.SEARCH_SAMPLE_CONTAINER_REAGENT);
		lotName = new Label();
		lotName.setId(Constants.SEARCH_SAMPLE_CONTAINER_LOT);
		
		amount = (RdIntegerField)Utils.createField("int", "amount", null, true, 1, 750);
		amount.setId(Constants.SEARCH_SAMPLE_CONTAINER_AMOUNT);
		concentration = (RdIntegerField)Utils.createField("int", "concentration", null, true, 2, 10);
		concentration.setId(Constants.SEARCH_SAMPLE_CONTAINER_CONCENTRATION);
		// just those to be validated
		fields = new RdBaseTextField[] {amount, concentration};
		
		RdFieldGrid fieldGrid = new RdFieldGrid();
		this.getChildren().add(fieldGrid);
		fieldGrid.addOneRow(new Node [] {new Label("Position:"), position});
		fieldGrid.addOneRow(new Node [] {new Label("Reagent Name:"), reagentName});
		fieldGrid.addOneRow(new Node [] {new Label("Lot Name:"), lotName});
		fieldGrid.addOneRow(new Node [] {new Label("Amount (ul):"), amount});
		fieldGrid.addOneRow(new Node [] {new Label("Concentration (mM):"), concentration});
		
		HBox buttonBar = new HBox();
		buttonBar.setAlignment(Pos.BASELINE_CENTER);
		updateBtn = new Button("Update");
		deleteBtn = new Button("Delete");
		updateBtn.getStyleClass().add("small-button");
		deleteBtn.getStyleClass().add("small-button");
		buttonBar.getChildren().addAll(updateBtn, deleteBtn);
		Insets buttonMargin = new Insets(10,10,10,10);
		HBox.setMargin(updateBtn, buttonMargin);
		HBox.setMargin(deleteBtn, buttonMargin);
		this.getChildren().add(buttonBar);
		
        updateBtn.setOnAction(new EventHandler<ActionEvent>() {
            public void handle(ActionEvent e)
            {
                doUpdate();
            }
        });
        deleteBtn.setOnAction(new EventHandler<ActionEvent>() {
            public void handle(ActionEvent e)
            {
                doDelete();
            }
        });
		
		errorLbl = new Label();
		errorLbl.setId(Constants.SEARCH_SAMPLE_CONTAINER_ERROR_LABEL);
		errorLbl.getStyleClass().add("error-message");
		errorLbl.setAlignment(Pos.TOP_LEFT);
		errorLbl.setVisible(false);
		this.getChildren().add(errorLbl);
	}
	
	public void setContainer(Container cntr) throws Exception {
		// make a copy of the source container because we'll use this for the save
		this.cntr = cntr.clone();
	}
	
	private void doUpdate() {
		Container updatedCntr = panelController.updateContainer(cntr);
		if (updatedCntr != null) {
			// update successful
			this.cntr = updatedCntr;
		}
	}
	
	private void doDelete() {
		panelController.deleteContainer(cntr);
	}
}
