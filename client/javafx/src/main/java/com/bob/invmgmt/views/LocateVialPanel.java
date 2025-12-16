package com.bob.invmgmt.views;

import javafx.scene.control.ScrollPane;
import javafx.scene.control.Label;
import javafx.scene.control.Button;
import javafx.beans.property.ReadOnlyBooleanProperty;
import javafx.beans.value.ChangeListener;
import javafx.event.ActionEvent;
import javafx.event.EventHandler;
import javafx.scene.Node;

import javafx.scene.control.Separator;
import javafx.geometry.Orientation;

import com.bob.invmgmt.Constants;
import com.bob.invmgmt.controls.*;
import com.bob.invmgmt.utils.Utils;
import com.bob.invmgmt.controllers.LocateVialController;

public class LocateVialPanel extends RdVBox {

	private RdStringField vialBarcode;
	private RdStringField rackBarcode;
	private RdStringField position;
	
	private RdBaseTextField fields [];
	private Button saveBtn;
	private ScrollPane errorScrollPane;
	
	private LocateVialController panelController;
	
	public LocateVialPanel() {
		super();
		try {
			initialize();
		}
		catch (Exception ex) {
			System.out.println("*** initialization error " + ex);
		}
	}
	
	private void initialize() throws Exception {
		this.setId("locateVial");
		
		panelController = new LocateVialController(this);
		
		vialBarcode = (RdStringField)Utils.createField("str", "vial barcode", null, true, 8, null);
		vialBarcode.setId(Constants.LOCATE_VIAL_BARCODE);
		rackBarcode = (RdStringField)Utils.createField("str", "rack barcode", null, true, 8, null);
		rackBarcode.setId(Constants.LOCATE_RACK_BARCODE);
		position = (RdStringField)Utils.createField("str", "position", null, true);
		position.setId(Constants.LOCATE_POSITION);
		fields = new RdBaseTextField[] {vialBarcode, rackBarcode, position};
		
		RdFieldGrid fieldGrid = new RdFieldGrid();
		this.getChildren().add(fieldGrid);
		
		Node [][] allNodes = new Node [][] {
			{new Label("Vial Barcode:"),vialBarcode},
			{new Label("Rack Barcode:"), rackBarcode},
			{new Label("Position:"), position}
		};
		fieldGrid.addManyRows(allNodes);
		
		// this.getChildren().add(new Label(" "));
		Label requiredLbl = new Label("All fields are required");
		requiredLbl.getStyleClass().add("important-message");
		this.getChildren().add(requiredLbl);
		
		// create an "on-focus" listener to handle focus gained AND focus lost.
		// there are no OnFcus events so we look for a change in the focus property
		ChangeListener<? super Boolean> fldVal = (observable, oldValue, newValue) -> {
			// get the field involved.  easier than trying to put this in the handler.
			RdBaseTextField fld = (RdBaseTextField)((ReadOnlyBooleanProperty) observable).getBean();
			this.onFocus(fld, oldValue, newValue);
		};
		// apply to all fields
		for (RdBaseTextField fld : fields) {
			fld.focusedProperty().addListener(fldVal);
		}
		
		// add save button
		saveBtn = new Button("Save!");
		saveBtn.setId(Constants.LOCATE_SAVE_BUTTON);
		saveBtn.setDisable(true);
		// responds to left click or ENTER
		EventHandler<ActionEvent> saveHandler = new EventHandler<ActionEvent>() {
            public void handle(ActionEvent e)
            {
                panelController.doSave();
            }
        };
        
        Separator sep = new Separator();
        sep.setOrientation(Orientation.HORIZONTAL);
        this.getChildren().add(sep);
        
        saveBtn.setOnAction(saveHandler);
		this.getChildren().add(saveBtn);
		
		errorScrollPane = new ScrollPane();
		errorScrollPane.setId(Constants.LOCATE_ERROR_MESSAGE);
		Label errorMsgLbl = new Label();
		errorMsgLbl.getStyleClass().add("error-message");
		
		errorScrollPane.setVisible(false);
		// this will make it fit to the bottom of the pane
		errorScrollPane.setPrefHeight(10000);
		errorScrollPane.setContent(errorMsgLbl);
		this.getChildren().add(errorScrollPane);
	}
	
	private void onFocus(RdBaseTextField fld, boolean oldValue, boolean newValue ) {
		if (newValue) {
	    	// entered the field - restore error state???
	    } else {
	        // exited the field
			panelController.handleFieldChange(fld);
	    }
	}
	
}
