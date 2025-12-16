package com.bob.invmgmt.controllers;

import java.awt.Color;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Callable;

import javax.print.Doc;
import javax.print.DocFlavor;
import javax.print.DocPrintJob;
import javax.print.PrintService;
import javax.print.PrintServiceLookup;
import javax.print.SimpleDoc;

import org.openpdf.text.Cell;
import org.openpdf.text.Document;
import org.openpdf.text.Element;
import org.openpdf.text.Font;
import org.openpdf.text.HeaderFooter;
import org.openpdf.text.PageSize;
import org.openpdf.text.Phrase;
import org.openpdf.text.Rectangle;
import org.openpdf.text.Table;
import org.openpdf.text.alignment.HorizontalAlignment;
import org.openpdf.text.alignment.VerticalAlignment;
import org.openpdf.text.pdf.BaseFont;
import org.openpdf.text.pdf.PdfWriter;

import com.bob.invmgmt.Constants;
import com.bob.invmgmt.Dao;
import com.bob.invmgmt.controls.BlockingNotification;
import com.bob.invmgmt.controls.RdBaseTextField;
import com.bob.invmgmt.controls.RdVBox;
import com.bob.invmgmt.events.GeneratePickListEvent;
import com.bob.invmgmt.events.PickListSearchEvent;
import com.bob.invmgmt.exceptions.ApplicationException;
import com.bob.invmgmt.models.PickListItem;
import com.bob.invmgmt.models.PickListResult;
import com.bob.invmgmt.models.PickListResultItem;
import com.bob.invmgmt.utils.Utils;
import com.bob.invmgmt.views.PickListPanel;
import com.bob.invmgmt.views.PickListResultPanel;

import javafx.scene.control.ChoiceBox;
import javafx.scene.control.TableView;
import javafx.scene.control.TextArea;
import javafx.scene.layout.StackPane;

public class PickListController {
	private PickListPanel panel;
	
	public PickListController(PickListPanel panel) {
		this.panel = panel;
	}
	
	public void handleGeneratePickListEvent(PickListPanel panel, List<PickListItem> requestData) {
		try {
			// post the request and disable EVERYTHING until the call completes
        	GeneratePickListCallable c = new GeneratePickListCallable(requestData);
			BlockingNotification<PickListResult> d = new BlockingNotification<>("Info!", "Processing - Please Wait ...", c);
			d.showAndWait();
			// now switch to the result pane and display the pick list data
			StackPane sp = (StackPane)Utils.lookupById(panel, Constants.PICKLIST_STACK_PANE);
			PickListResultPanel resultPnl = (PickListResultPanel)Utils.lookupById(panel, Constants.PICKLIST_RESULT_PANEL);
        	resultPnl.setData(d.getResult());
        	Utils.displaySpackPaneChild(sp, resultPnl);
        } 
        catch (ApplicationException aex) {
        	Utils.displayErrorDialog("Generate Pick List failed!!", aex.getMessages());
        } 
		catch (Exception ex) {
			Utils.displayErrorDialog("Generate Pick List failed!!", ex.getMessage());
        }
		
	}
	
	// does what it says - clear (blank) out all values in the request table
	public void clearSearchTable(List<PickListItem> data) {
		TableView<PickListItem> searchTbl = (TableView<PickListItem>)Utils.lookupById(panel,Constants.PICKLIST_SEARCH_TABLE);
		data.forEach(item -> {
			item.setReagent(null);
			item.setAmount(null);
			item.setConcentration(null);
		});
		searchTbl.getSelectionModel().clearSelection();
		searchTbl.refresh();
	}
	
	// validate the values in the request table and create the requests data list
	public void generatePickList(List<PickListItem> tableData) {
		List<String> errors = new ArrayList<>();
		tableData.forEach(item -> {
			if (item.getReagent() != null) {
				item.setReagent(item.getReagent().trim());
			}
			
			// if any field on a line is set, they ALL must be set.  reagent can be null or blank.
			if ((item.getReagent() != null && item.getReagent().length() > 0) || item.getAmount() != null || item.getConcentration() != null) {
				// one of the values is set -> they must ALL be set
				if (item.getReagent() == null || item.getReagent().length() < 1) {
					errors.add("Line " + item.getLineNum() + " : reagent must be specified");
				}
				if (item.getAmount() == null) {
					errors.add("Line " + item.getLineNum() + " : amount must be specified");
				}
				// only limit on the amount and conc is that they are > 0.  the backend will validate the
				// actual value.
				else if (item.getAmount().intValue() < 1) {
					errors.add("Line " + item.getLineNum() + " : amount must be > 0");
				}
				if (item.getConcentration() == null) {
					errors.add("Line " + item.getLineNum() + " : concentration must be specified");
				}
				else if (item.getConcentration().doubleValue() < 1) {
					errors.add("Line " + item.getLineNum() + " : concentration must be > 0");
				}
			}
		});
		if (errors.isEmpty()) {
			// no errors --> create the requests list
			List<PickListItem> requestData = new ArrayList<>(tableData.size());
			tableData.forEach(item -> {
				// if one field is set, they all are
				if (item.getAmount() != null) {
					requestData.add(item);
				}
			});
			if (requestData.size() < 1) {
				Utils.displayErrorDialog("Validation failed!", "You must enter at least one item.");
			}
			else {
				// all OK, fire the event to push the request to the backend
				GeneratePickListEvent event = new GeneratePickListEvent(requestData);
				GeneratePickListEvent.fireEvent(panel, event);
			}
		}
		else {
			Utils.displayErrorDialog("Validation failed!", errors);
		}
	}
	
