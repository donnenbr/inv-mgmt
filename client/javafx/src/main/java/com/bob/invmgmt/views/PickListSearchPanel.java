/*
 * panel for the search portion of the pick list function.  it contains the main editable table for entering
 * the requests data (reagent, amount, concentration).  it also has options on the bottom for bulk setting
 * values to fill the table, a God send for testing as manual entry is a real pain.
 */

package com.bob.invmgmt.views;

import java.util.ArrayList;
import java.util.List;

import com.bob.invmgmt.Constants;
import com.bob.invmgmt.controllers.PickListController;
import com.bob.invmgmt.controls.RdDoubleField;
import com.bob.invmgmt.controls.RdIntegerField;
import com.bob.invmgmt.controls.RdTableCell;
import com.bob.invmgmt.controls.RdVBox;
import com.bob.invmgmt.models.PickListItem;
import com.bob.invmgmt.utils.Utils;

import javafx.application.Platform;
import javafx.collections.FXCollections;
import javafx.geometry.Orientation;
import javafx.geometry.Pos;
import javafx.scene.Node;
import javafx.scene.control.Button;
import javafx.scene.control.ChoiceBox;
import javafx.scene.control.Label;
import javafx.scene.control.Separator;
import javafx.scene.control.TableColumn;
import javafx.scene.control.TableView;
import javafx.scene.control.TextArea;
import javafx.scene.control.Tooltip;
import javafx.scene.control.cell.PropertyValueFactory;
import javafx.scene.layout.HBox;
import javafx.scene.layout.VBox;
import javafx.util.converter.DoubleStringConverter;
import javafx.util.converter.IntegerStringConverter;

public class PickListSearchPanel extends RdVBox {
	
	private final int NUM_ENTRIES = 10;

	private List<PickListItem> data;
	private TableView<PickListItem> searchTbl;
	private TextArea reagentTxtArea;
	private RdIntegerField amountFld;
	private RdDoubleField concentrationFld;
	private ChoiceBox<String> loadOptionCbox;
	private PickListController panelController;
	
	// note that both the search and result panels use the same controller, so it is passed in from
	// the parent panel.
	public PickListSearchPanel(PickListController panelController) {
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
		searchTbl = new TableView<>();
		searchTbl.setId(Constants.PICKLIST_SEARCH_TABLE);
		searchTbl.setEditable(true);
		searchTbl.setPrefHeight(280);
		searchTbl.setFocusTraversable(true);
		TableColumn<PickListItem, Integer> lineNumCol = new TableColumn<>("Line #");
		TableColumn<PickListItem, String> reagentCol = new TableColumn<>("Reagent");
		TableColumn<PickListItem, Integer> amountCol = new TableColumn<>("Amount");
		TableColumn<PickListItem, Double> concentrationCol = new TableColumn<>("Concentration");

		lineNumCol.setCellValueFactory(new PropertyValueFactory<PickListItem, Integer>("lineNum"));

		// setup the editable columns.  for each, we consume the event so it does not propagate.
		// we also set the corresponding value in the underlying data.
		// lastly we move on to the next column, which is hard coded so we move from
		// reagent -> amount -> concentration.  moving from concentration moves to the reagent
		// cell on the next line.  FYI, the columns CANNOT be moved around because of this.
		// the key used for navigation cannot be passed to the event handlers, so doing things
		// like navigating the the previous column via back-tab cannot be done.
		// too bad, that's the way it is.
		reagentCol.setCellValueFactory(new PropertyValueFactory<PickListItem, String>("reagent"));
		reagentCol.setCellFactory(column -> {
			return new RdTableCell<PickListItem,String>();
		});
		reagentCol.addEventHandler(TableColumn.editCommitEvent(), e -> {
			TableColumn.CellEditEvent<PickListItem, String> t = (TableColumn.CellEditEvent)e;
			t.consume();
			int row = t.getTablePosition().getRow();
			PickListItem item = t.getTableView().getItems().get(row);
			item.setReagent((String)t.getNewValue());
			
			editCell(amountCol, row);
		});

		amountCol.setCellValueFactory(new PropertyValueFactory<PickListItem, Integer>("amount"));
		amountCol.setCellFactory(column -> {
			return new RdTableCell<PickListItem,Integer>(new IntegerStringConverter());
		});
		amountCol.addEventHandler(TableColumn.editCommitEvent(), e -> {
			TableColumn.CellEditEvent<PickListItem, Integer> t = (TableColumn.CellEditEvent)e;
			t.consume();
			int row = t.getTablePosition().getRow();
			PickListItem item = t.getTableView().getItems().get(row);
			item.setAmount(t.getNewValue());
			editCell(concentrationCol, row);
		});
		concentrationCol.setCellValueFactory(new PropertyValueFactory<PickListItem, Double>("concentration"));
		concentrationCol.setCellFactory(column -> {
			return new RdTableCell<PickListItem,Double>(new DoubleStringConverter());
		});
		concentrationCol.addEventHandler(TableColumn.editCommitEvent(), e -> {
			TableColumn.CellEditEvent<PickListItem, Double> t = (TableColumn.CellEditEvent)e;
			t.consume();
			int row = t.getTablePosition().getRow();
			PickListItem item = t.getTableView().getItems().get(row);
			item.setConcentration(t.getNewValue());
			++row;
			if (row < t.getTableView().getItems().size()) {
				editCell(reagentCol, row);
			}
		});
		
		// make all columns fit their contents
		searchTbl.setColumnResizePolicy(TableView.CONSTRAINED_RESIZE_POLICY_ALL_COLUMNS);
		searchTbl.getColumns().addAll(lineNumCol, reagentCol, amountCol, concentrationCol);
		searchTbl.getColumns().forEach(col -> {
			// columns are NOT sortable as that would not make sense.  they are, naturally, editable.
			col.setSortable(false);
			col.setEditable(true);
			// facist dr. bob does NOT allow columns to be reordered due to the "edit next cell" logic
			col.setReorderable(false);
		});
		// the line number column is simply informative and used as a reference when the backend rejects
		// your entries.
		lineNumCol.setEditable(false);
		
		// create the underlying data items and link them to the table.
		data = new ArrayList<>(NUM_ENTRIES);
		for (int i = 0; i < NUM_ENTRIES; ++i) {
			data.add(new PickListItem(i + 1, null, null, null));
		}
		searchTbl.setItems(FXCollections.observableList(data));
		// allow cell level selection, which will block row level selection.
		searchTbl.getSelectionModel().setCellSelectionEnabled(true);

		// action buttons!!!
		HBox hb = new HBox();
		hb.setSpacing(30);
		hb.setAlignment(Pos.CENTER);
		Button generateBtn = new Button("Generate Pick List");
		generateBtn.getStyleClass().add("small-button");
		generateBtn.setOnAction(e -> {
			panelController.generatePickList(data);
		});
		Button clearBtn = new Button("Clear");
		clearBtn.getStyleClass().add("small-button");
		clearBtn.setOnAction( e -> {
			panelController.clearSearchTable(data);
		});
		hb.getChildren().addAll(clearBtn, generateBtn);
		this.getChildren().addAll(searchTbl, hb);
		
		// bulk set options on the bottom to make testing easier.  anyway, in the "real world", someone
		// might very well have a list of reagents to request, so it's a real use case.
		Separator sep = new Separator();
        sep.setOrientation(Orientation.HORIZONTAL);
        this.getChildren().add(sep);
		
        Label titleLbl = new Label("Bulk Set Options");
		titleLbl.getStyleClass().add("title");
		
		this.getChildren().addAll(titleLbl, makeOptionsPane());
		
		hb = new HBox();
		hb.setSpacing(10);
		hb.setAlignment(Pos.CENTER);
		hb.getChildren().add(new Label("How to do the bulk load:"));
		loadOptionCbox = new ChoiceBox<>();
		loadOptionCbox.setId(Constants.PICKLIST_SEARCH_LOAD_OPTIONS);
		loadOptionCbox.getItems().addAll("Load all", "Load empty");
		loadOptionCbox.getSelectionModel().select("Load empty");
		loadOptionCbox.setTooltip(new Tooltip("Load all will overwrite current values.\nLoad empty will fill only empty cells."));
		hb.getChildren().add(loadOptionCbox);
		this.getChildren().add(hb);
	}
	
