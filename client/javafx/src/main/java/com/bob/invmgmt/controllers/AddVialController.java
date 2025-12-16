/* 
 * controller for the Add Vial operation
 */
package com.bob.invmgmt.controllers;

import com.bob.invmgmt.controls.RdBaseTextField;
import com.bob.invmgmt.exceptions.ApplicationException;
import com.bob.invmgmt.models.Container;
import com.bob.invmgmt.utils.Utils;
import com.bob.invmgmt.Constants;
import com.bob.invmgmt.views.AddVialPanel;

import javafx.scene.control.ScrollPane;
import javafx.scene.control.Button;
import javafx.scene.control.Label;

public class AddVialController {
	
	// so we can access nodes (ie, fields) by id.  could we have used the scene??  yes, but that assumes the
	// ids for the nodes are unique throughout the app.  this way they only have to be unique within the 
	// panel and its children.
	private AddVialPanel panel;

	public AddVialController(AddVialPanel panel) {
		this.panel = panel;
	}

	// validate a field when the user leaves it.  dr. bob holds the user for ransom and does NOT let you
	// leave the field if it is in error.
	public void handleFieldChange(RdBaseTextField fld) {
		boolean valid = fld.validate();
		// get the error message label
		ScrollPane errorScrollPane = (ScrollPane)panel.lookup("#" + Constants.ADD_ERROR_MESSAGE);
		Label errorMsgLbl = (Label) errorScrollPane.getContent();
		if (valid) {
			// clear all errors in the error area
			fld.getStyleClass().removeAll("error-field");
			errorMsgLbl.setText("");
		}
		else {
			// put the errors in the error area
			fld.getStyleClass().add("error-field");
			errorMsgLbl.setText(String.join("\n", fld.getErrors()));
		}
		errorScrollPane.setVisible(!valid);
		
		// only enable the save button if the field is error free
		Button saveBtn = (Button)panel.lookup("#" + Constants.ADD_SAVE_BUTTON);
		saveBtn.setDisable(!valid);
		// return to the field if it is not valid
		// we still support a scroll pane in case there are multiple errors.  maybe we'll use that if the
		// post to the backend fails, as opposed to showing a dialog???
		if (!valid) {
			fld.requestFocus();
		}
	}
	
	// the save operation
	public void doSave() {
		try {
			// get the fields
			RdBaseTextField barcode = (RdBaseTextField)Utils.lookupById(panel,Constants.ADD_BARCODE);
			RdBaseTextField lot = (RdBaseTextField)Utils.lookupById(panel,Constants.ADD_LOT_NAME);
			RdBaseTextField amount = (RdBaseTextField)Utils.lookupById(panel,Constants.ADD_AMOUNT);
			RdBaseTextField concentration = (RdBaseTextField)Utils.lookupById(panel,Constants.ADD_CONCENTRATION);
			// ideally if we get to this point the fields are valid.  we can get here with invalid fields only 
			// if the user switches tabs, then switches back again.  in that case, the backend will catch
			// any errors
			
			// populate a container object to send to the backend
			Container cntr = new Container();
			cntr.setBarcode(barcode.getValue());
			cntr.setLot(lot.getValue());
			cntr.setAmount(Double.valueOf(amount.getValue()));
			cntr.setConcentration(Double.valueOf(concentration.getValue()));
			
			// now send the container info to the backend.  no exception -> raging success
			ContainerController controller = new ContainerController();
			cntr = controller.addContainer(cntr);
			Utils.displayInfoDialog("Vial successfully added!");
		}
		catch (ApplicationException ae) {
			// custom error return from the backend (usually bad data)
			Utils.displayErrorDialog("Save vial failed!!", ae.getMessages());
		}
		catch (Throwable t) {
			// some other error
			Utils.displayErrorDialog("Save vial failed!!", t.getMessage());
		}
	}
}
