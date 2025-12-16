/*
 * our own special table cell with custom editing and navigation supporting moving to the next cell when
 * you move to the next field via ENTER or TAB.  no support for previous field via BACK-TAB because we
 * can't pass the key pressed or direction to the commitEdit method.
 */
package com.bob.invmgmt.controls;

import javafx.scene.control.TextField;
import javafx.scene.control.cell.TextFieldTableCell;
import javafx.scene.input.KeyCode;
import javafx.scene.input.KeyEvent;
import javafx.util.StringConverter;
import javafx.util.converter.DefaultStringConverter;

public class RdTableCell<S,T> extends TextFieldTableCell {
	public RdTableCell(StringConverter converter) {
			super();
			setConverter(converter);
			setEditable(true);

			// capture the tab so it is not used to move focus to the next item.
			// use it to commit the change.  we do not process TAB when ctrl, shift, etc. are also pressed.
			// ctrl-TAB to move back would be nice, but no way to detect that in the commit handler.
			this.addEventFilter(KeyEvent.KEY_PRESSED, event -> {
	            if (event.getCode() == KeyCode.TAB && 
	            		!(event.isAltDown() || event.isControlDown() || event.isMetaDown() || event.isShiftDown())) {
	                // prevent further processing
	                event.consume();
	                // the "graphic" is the UI control used to edit the cell.  a text field.
	                TextField fld = (TextField) this.getGraphic();
	                // now do the commit.  must be run through the converter to create an object of the correct type
	                this.commitEdit(this.getConverter().fromString(fld.getText()));
	            }
	        });
		}
	public RdTableCell() {
		this(new DefaultStringConverter());
	}
	
	// @Override
	public void updateItem(Object item, boolean empty) {
		super.updateItem(item, empty);

		// display the value in the cell.  no, it ain't automatic after the update.
		if (empty || item == null) {
			setText(null);
			setGraphic(null);
		} else {
			setText(this.getConverter().toString(item));
		}
	}
}