	// set the reagent fields based on the values in the textarea.
	public void bulkSetReagents(List<PickListItem> data) {
		TableView<PickListItem> searchTbl = (TableView<PickListItem>)Utils.lookupById(panel,Constants.PICKLIST_SEARCH_TABLE);
		TextArea reagentTxtArea = (TextArea)Utils.lookupById(panel, Constants.PICKLIST_SEARCH_REAGENT_LIST);
		ChoiceBox<String> loadOptionCbox = (ChoiceBox<String>)Utils.lookupById(panel,Constants.PICKLIST_SEARCH_LOAD_OPTIONS);
		// convert the \n separated list of reagents into an array
		List<String> reagents = new ArrayList<>();
		for (String s : reagentTxtArea.getText().split("\n")) {
			String r = s.trim();
			if (r.length() > 0 && ! reagents.contains(r)) {
				reagents.add(r);
			}
		}
		if (reagents.isEmpty()) {
			Utils.displayErrorDialog(null, "You must enter at least one reagent!");
			return;
		}
		
		boolean loadAll = loadOptionCbox.getValue().equalsIgnoreCase("load all");
		// loadAll == true -> over write the values starting at the top
		// false -> only fill in the empty fields
		for (PickListItem item: data) {
			if (loadAll || item.getReagent() == null || item.getReagent().trim().length() < 1) {
				item.setReagent(reagents.get(0));
				reagents.remove(0);
				if (reagents.isEmpty()) {
					break;
				}
			}
		}
		// see if we need to add anything to the end
		if (!reagents.isEmpty()) {
			int lineNum = data.get(data.size()-1).getLineNum();
			while (!reagents.isEmpty()) {
				PickListItem item = new PickListItem();
				item.setLineNum(++lineNum);
				item.setReagent(reagents.get(0));
				data.add(item);
				reagents.remove(0);
			}
		}
		
		searchTbl.refresh();
	}
	
	// similar for the amount.
	public void bulkSetAmount(List<PickListItem> data) {
		TableView<PickListItem> searchTbl = (TableView<PickListItem>)Utils.lookupById(panel,Constants.PICKLIST_SEARCH_TABLE);
		ChoiceBox<String> loadOptionCbox = (ChoiceBox<String>)Utils.lookupById(panel,Constants.PICKLIST_SEARCH_LOAD_OPTIONS);
		RdBaseTextField amountFld = (RdBaseTextField)Utils.lookupById(panel,Constants.PICKLIST_SEARCH_AMOUNT);
		if (!amountFld.validate()) {
			// for now
			Utils.displayErrorDialog(null, amountFld.getErrors());
			return;
		}
		Integer val = Integer.valueOf(amountFld.getValue());
		boolean loadAll = loadOptionCbox.getValue().equalsIgnoreCase("load all");
		// load amount only when an row has a reagent specified
		// true -> set for any such row
		// false -> set only when row does NOT have an amount
		data.forEach(item -> {
			// only set where a reagent is defined
			if (item.getReagent() != null && item.getReagent().trim().length() > 0) {
				if (loadAll || item.getAmount() == null) {
					item.setAmount(val);
				}
			}
		});
		searchTbl.refresh();
	}
	
