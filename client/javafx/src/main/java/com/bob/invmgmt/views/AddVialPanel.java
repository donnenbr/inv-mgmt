package com.bob.invmgmt.views;

import javafx.scene.control.ScrollPane;
import javafx.scene.control.Label;
import javafx.scene.control.Button;
import javafx.scene.control.Tooltip;
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
import com.bob.invmgmt.controllers.AddVialController;

public class AddVialPanel extends RdVBox {

	private RdStringField barcode;
	private RdStringField lot;
	private RdIntegerField amount;
	private RdIntegerField concentration;
	private RdBaseTextField fields [];
	private Button saveBtn;
	private ScrollPane errorScrollPane;
	
	private AddVialController panelController;
	
	public AddVialPanel() {
		super();
		try {
			initialize();
		}
		catch (Exception ex) {
			System.out.println("*** initialization error " + ex);
		}
	}
	
	private void initialize() throws Exception {
		this.setId("addVial");
		
		panelController = new AddVialController(this);
		
		barcode = (RdStringField)Utils.createField("str", "barcode", null, true, 8, null);
		barcode.setId(Constants.ADD_BARCODE);
		lot = (RdStringField)Utils.createField("str", "lot", null, true);
		lot.setId(Constants.ADD_LOT_NAME);
		amount = (RdIntegerField)Utils.createField("int", "amount", null, true, 1, 750);
		amount.setId(Constants.ADD_AMOUNT);
		concentration = (RdIntegerField)Utils.createField("int", "concentration", null, true, 1, 10);
		concentration.setId(Constants.ADD_CONCENTRATION);
		fields = new RdBaseTextField[] {barcode, lot, amount, concentration};
		
		RdFieldGrid fieldGrid = new RdFieldGrid();
		this.getChildren().add(fieldGrid);
		
		// lbl_2.setStyle("-fx-font-style: italic; -fx-font-size: 14");		
		// seems almost impossible to cancel an event, where we would BEEP the terminal when a non-digit is pressed
		// and NOT allow the character through.  although we can hold and restore the previous value, it always
		// moves the cursor to the start of the field.
		barcode.setPromptText("Enter at least " + barcode.getMinLength() + " characters");
		barcode.setTooltip(new Tooltip("Any alpha-numeric.  Must be at least " + barcode.getMinLength() + " characters long."));
		
		// one way
		/*
		fieldGrid.addRow(0, new Label("Barcode:"),barcode);
		fieldGrid.addRow(1, new Label("Lot Name:"), lot);
		fieldGrid.addRow(2, new Label("Amount (ul):"),amount);
		fieldGrid.addRow(3, new Label("Concentration (mM):"), concentration);
		*/
		
		// another way
		/*
		fieldGrid.addOneRow(new Node[] {new Label("Barcode:"),barcode});
		fieldGrid.addOneRow(new Node[] {new Label("Lot Name:"), lot});
		fieldGrid.addOneRow(new Node[] {new Label("Amount (ul):"),amount});
		fieldGrid.addOneRow(new Node[] {new Label("Concentration (mM):"), concentration});
		*/
		
		// all in one shot
		Node [][] allNodes = new Node [][] {
			{new Label("Barcode:"),barcode},
			{new Label("Lot Name:"), lot},
			{new Label("Amount (ul):"),amount},
			{new Label("Concentration (mM):"), concentration}
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
		saveBtn.setId(Constants.ADD_SAVE_BUTTON);
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
		errorScrollPane.setId(Constants.ADD_ERROR_MESSAGE);
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
