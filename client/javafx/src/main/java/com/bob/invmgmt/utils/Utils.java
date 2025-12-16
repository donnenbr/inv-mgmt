package com.bob.invmgmt.utils;

import javafx.application.Application;

import javafx.scene.control.Alert;
import javafx.scene.control.Alert.AlertType;
import javafx.scene.control.ButtonType;

import javafx.scene.layout.StackPane;
import javafx.scene.Node;

import javafx.stage.Stage;

import java.util.Arrays;
import java.util.List;
import java.util.Set;

import com.bob.invmgmt.controls.*;

public class Utils {
	
	// we need this for various things - the main stage of the application
	static Stage mainStage = null;
	// and to access some features of the application, like the host services
	static Application app = null;
	
	public static Stage getMainStage() {
		return mainStage;
	}
	
	public static void setMainStage(Stage stage) {
		mainStage = stage;
	}
	
	public static Application getApp() {
		return app;
	}

	public static void setApp(Application app) {
		Utils.app = app;
	}

	public static Node getRoot() {
		return mainStage == null ? null : mainStage.getScene().getRoot();
	}
	
	// convenience method to create a string, int, or double text field with all the options
	public static RdBaseTextField createField(String type, String name, String initialValue, boolean required, Number minValue, Number maxValue) throws Exception {
		RdBaseTextField fld = null;
		if (type.equalsIgnoreCase("str")) {
			fld = new RdStringField();
			if (minValue != null) {
				((RdStringField)fld).setMinLength(minValue.intValue());
			}
			if (maxValue != null) {
				((RdStringField)fld).setMaxLength(maxValue.intValue());
			}
		}
		else if (type.equalsIgnoreCase("int")) {
			fld = new RdIntegerField();
			if (minValue != null) {
				((RdIntegerField)fld).setMinValue(minValue.intValue());
			}
			if (maxValue != null) {
				((RdIntegerField)fld).setMaxValue(maxValue.intValue());
			}
		}
		else if (type.equalsIgnoreCase("double")) {
			fld = new RdDoubleField();
			if (minValue != null) {
				((RdDoubleField)fld).setMinValue(minValue.intValue());
			}
			if (maxValue != null) {
				((RdDoubleField)fld).setMaxValue(maxValue.intValue());
			}
		}
		else {
			throw new RuntimeException("Field type " + type + " is invalid");
		}
		fld.setName(name);
		if (initialValue != null) {
			fld.setText(initialValue);
		}
		fld.setRequired(required);
		
		return fld;
	}

	// shorter call for above when you don't need all the options
	public static RdBaseTextField createField(String type, String name, String initialValue, boolean required) throws Exception {
		return createField(type, name, initialValue, required, null, null);
	}
	
	// display a handy info dialog
	public static void displayInfoDialog(String message) {
		Alert alert = new Alert(AlertType.INFORMATION);
		alert.setTitle("Inventory Management");
		alert.setHeaderText("");
		alert.setContentText(message);
		alert.show();
	}
	
	// same, for confirmation
	public static boolean displayConfirmationDialog(String message) {
		Alert alert = new Alert(AlertType.CONFIRMATION);
		alert.setTitle("Inventory Management");
		alert.setHeaderText("");
		alert.setContentText(message);
		alert.showAndWait();
		ButtonType btnType = alert.getResult();
		return ButtonType.OK.equals(btnType);
	}
	
	// same, for error
	public static void displayErrorDialog(String title, List<String> messages) {
		String prefix = messages.size() == 1 ? "" : "* ";
		Alert alert = new Alert(AlertType.ERROR);
		alert.setTitle("Inventory Management");
		alert.setHeaderText(title);
		StringBuilder bldr = new StringBuilder();
		for (int i = 0; i < messages.size(); ++i) {
			if (i != 0) {
				bldr.append("\n");
			}
			bldr.append(prefix).append(messages.get(i));
		}
		
		alert.setContentText(bldr.toString());
		alert.show();
	}
	
	// same, but for one message
	public static void displayErrorDialog(String title, String message) {
		List<String> messages = Arrays.asList(new String [] {message});
		displayErrorDialog(title, messages);
	}
	
	// convenience method to show a specific panel in a StackPane.  placed here instead of in a controller 
	// so it can have more general use.
	public static void displaySpackPaneChild(StackPane sp, Node child) {
		for (Node node : sp.getChildren()) {
			node.setVisible(node == child);
		}
	}
	
	// convenience method for looking up nodes by id.  better than having to
	// specify the leading "#" everywhere
	public static Node lookupById(Node parent, String id) {
		Set<Node> matches = parent.lookupAll("#" + id);
		return matches.size() < 1 ? null : matches.iterator().next();
	}
}
