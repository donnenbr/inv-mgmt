// javafx mvn plugin does NOT like this being in a package.
// or dr. bob does not have the patience to figure it out

// package com.bob.invmgmt;

import javafx.application.Application;
import javafx.scene.Scene;
import javafx.stage.Stage;

import com.bob.invmgmt.views.MainPanel;
import com.bob.invmgmt.Constants;

import com.bob.invmgmt.utils.Utils;

// run with mvn javafx:run

public class InvMgmtJavafx extends Application {

    @Override
    public void start(Stage stage) {
    	Utils.setApp(this);
    	Utils.setMainStage(stage);
    	
    	Scene scene = new Scene(new MainPanel(), 750, 800);
    	String css = this.getClass().getResource(Constants.CSS_FILE).toExternalForm();
    	scene.getStylesheets().add(css);
        
        // gives the close icon
        stage.setTitle("Inventory Management with JavaFX");
        stage.setScene(scene);
        stage.show();
    }
}