	// ditto for concentration
	public void bulkSetConcentration(List<PickListItem> data) {
		TableView<PickListItem> searchTbl = (TableView<PickListItem>)Utils.lookupById(panel,Constants.PICKLIST_SEARCH_TABLE);
		ChoiceBox<String> loadOptionCbox = (ChoiceBox<String>)Utils.lookupById(panel,Constants.PICKLIST_SEARCH_LOAD_OPTIONS);
		RdBaseTextField concentrationFld = (RdBaseTextField)Utils.lookupById(panel,Constants.PICKLIST_SEARCH_CONCENTRATION);
		if (!concentrationFld.validate()) {
			// for now
			Utils.displayErrorDialog(null, concentrationFld.getErrors());
			return;
		}
		Double val = Double.valueOf(concentrationFld.getValue());
		boolean loadAll = loadOptionCbox.getValue().equalsIgnoreCase("load all");
		// load concentration only when an row has a reagent specified
		// true -> set for any such row
		// false -> set only when row does NOT have a concentration
		data.forEach(item -> {
			// only set where a reagent is defined
			if (item.getReagent() != null && item.getReagent().trim().length() > 0) {
				if (loadAll || item.getConcentration() == null) {
					item.setConcentration(val);
				}
			}
		});
		searchTbl.refresh();
	}
	
	// a word of explanation as to why we have what we have here.
	// we cannot use the panel defined for this class because we need to explicitly access the result panel.
	// we cannot lookup the available section by id because it is removed from the panel to hide it, so 
	// lookup will return NULL.
	public void showHideAvailableSamples(boolean showIt, PickListResultPanel resultPanel, RdVBox availableSection) {
		if (showIt) {
    		if (!resultPanel.getChildren().contains(availableSection)) {
    			resultPanel.getChildren().add(0, availableSection);
    		}
    	}
    	else {
    		if (resultPanel.getChildren().contains(availableSection)) {
    			resultPanel.getChildren().remove(availableSection);
    		}
    	}
	}
	
	// similar to above
	public void showHideUnavailableSamples(boolean showIt, PickListResultPanel resultPanel, RdVBox unavailableSection) {
		if (showIt) {
    		if (!resultPanel.getChildren().contains(unavailableSection)) {
    			// if available section is shown, the unavailable section goes beneath it at index 1
    			// since we assume the available section is at index 0, otherwise it goes to the top
    			// as index 0
    			RdVBox availableSection = (RdVBox)Utils.lookupById(resultPanel,Constants.PICKLIST_RESULT_AVAILABLE_SAMPLES);
    			int idx = resultPanel.getChildren().contains(availableSection) ? 1 : 0;
    			resultPanel.getChildren().add(idx, unavailableSection);
    		}
    	}
    	else {
    		if (resultPanel.getChildren().contains(unavailableSection)) {
    			resultPanel.getChildren().remove(unavailableSection);
    		}
    	}
	}
	
	// flip back to the search panel.
	public void returnToSearch() {
		PickListSearchEvent event = new PickListSearchEvent();
		PickListSearchEvent.fireEvent(panel, event);
	}
	
