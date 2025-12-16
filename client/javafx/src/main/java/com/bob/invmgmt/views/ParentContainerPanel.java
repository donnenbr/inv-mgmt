package com.bob.invmgmt.views;

import javafx.scene.Node;
import javafx.scene.control.Label;
import javafx.scene.control.TableColumn;
import javafx.scene.control.TableView;
import javafx.scene.control.TableCell;
import javafx.scene.control.SelectionMode;
import javafx.scene.control.cell.PropertyValueFactory;

import com.bob.invmgmt.Constants;
import com.bob.invmgmt.controllers.SearchController;
import com.bob.invmgmt.controls.*;
import com.bob.invmgmt.models.Container;

public class ParentContainerPanel extends RdVBox {
	
	private Label position;
	private TableView<Container> childContainerTbl;
	private SearchController panelController;

	public ParentContainerPanel() {
		super();
		try {
			initialize();
		}
		catch (Exception ex) {
			System.out.println("*** initialization error " + ex);
		}
	}
	
	private void initialize() throws Exception {
		
		panelController = new SearchController(this);
		position = new Label();
		position.setId(Constants.SEARCH_PARENT_POSITION);
		RdFieldGrid fieldGrid = new RdFieldGrid();
		fieldGrid.addOneRow(new Node [] {new Label("Position:"), position});
		Label infoLbl = new Label("Click a row to select that container");
		infoLbl.getStyleClass().add("important-message");
		this.getChildren().add(fieldGrid);
		this.getChildren().add(infoLbl);
		
		childContainerTbl = new TableView<>();
		childContainerTbl.setId(Constants.SEARCH_CHILD_CONTAINER_TABLE);
		childContainerTbl.setEditable(false);
		// to make it fill the rest of the vbox.  should be enough.
		childContainerTbl.setPrefHeight(10000);
		TableColumn<Container,String> barcodeCol = new TableColumn<>("Barcode"),
				containerTypeCol = new TableColumn<>("Container Type"),
				positionCol = new TableColumn<>("Position"),
				reagentCol = new TableColumn<>("Reagent");
		// for any column, use setSortable(false); to disable sorting
		barcodeCol.setCellValueFactory(
			    new PropertyValueFactory<Container,String>("barcode")
				);
		barcodeCol.setCellFactory((tableColumn) -> {
		    TableCell<Container, String> tableCell = new TableCell<Container,String>() {
		        @Override
		        protected void updateItem(String item, boolean empty) {
		            super.updateItem(item, empty);

		            // this.setText(null);
		            // this.setGraphic(null);
		            if(empty || item == null || item.trim().length() < 1){
		            	this.setText("EMPTY");
		            }
		            else {
		                this.setText(item);
		            }
		        }
		    };

		    return tableCell;
		});
		containerTypeCol.setCellValueFactory(
			    new PropertyValueFactory<Container,String>("container_type")
				);
		positionCol.setCellValueFactory(
			    new PropertyValueFactory<Container,String>("position")
				);
		reagentCol.setCellValueFactory(
			    new PropertyValueFactory<Container,String>("reagent")
				);
		childContainerTbl.getColumns().addAll(barcodeCol, containerTypeCol, positionCol, reagentCol);
		// make all columns fit their contents
		childContainerTbl.setColumnResizePolicy( TableView.CONSTRAINED_RESIZE_POLICY_ALL_COLUMNS);
		
		// childContainerTbl.setItems(data);
		
		// force single item selection even tho this seems to be the default
		childContainerTbl.getSelectionModel().setSelectionMode(SelectionMode.SINGLE);
		
		// event to capture when a container was clicked so we can descend the hierarchy
		
		/* the best solution.  we just capture the mouse release, get the selected item and file the custom event.
		 * NO errors logged to stdout/stderr!! 
		 */
		childContainerTbl.setOnMouseReleased(event -> {
			panelController.handleContainerSelect(childContainerTbl.getSelectionModel().getSelectedItem());
		});
		
		// the rest are other attempts here for documentation and posterity!!
		// add selection listener
		/*
		// this works, although clearing the data causes an exception in either the data observable list of selected items list
		ObservableList<Container> selectedItems = childContainerTbl.getSelectionModel().getSelectedItems();
		// so we can access the current panel, file the event against it, and have it bubble up to a handler
		// could also use any control in the panel
		ParentContainerPanel panel = this;
		selectedItems.addListener(new ListChangeListener<Container>() {
			@Override
			public void onChanged(Change<? extends Container> change) {
				try {
					System.out.println("*** selected " + change.getList().size());
					if (change.getList().size() > 0) {
						Container cntr = change.getList().get(0);
						System.out.println("*** barcode " + cntr.getBarcode());
						if (cntr.getBarcode() != null && cntr.getBarcode().trim().length() > 0) {
							ContainerSelectedEvent e = new ContainerSelectedEvent(cntr.getBarcode());
							ContainerSelectedEvent.fireEvent(panel, e);
						}
					}
				}
				catch (Throwable t) {
					System.out.println("*** error " + t);
				}
			}
		});
		*/
		
		// changing the contents of data will cause this to fire again when the container at data[x] chages when the
		// data is replaced.  you skip from shelf to vial
		/*
		childContainerTbl.getSelectionModel().selectedItemProperty().addListener(
				(e, oldVal, newVal) -> {
					System.out.println("*** sel " + e + "\n*** old " + oldVal + "\n*** new " + newVal);
					Container cntr = e.getValue();
					if (cntr.getBarcode() != null && cntr.getBarcode().trim().length() > 0) {
						childContainerTbl.getSelectionModel().clearSelection();
						ContainerSelectedEvent cse = new ContainerSelectedEvent(cntr.getBarcode());
						ContainerSelectedEvent.fireEvent(this, cse);
					}
				}
		);
		*/
		
		/*
		// this will not fire if you select the same table row after new data was loaded. 
		childContainerTbl.getSelectionModel().selectedIndexProperty().addListener(
				(e, oldVal, newVal) -> {
					System.out.println("*** sel " + e + "\n*** old " + oldVal + "\n*** new " + newVal);
					if (newVal.intValue() >= 0) {
						Container cntr = childContainerTbl.getItems().get(newVal.intValue());
						System.out.println("*** cntr " + cntr);
						if (cntr.getBarcode() != null && cntr.getBarcode().trim().length() > 0) {
							childContainerTbl.getSelectionModel().clearSelection();
							ContainerSelectedEvent cse = new ContainerSelectedEvent(cntr.getBarcode());
							ContainerSelectedEvent.fireEvent(this, cse);
						}
					}
				}
		);
		*/
		
		this.getChildren().add(childContainerTbl);
	}
}
