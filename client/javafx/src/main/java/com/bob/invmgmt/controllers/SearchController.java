/*
 * controller for the search container operation
 */
package com.bob.invmgmt.controllers;

import com.bob.invmgmt.controls.RdBaseTextField;
import com.bob.invmgmt.events.ContainerSelectedEvent;
import com.bob.invmgmt.exceptions.ApplicationException;
import com.bob.invmgmt.exceptions.NotFoundException;
import com.bob.invmgmt.models.Container;
import com.bob.invmgmt.utils.Utils;

import java.util.ArrayList;
import java.util.List;

import com.bob.invmgmt.Constants;
import com.bob.invmgmt.views.SampleContainerPanel;
import com.bob.invmgmt.views.ParentContainerPanel;
import com.bob.invmgmt.controls.RdVBox;

import javafx.scene.layout.Pane;
import javafx.collections.FXCollections;
import javafx.scene.Node;
import javafx.scene.control.Label;
import javafx.scene.control.TableView;

public class SearchController {
	
	// so we can access nodes (ie, fields) by id.  could we have used the scene??  yes, but that assumes the
	// ids for the nodes are unique throughout the app.  this way they only have to be unique within the 
	// panel and its children.
	// NOTE - this controller is used by the main panel as well as the child container list panel and the
	// sample container panel, so we use the common super class.
	private RdVBox panel;

	public SearchController(RdVBox panel) {
		this.panel = panel;
	}
	
	// display a specific node (panel) within a pane, which is assumed to be a stackpane
	private void displayInfoPanel(Node node) {
		Pane detailPane = (Pane)Utils.lookupById(panel,Constants.SEARCH_DETAIL_PANE);
		for (Node n : detailPane.getChildren()) {
			n.setVisible(n == node);
		}
	}
	
	// perform the search operation
	public void doSearch() {
		RdBaseTextField barcode = (RdBaseTextField)Utils.lookupById(panel,Constants.SEARCH_BARCODE);
		Label errorLbl = (Label)Utils.lookupById(panel,Constants.SEARCH_ERROR_LABEL);
		if (barcode.validate()) {
			try {
				// lookup the container data
				Label containerType = (Label)Utils.lookupById(panel,Constants.SEARCH_CONTAINER_TYPE);
				ContainerController controller = new ContainerController();
				Container cntr = controller.getContainerByBarcode(barcode.getValue());
				containerType.setText(cntr.getContainer_type());
				// no children -> assumed to be a sample container, so display that panel
				if (cntr.getContainers() == null) {
					SampleContainerPanel samplePanel = (SampleContainerPanel)Utils.lookupById(panel,Constants.SEARCH_SAMPLE_CONTAINER_PANEL);
					setSampleContainer(samplePanel, cntr);
					samplePanel.setContainer(cntr);
					displayInfoPanel(samplePanel);
				}
				else {
					// it has children, so display the child container panel
					ParentContainerPanel parentPanel = (ParentContainerPanel)Utils.lookupById(panel,Constants.SEARCH_PARENT_CONTAINER_PANEL);
					setParentContainer(cntr);
					displayInfoPanel(parentPanel);
				}
			}
			catch (NotFoundException nfe) {
				// returned when the backend sends an http 404 error.
				errorLbl.setText("Barcode is invalid");
				displayInfoPanel(errorLbl);
			}
			// app specific error
			catch (ApplicationException ae) {
				// Utils.displayErrorDialog("Search failed!!", ae.getMessages());
				StringBuilder bldr = new StringBuilder("Search failed:\n");
				bldr.append(String.join("\n", barcode.getErrors()));
				errorLbl.setText(bldr.toString());
				displayInfoPanel(errorLbl);
			}
			// some other error
			catch (Throwable t) {
				Utils.displayErrorDialog("Search failed!!", t.getMessage());
			}
		}
		else {
			errorLbl.setText(String.join("\n", barcode.getErrors()));
			displayInfoPanel(errorLbl);
		}
	}
	
	// handler for selecting a container from among the children.  use an event to tell the
	// listener about it.
	public void handleContainerSelect(Container cntr) {
		if (cntr != null && cntr.getBarcode() != null && cntr.getBarcode().trim().length() > 0) {
			ContainerSelectedEvent e = new ContainerSelectedEvent(cntr.getBarcode());
			ContainerSelectedEvent.fireEvent(panel, e);
		}
	}
	