	// the only way to edit a cell.  we must use runLater so the action is not on the main thread.
	private void editCell(TableColumn col, int row) {
		Thread t = new Thread() {
			public void run() {
				searchTbl.getSelectionModel().clearAndSelect(row, col);
				searchTbl.edit(row, col);
			}
		};
		Platform.runLater(t);
	}
	
	// create the options area, pulled outside the main initialization function for simplicity.
	private Node makeOptionsPane() throws Exception {	
		HBox optionsPane = new HBox();
		optionsPane.setSpacing(15);
		optionsPane.setAlignment(Pos.CENTER);
		
		VBox loadReagents = new VBox();
		loadReagents.setAlignment(Pos.CENTER);
		loadReagents.setSpacing(10);
		reagentTxtArea = new TextArea();
		reagentTxtArea.setId(Constants.PICKLIST_SEARCH_REAGENT_LIST);
		reagentTxtArea.setPrefWidth(250);
		Button loadReagentsBtn = new Button("Load Reagents");
		loadReagentsBtn.getStyleClass().add("small-button");
		loadReagentsBtn.setOnAction(e -> {
			panelController.bulkSetReagents(data); 
		});
		loadReagents.getChildren().addAll(new Label("Reagent List"), reagentTxtArea, loadReagentsBtn);
		
		VBox setAmount = new VBox();
		setAmount.setAlignment(Pos.CENTER);
		setAmount.setSpacing(10);
		amountFld = (RdIntegerField)Utils.createField("int", "amount", null, true, 1, 750);
		amountFld.setId(Constants.PICKLIST_SEARCH_AMOUNT);
		Button setAmountBtn = new Button("Set Amount");
		setAmountBtn.getStyleClass().add("small-button");
		setAmountBtn.setOnAction(e -> {
			panelController.bulkSetAmount(data);
		});
		setAmount.getChildren().addAll(new Label("Amount (ul)"), amountFld, setAmountBtn);
		
		VBox setConcentration = new VBox();
		setConcentration.setAlignment(Pos.CENTER);
		setConcentration.setSpacing(10);
		concentrationFld = (RdDoubleField)Utils.createField("double", "concentration", null, true, 1, 10);
		concentrationFld.setId(Constants.PICKLIST_SEARCH_CONCENTRATION);
		Button setConcentrationBtn = new Button("Set Concentration");
		setConcentrationBtn.getStyleClass().add("small-button");
		setConcentrationBtn.setOnAction(e -> {
			panelController.bulkSetConcentration(data);
		});
		setConcentration.getChildren().addAll(new Label("Concentration (uM)"), concentrationFld, setConcentrationBtn);
		
		optionsPane.getChildren().addAll(loadReagents, setAmount, setConcentration);
		
		return optionsPane;
	}
}
