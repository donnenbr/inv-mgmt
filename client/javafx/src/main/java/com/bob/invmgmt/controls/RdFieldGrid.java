/*
 * class to setup a grid for fields (ie, a label and a text field next to it) with suitable defaults.
 */
package com.bob.invmgmt.controls;

import javafx.geometry.HPos;
import javafx.scene.layout.ColumnConstraints;
import javafx.scene.layout.GridPane;
import javafx.scene.Node;


public class RdFieldGrid extends GridPane {
	
	public RdFieldGrid() {
		super();
		
		this.getStyleClass().add("grid");
		
		ColumnConstraints labelColConstraint = new ColumnConstraints();
		labelColConstraint.setFillWidth(true);
		labelColConstraint.setHalignment(HPos.RIGHT);
		this.getColumnConstraints().add(0,labelColConstraint);
	}
	
	// add a row specifying the nodes as an array
	public void addOneRow(int idx, Node[] nodes) {
		for (int i = 0; i < nodes.length; ++i) {
			this.add(nodes[i], i, idx);
		}
	}
	
	// same, but add to the end of the grid
	public void addOneRow(Node[] nodes) {
		addOneRow(this.getRowCount(), nodes);
	}
	
	// same as above, but add many rows as an array of arrays
	public void addManyRows(int idx, Node [][] nodes) {
		for (int i = 0; i < nodes.length; ++i) {
			Node[] arr = nodes[i];
			addOneRow(idx+i, arr);
		}
	}
	
	public void addManyRows(Node [][] nodes) {
		int idx = this.getRowCount();
		for (int i = 0; i < nodes.length; ++i) {
			Node[] arr = nodes[i];
			addOneRow(idx+i, arr);
		}
	}
}
