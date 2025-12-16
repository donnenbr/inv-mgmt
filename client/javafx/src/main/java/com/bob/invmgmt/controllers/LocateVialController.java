/*
 * controller for the locate container operation.  hauntingly similar to AddContainerController
 * because they're really not that different.
 */
package com.bob.invmgmt.controllers;

import com.bob.invmgmt.controls.RdBaseTextField;
import com.bob.invmgmt.exceptions.ApplicationException;
import com.bob.invmgmt.models.Container;
import com.bob.invmgmt.models.LocateContainer;
import com.bob.invmgmt.utils.Utils;
import com.bob.invmgmt.Constants;
import com.bob.invmgmt.views.LocateVialPanel;

import javafx.scene.control.ScrollPane;
import javafx.scene.control.Button;
import javafx.scene.control.Label;

public class LocateVialController {
	
	// so we can access nodes (ie, fields) by id.  could we have used the scene??  yes, but that assumes the
	// ids for the nodes are unique throughout the app.  this way they only have to be unique within the 
	// panel and its children.
	private LocateVialPanel panel;

	public LocateVialController(LocateVialPanel panel) {
		this.panel = panel;
	}

	// validate a field when the user leaves it.  dr. bob holds the user for ransom and does NOT let you
	// leave the field if it is in error.
	public void handleFieldChange(RdBaseTextField fld) {
		boolean valid = fld.validate();
		// get the error message label
		ScrollPane errorScrollPane = (ScrollPane)panel.lookup("#" + Constants.LOCATE_ERROR_MESSAGE);
		Label errorMsgLbl = (Label) errorScrollPane.getContent();
		if (valid) {
			fld.getStyleClass().removeAll("error-field");
			errorMsgLbl.setText("");
		}
		else {
			fld.getStyleClass().add("error-field");
			errorMsgLbl.setText(String.join("\n", fld.getErrors()));
		}
		errorScrollPane.setVisible(!valid);
		
		Button saveBtn = (Button)panel.lookup("#" + Constants.LOCATE_SAVE_BUTTON);
		saveBtn.setDisable(!valid);
		// return to the field if it is not valid
		// we still support a scroll pane in case there are multiple errors.  maybe we'll use that if the
		// post to the backend fails, as opposed to showing a dialog???
		if (!valid) {
			fld.requestFocus();
		}
	}
	
	public void doSave() {		
		try {
			// get the fields and populate the model for locating a container
			RdBaseTextField vialBarcode = (RdBaseTextField)Utils.lookupById(panel,Constants.LOCATE_VIAL_BARCODE);
			RdBaseTextField rackBarcode = (RdBaseTextField)Utils.lookupById(panel,Constants.LOCATE_RACK_BARCODE);
			RdBaseTextField position = (RdBaseTextField)Utils.lookupById(panel,Constants.LOCATE_POSITION);
			LocateContainer locateCntr = new LocateContainer(
					vialBarcode.getValue(),
					rackBarcode.getValue(),
					position.getValue());
			
			// send the model to the backend.  no errors, success!!!
			ContainerController controller = new ContainerController();
			Container cntr = controller.locateContainer(locateCntr);
			Utils.displayInfoDialog("Vial successfully located!");
		}
		catch (ApplicationException ae) {
			// application specific error - probably bad data
			Utils.displayErrorDialog("Locate vial failed!!", ae.getMessages());
		}
		catch (Throwable t) {
			// some other error
			Utils.displayErrorDialog("Locate vial failed!!", t.getMessage());
		}
	}
}