	// set the values for a parent container and its children 
	public void setParentContainer(Container cntr) throws Exception {
		Label position = (Label)Utils.lookupById(panel,Constants.SEARCH_PARENT_POSITION);
		// set the fields
		if (cntr.getPosition() == null || cntr.getPosition().trim().length() < 1) {
			position.setText("None");
		}
		else {
			position.setText(cntr.getPosition());
		}
		
		try {
			TableView<Container> childContainerTbl = (TableView<Container>)Utils.lookupById(panel,Constants.SEARCH_CHILD_CONTAINER_TABLE);
			childContainerTbl.setItems(FXCollections.observableList(cntr.getContainers()));
		}
		catch (Throwable t) {
			Utils.displayErrorDialog("Exception !!", t.getMessage());
		}
	}
	
	// setup the values for a sample container
	public void setSampleContainer(SampleContainerPanel sampleCntrPanel, Container cntr) {
		Label position = (Label)Utils.lookupById(panel,Constants.SEARCH_SAMPLE_CONTAINER_POSITION);
		if (cntr.getPosition() == null || cntr.getPosition().trim().length() < 1) {
			position.setText("None");
		}
		else {
			position.setText(cntr.getPosition());
		}
		Label reagentName = (Label)Utils.lookupById(panel,Constants.SEARCH_SAMPLE_CONTAINER_REAGENT);
		Label lotName = (Label)Utils.lookupById(panel,Constants.SEARCH_SAMPLE_CONTAINER_LOT);
		RdBaseTextField amount = (RdBaseTextField)Utils.lookupById(panel,Constants.SEARCH_SAMPLE_CONTAINER_AMOUNT);
		RdBaseTextField concentration = (RdBaseTextField)Utils.lookupById(panel,Constants.SEARCH_SAMPLE_CONTAINER_CONCENTRATION);
		reagentName.setText(cntr.getReagent());
		lotName.setText(cntr.getLot());
		amount.setText(String.format("%.0f", cntr.getAmount()));
		concentration.setText(String.format("%.0f", cntr.getConcentration()));
		try {
			sampleCntrPanel.setContainer(cntr);
		}
		catch (Exception ex) {
			Utils.displayErrorDialog(null, "Error setting container - " + ex.getMessage());
		}
	}
	
	// update a container via the backend
	public Container updateContainer(Container cntr) {
		Container newCntr = null;
		// we only need to update the amount and concentration.
		RdBaseTextField amount = (RdBaseTextField)Utils.lookupById(panel,Constants.SEARCH_SAMPLE_CONTAINER_AMOUNT);
		RdBaseTextField concentration = (RdBaseTextField)Utils.lookupById(panel,Constants.SEARCH_SAMPLE_CONTAINER_CONCENTRATION);
		List<String> allErrors = new ArrayList<>();
		for (RdBaseTextField fld : new RdBaseTextField [] { amount,concentration }) {
			if (!fld.validate()) {
				allErrors.addAll(fld.getErrors());
			}
		}
		Label errorLbl = (Label)Utils.lookupById(panel,Constants.SEARCH_SAMPLE_CONTAINER_ERROR_LABEL);
		if (allErrors.size() > 0) {
			StringBuilder bldr = new StringBuilder("Please fix the following errors:");
			for (String s : allErrors) {
				bldr.append("\n  * ").append(s);
			}
			errorLbl.setText(bldr.toString());
			errorLbl.setVisible(true);
		}
		else {
			errorLbl.setText("");
			errorLbl.setVisible(false);
			try {
				cntr.setAmount(Double.valueOf(amount.getText()));
				cntr.setConcentration(Double.valueOf(concentration.getText()));
				ContainerController controller = new ContainerController();
				newCntr = controller.updateContainer(cntr);
				// the updated value becomes the new container
				Utils.displayInfoDialog("Update successful!!!");
			}
			catch (ApplicationException ae) {
				Utils.displayErrorDialog("Update failed!!", ae.getMessages());
			}
			catch (Throwable t) {
				Utils.displayErrorDialog("Update failed!!", t.getMessage());
			}
		}
		return newCntr;
	}
	
	// delete a container from the backend
	public void deleteContainer(Container cntr) {
		Label errorLbl = (Label)Utils.lookupById(panel,Constants.SEARCH_SAMPLE_CONTAINER_ERROR_LABEL);
		errorLbl.setText("");
		errorLbl.setVisible(false);
		try {
			boolean b = Utils.displayConfirmationDialog("Are you sure you want to delete the container??");
			if (b) {
				ContainerController controller = new ContainerController();
				Container temp = controller.deleteContainer(cntr);
				Utils.displayInfoDialog("Delete successful!!!");
			}
		}
		catch (ApplicationException ae) {
			Utils.displayErrorDialog("Delete failed!!", ae.getMessages());
		}
		catch (Throwable t) {
			Utils.displayErrorDialog("Delete failed!!", t.getMessage());
		}
	}
}
