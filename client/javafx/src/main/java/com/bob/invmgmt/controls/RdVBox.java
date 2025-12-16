/*
 * a VBOX with suitable defaults so the app has a consistent look and we don't need to constantly set them.
 */
package com.bob.invmgmt.controls;

import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.layout.VBox;

public class RdVBox extends VBox {

	public RdVBox() {
		super();
		
		this.setSpacing(15);
		this.setPadding(new Insets(20, 30, 20, 30));
		this.setAlignment(Pos.TOP_CENTER);
		this.setFillWidth(true);
	}
}
