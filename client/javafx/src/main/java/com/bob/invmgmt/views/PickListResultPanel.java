/*
 * panel to display the results of the pick list search.  it contains separate tables for samples which are
 * available and those which are not.  it also contains various options on the bottom. 
 */

package com.bob.invmgmt.views;

import java.text.NumberFormat;

import com.bob.invmgmt.Constants;
import com.bob.invmgmt.controllers.PickListController;
import com.bob.invmgmt.controls.RdTableCell;
import com.bob.invmgmt.controls.RdVBox;
import com.bob.invmgmt.models.PickListResult;
import com.bob.invmgmt.models.PickListResultItem;
import com.bob.invmgmt.utils.Utils;

import javafx.collections.FXCollections;
import javafx.geometry.Insets;
import javafx.geometry.Orientation;
import javafx.geometry.Pos;
import javafx.scene.control.Button;
import javafx.scene.control.CheckBox;
import javafx.scene.control.Label;
import javafx.scene.control.Separator;
import javafx.scene.control.TableColumn;
import javafx.scene.control.TableView;
import javafx.scene.control.Tooltip;
import javafx.scene.control.cell.PropertyValueFactory;
import javafx.scene.layout.HBox;
import javafx.scene.layout.VBox;
import javafx.util.converter.DoubleStringConverter;
import javafx.util.converter.FormatStringConverter;

public class PickListResultPanel extends RdVBox {
	private PickListController panelController;
	
	private TableView<PickListResultItem> availableSamples, unavailableSamples;
	// vboxes will hold a title label and a table view, allowing both to be shown/hidden at once 
	// the RdVBox tweaks are almost exactly what we need and will adjust after construction
	private RdVBox availableSection, unavailableSection;
	
	// too lazy to use an id just to access it for disabling at the end of the code
	private Button printBtn, displayBtn;

	// note that both the search and result panels use the same controller, so it is passed in from
	// the parent panel.
	public PickListResultPanel(PickListController panelController) {
		super();
		
		try {
			this.panelController = panelController;
			initialize();
		} catch (Exception ex) {
			System.out.println("*** initialization error " + ex);
			ex.printStackTrace();
		}
	}
	