	// create a pdf report of the pick list.  private because it will be called by another function which
	// will handle (display, print) the report.
	// NOTE - we're using openpdf because it has really nice support for tables.  pdfbox was pretty
	// abysmal in that sense.  also, one cannot create a pdf document "object", then have some writer
	// object write it out.  you must link the document to a writer from the get-go, so we supply
	// the output stream the writer will use when creating the document.
	private void makePickListReport(List<PickListResultItem> data, OutputStream outF) throws Exception {
		Document document = new Document(PageSize.LETTER, 10, 10, 30, 30);
		try
        {
            // create the writer.  we must do this BEFORE adding anything to the document
            PdfWriter writer = PdfWriter.getInstance(document, outF);

            // was Cp1252
            BaseFont bf_times = BaseFont.createFont(BaseFont.TIMES_ROMAN, "utf8", false);

            // add a page number footer, no header
            HeaderFooter footer = new HeaderFooter(new Phrase("Page ", new Font(bf_times)), true);
            footer.setBorder(Rectangle.NO_BORDER);
            footer.setAlignment(Element.ALIGN_RIGHT);
            document.setFooter(footer);

            // NOW we start filling in the document
            document.open();
            
            Font font = new Font(bf_times, 10);
            Table table = new Table(6);
            table.setBorderWidth(1);
            table.setBorderColor(Color.GRAY);
            
            // create the column headers.  sizes determined by using legit "max size" mock values for the data,
            // then tweaking the widths.  note how we can use \n to make multi-line column headings!!!
            String colHeaders[] = new String[] {
            		"Reagent", "Requested\nAmt (ul)", "Barcode", "Location", "Container\nAmt (ul)", "Conc (ul)"}; 
            table.setWidths(new float [] { 2f, 1f, 1.5f, 2.5f, 1f, 1f});
            for (String s : colHeaders) { 
            	Cell c = new Cell(new Phrase(s,font));
            	c.setBackgroundColor(Color.LIGHT_GRAY);
            	c.setRowspan(2);
            	c.setHorizontalAlignment(HorizontalAlignment.CENTER);
            	c.setVerticalAlignment(VerticalAlignment.CENTER);
            	c.setHeader(true);
            	table.addCell(c);
            }
            table.endHeaders();
            
            // now just fill in the data.  the pfd will repeat the columns headings when a new page is needed.
            for (PickListResultItem item : data) {
            	Cell c = new Cell(new Phrase(item.getReagent(),font));
            	c.setHorizontalAlignment(HorizontalAlignment.CENTER);
            	c.setVerticalAlignment(VerticalAlignment.CENTER);
            	table.addCell(c);
            	
            	c = new Cell(new Phrase(String.format("%.0f",item.getRequested_amount()),font));
            	c.setHorizontalAlignment(HorizontalAlignment.CENTER);
            	c.setVerticalAlignment(VerticalAlignment.CENTER);
            	table.addCell(c);
            	
            	c = new Cell(new Phrase(item.getBarcode(),font));
            	c.setHorizontalAlignment(HorizontalAlignment.CENTER);
            	c.setVerticalAlignment(VerticalAlignment.CENTER);
            	table.addCell(c);
           
            	c = new Cell(new Phrase(item.getPosition(),font));
            	c.setHorizontalAlignment(HorizontalAlignment.CENTER);
            	c.setVerticalAlignment(VerticalAlignment.CENTER);
            	table.addCell(c);
            	
            	c = new Cell(new Phrase(String.format("%.0f",item.getAmount()),font));
            	c.setHorizontalAlignment(HorizontalAlignment.CENTER);
            	c.setVerticalAlignment(VerticalAlignment.CENTER);
            	table.addCell(c);
            	
            	c = new Cell(new Phrase(String.format("%.2f",item.getConcentration()),font));
            	c.setHorizontalAlignment(HorizontalAlignment.CENTER);
            	c.setVerticalAlignment(VerticalAlignment.CENTER);
            	table.addCell(c);
            }
            
            document.add(table);

            // done.  just close/flush everything.
            document.close();
            
            writer.flush();
            writer.close();
            outF.flush();
            outF.close();
        } catch (Exception ex) {
            throw ex;
        }
	}
	
	// create and print the pick list report.  there is no print dialog, it just prints to the default
	// printer.
	public void printReport(List<PickListResultItem> data) {
		try {
			DocFlavor flavor = DocFlavor.INPUT_STREAM.PDF;
			// get the default printer if defined
			PrintService service = PrintServiceLookup.lookupDefaultPrintService();
			System.out.println("*** default svc " + service);
			if (service == null) {
				// not defined, so pick up the first one
				PrintService[] printServices = PrintServiceLookup.lookupPrintServices(flavor, null);
				if (printServices.length < 1) {
					// nothing defined - error
					Utils.displayErrorDialog("Error!!", "There are no printers to send the report to.");;
				}
			}
			else {
				// create the report
				ByteArrayOutputStream outF = new ByteArrayOutputStream();
				makePickListReport(data, outF);
				// convert the output stream to an input stream (what we need to print)
	            InputStream inF = new ByteArrayInputStream(outF.toByteArray());
				DocPrintJob printJob = service.createPrintJob();
				Doc doc = new SimpleDoc(inF, DocFlavor.INPUT_STREAM.AUTOSENSE, null);
				printJob.print(doc, null);
			}
		}
		catch (Exception ex) {
			Utils.displayErrorDialog("Print pick list failed", ex.getMessage());
		}
	}
	
	// create the pdf pick list report and display it using the default app for that.
	public void displayReport(List<PickListResultItem> data) {
		try {
			File pdfReport = File.createTempFile("pick-list-", ".pdf");
			FileOutputStream outF = new FileOutputStream(pdfReport);
			makePickListReport(data, outF);
			outF.flush();
			outF.close();
	        Utils.getApp().getHostServices().showDocument(pdfReport.toURI().toString());
		}
		catch (Exception ex) {
			Utils.displayErrorDialog("Display pick list failed", ex.getMessage());
		}
	}
}

// a callable to fetch the pick list data from the backend.  this lets us run it as an async job
// which is required to disable the UI at the same time.
class GeneratePickListCallable implements Callable<PickListResult> {
	private List<PickListItem> requestData;
	public GeneratePickListCallable(List<PickListItem> requestData) {
		super();
		this.requestData = requestData;
	}
	public PickListResult call() throws Exception {
		Dao dao = new Dao();
		return dao.generatePickList(requestData);
	}
}

