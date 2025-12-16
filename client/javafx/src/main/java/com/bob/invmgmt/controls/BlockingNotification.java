/*
 * a class which displays an info dialog AND completely disables the application and all its controls 
 * until it is closed.
 */
package com.bob.invmgmt.controls;

import javafx.application.Platform;
import javafx.geometry.Pos;
import javafx.geometry.Insets;
import javafx.scene.Node;
import javafx.scene.Scene;
import javafx.scene.control.Label;
import javafx.scene.layout.VBox;
import javafx.stage.Stage;

import java.util.concurrent.Callable;

import com.bob.invmgmt.utils.Utils;

public class BlockingNotification<T> extends Stage {
	private Node root;
	private Callable<T> callable;
	private T returnVal;
	private Exception error;
	
	public BlockingNotification (String title, String message, Callable<T> callable) {
		super();
		
		this.root = Utils.getRoot();
		
		VBox vbox = new VBox();
		vbox.setSpacing(15);
		vbox.setPadding(new Insets(20,20,20,20));
		vbox.setAlignment(Pos.CENTER);
		
		Label lbl = new Label(message);
		lbl.getStyleClass().add("important-message");
		vbox.getChildren().addAll(lbl, new Label("This dialog will close automatically"));
		Scene scene = new Scene(vbox);
		scene.getStylesheets().addAll(root.getScene().getStylesheets());
		setTitle(title);
        setScene(scene);
		
		this.callable = callable;
		
		initialize();
		
		// seems we don't need this!
		// vbox.setPrefWidth(Region.USE_COMPUTED_SIZE);
		// vbox.setPrefHeight(Region.USE_COMPUTED_SIZE);
		vbox.requestLayout();
		
		this.setResizable(true);
	}
	
	private void initialize() {
		
		BlockingNotification<T> dlg = this;
		
		this.setOnShown(evt -> {
			Thread t = new Thread() {
				public void run() {
					try {
						root.setDisable(true);
						System.out.println("*** start @ " + System.currentTimeMillis());
						T callResult = callable.call();
						dlg.setResult(callResult);
						System.out.println("*** end @ " + System.currentTimeMillis());
						// not on javafx app thread!!!  must close the dialog this way
					}
					catch (Exception ex) {
						error = ex;
						root.setDisable(false);
						System.out.println("Exception !!!! " + ex);
					}
					finally {
						Thread t2 = new Thread() {
							public void run() {
								dlg.close();
							}
						};
						Platform.runLater(t2);
					}
				}
			};
			t.start();
		});
		this.setOnHidden(evt -> {
				root.setDisable(false);
				System.out.println("*** size " + this.getHeight() + "h X " + this.getWidth() + " w");
		});
		// prevent closing via the X on the window
		this.setOnCloseRequest(evt -> {
			evt.consume();
		});
	}
	
	public T getResult() throws Exception {
		if (error != null) {
			throw error;
		}
		return returnVal;
	}
	
	public void setResult(T result) {
		this.returnVal = result;
	}
}