	private void initialize() throws Exception {
		availableSection = new RdVBox();
		availableSection.setId(Constants.PICKLIST_RESULT_AVAILABLE_SAMPLES);
		availableSection.setPadding(new Insets(0,0,0,0));
		availableSamples = new TableView<>();
		availableSamples.setEditable(false);
		availableSamples.setColumnResizePolicy(TableView.CONSTRAINED_RESIZE_POLICY_ALL_COLUMNS);
		// custom message for when the table is empty
		availableSamples.setPlaceholder(new Label("There are no Available Samples"));
		
		// note - PickListResulItem extends Container, so the amount and request_amount are Double, not Integer.
		// try FormatStringConverter to display amounts as ints
		FormatStringConverter intConverter = new FormatStringConverter(NumberFormat.getIntegerInstance());
		DoubleStringConverter dblConverter = new DoubleStringConverter();
		TableColumn<PickListResultItem, String> availReagentCol = new TableColumn<>("Reagent");
		availReagentCol.setCellValueFactory(new PropertyValueFactory<PickListResultItem, String>("reagent"));
		availReagentCol.setCellFactory(column -> {
			return new RdTableCell<PickListResultItem,String>();
		});
		TableColumn<PickListResultItem, Double> availRequestedAmountCol = new TableColumn<>("Requested\nAmt (ul)");
		availRequestedAmountCol.setCellValueFactory(new PropertyValueFactory<PickListResultItem, Double>("requested_amount"));
		availRequestedAmountCol.setCellFactory(column -> {
			return new RdTableCell<PickListResultItem,Double>(intConverter);
		});
		TableColumn<PickListResultItem, String> availBarcodeCol = new TableColumn<>("Barcode");
		availBarcodeCol.setCellValueFactory(new PropertyValueFactory<PickListResultItem, String>("barcode"));
		availBarcodeCol.setCellFactory(column -> {
			return new RdTableCell<PickListResultItem,String>();
		});
		TableColumn<PickListResultItem, String> availLocationCol = new TableColumn<>("Location");
		availLocationCol.setCellValueFactory(new PropertyValueFactory<PickListResultItem, String>("position"));
		availLocationCol.setCellFactory(column -> {
			return new RdTableCell<PickListResultItem,String>();
		});
		// availLocationCol.setPrefWidth(150);
		TableColumn<PickListResultItem, Double> availAmountCol = new TableColumn<>("Container\nAmt (ul)");
		availAmountCol.setCellValueFactory(new PropertyValueFactory<PickListResultItem, Double>("amount"));
		availAmountCol.setCellFactory(column -> {
			return new RdTableCell<PickListResultItem,Integer>(intConverter);
		});
		// we'll still use double for the concentration
		TableColumn<PickListResultItem, Double> availConcentrationCol = new TableColumn<>("Conc. (uM)");
		availConcentrationCol.setCellValueFactory(new PropertyValueFactory<PickListResultItem, Double>("concentration"));
		availConcentrationCol.setCellFactory(column -> {
			return new RdTableCell<PickListResultItem,Double>(dblConverter);
		});
		
		availableSamples.getColumns().addAll(availReagentCol, availRequestedAmountCol, availBarcodeCol,
				availLocationCol, availAmountCol, availConcentrationCol);
		
		Label lbl = new Label("Available Samples");
		lbl.getStyleClass().add("title");
		availableSection.getChildren().addAll(lbl, availableSamples);
		
		///////////////////////////////////////////////////////////////////////////////////////////////////////////
	
		unavailableSection = new RdVBox();
		unavailableSection.setId(Constants.PICKLIST_RESULT_UNAVAILABLE_SAMPLES);
		unavailableSection.setPadding(new Insets(0,0,0,0));
		unavailableSamples = new TableView<>();
		unavailableSamples.setEditable(false);
		unavailableSamples.setColumnResizePolicy(TableView.CONSTRAINED_RESIZE_POLICY_ALL_COLUMNS);
		unavailableSamples.setPlaceholder(new Label("There are no Unavailable Samples"));
		
		TableColumn<PickListResultItem, String> unavailReagentCol = new TableColumn<>("Reagent");
		unavailReagentCol.setCellValueFactory(new PropertyValueFactory<PickListResultItem, String>("reagent"));
		unavailReagentCol.setCellFactory(column -> {
			return new RdTableCell<PickListResultItem,String>();
		});
		
		availLocationCol.setPrefWidth(200);
		TableColumn<PickListResultItem, Double> unavailAmountCol = new TableColumn<>("Container\nAmt (ul)");
		unavailAmountCol.setCellValueFactory(new PropertyValueFactory<PickListResultItem, Double>("amount"));
		unavailAmountCol.setCellFactory(column -> {
			return new RdTableCell<PickListResultItem,Integer>(intConverter);
		});
		TableColumn<PickListResultItem, Double> unavailConcentrationCol = new TableColumn<>("Conc. (uM)");
		unavailConcentrationCol.setCellValueFactory(new PropertyValueFactory<PickListResultItem, Double>("concentration"));
		unavailConcentrationCol.setCellFactory(column -> {
			return new RdTableCell<PickListResultItem,Double>(dblConverter);
		});
		
		unavailableSamples.getColumns().addAll(unavailReagentCol, unavailAmountCol, unavailConcentrationCol);
		
		lbl = new Label("These samples are not available");
		lbl.getStyleClass().add("title");
		unavailableSection.getChildren().addAll(lbl, unavailableSamples);
		
		this.getChildren().addAll(availableSection, unavailableSection);
		
		Separator sep = new Separator();
        sep.setOrientation(Orientation.HORIZONTAL);
        this.getChildren().add(sep);
        
        HBox hb = new HBox();
        hb.setSpacing(30);
		// hb.setPadding(new Insets(30));
		hb.setAlignment(Pos.CENTER);
		// hb.setFillWidth(true);
        Button backBtn = new Button("Back to Request");
        backBtn.getStyleClass().add("small-button");
        backBtn.setOnAction(e -> {
        	panelController.returnToSearch();
        });
        hb.getChildren().add(backBtn);
        
        CheckBox showAvailCbox = new CheckBox("Show Available"), showUnavailCbox = new CheckBox("Show Unavailable"); 
        showAvailCbox.setSelected(true);
        showUnavailCbox.setSelected(true);
        hb.getChildren().addAll(showAvailCbox, showUnavailCbox);
        this.getChildren().add(hb);
        
        // event handlers for the check boxes.  note that if we change the visibility of a section, it STILL takes up
        // space.  so, we add/remove it from the parent to make it truely disappear.
        showAvailCbox.selectedProperty().addListener((event,oldVal,newVal) -> {
        	panelController.showHideAvailableSamples(newVal, this, availableSection);
        });
        showUnavailCbox.selectedProperty().addListener((event,oldVal,newVal) -> {
        	panelController.showHideUnavailableSamples(newVal, this, unavailableSection);
        });
        
        printBtn = new Button("Print Pick List");
        printBtn.getStyleClass().add("small-button");
        printBtn.setTooltip(new Tooltip("Print pick list report to the default printer"));
        printBtn.setOnAction(e -> {
        	panelController.printReport(availableSamples.getItems());
        });
        displayBtn = new Button("Display Pick List");
        displayBtn.getStyleClass().add("small-button");
        displayBtn.setTooltip(new Tooltip("Display pick list report in default viewer"));
        displayBtn.setOnAction(e -> {
        	panelController.displayReport(availableSamples.getItems());
        });
        VBox vbox = new VBox();
        vbox.setSpacing(5);
        vbox.setFillWidth(true);
        vbox.setAlignment(Pos.TOP_CENTER);
        vbox.getChildren().addAll(printBtn, displayBtn);
        hb.getChildren().add(vbox);
	}
	
	// apply the pick list data (supplied by the backend) to the available/unavailable samples tables.
	// short and sweet, so we'll leave it.  saves us from looking up the tables, which SHOULD be findable, 
	// but could in theory not be if the parent VBox is not in the result panel (ie, hidden).
	public void setData(PickListResult data) {
		availableSamples.setItems(FXCollections.observableList(data.getAvailable()));
		unavailableSamples.setItems(FXCollections.observableList(data.getUnavailable()));
		
		// print button is only enabled if there is available sample data
		printBtn.setDisable(data.getAvailable().size() < 1);
		displayBtn.setDisable(data.getAvailable().size() < 1);
	}
}
