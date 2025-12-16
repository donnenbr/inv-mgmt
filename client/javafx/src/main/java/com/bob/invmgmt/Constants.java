/*
 * constant values used throughout the application
 */
package com.bob.invmgmt;

public class Constants {
	// our lovely css file
	public static String CSS_FILE = "InvMgmt.css";
	
	// constants used to define the ids of UI elements.  the prefix ("add-", "locate-", etc.) are used
	// to make them unique.  ideally they only have to be unique within a panel and its children,
	// not the whole app and we typically DO perform the lookups from a panel or one of its parents.
	
	// NOTE - the id syntax is a little strict, with "-" the best word separator.  with that in mind we
	// probably could have used UUIDS for these!!!
	
	public static String ADD_BARCODE = "add-barcode";
	public static String ADD_LOT_NAME = "add-lot-name";
	public static String ADD_AMOUNT = "add-amount";
	public static String ADD_CONCENTRATION = "add-concentration";
	public static String ADD_SAVE_BUTTON = "add-save-button";
	public static String ADD_ERROR_MESSAGE = "add-error-message";
	
	public static String LOCATE_VIAL_BARCODE = "locate-vial-barcode";
	public static String LOCATE_RACK_BARCODE = "locate-rack-barcode";
	public static String LOCATE_POSITION = "locate-position";
	public static String LOCATE_SAVE_BUTTON = "locate-save-button";
	public static String LOCATE_ERROR_MESSAGE = "locate-error-message";
	
	public static String SEARCH_BARCODE = "search-barcode";
	public static String SEARCH_CONTAINER_TYPE = "search-container-type";
	public static String SEARCH_PARENT_POSITION = "search-parent-position";
	public static String SEARCH_ERROR_LABEL = "search-error-label";
	public static String SEARCH_DETAIL_PANE = "search-detail-pane";
	public static String SEARCH_SAMPLE_CONTAINER_PANEL = "search-sample-container-panel";
	public static String SEARCH_PARENT_CONTAINER_PANEL = "search-parent-container-panel";
	public static String SEARCH_CHILD_CONTAINER_TABLE = "search-child-containers";
	public static String SEARCH_SAMPLE_CONTAINER_POSITION = "search-sample-container-position";
	public static String SEARCH_SAMPLE_CONTAINER_REAGENT = "search-sample-container-reagent";
	public static String SEARCH_SAMPLE_CONTAINER_LOT = "search-sample-container-lot";
	public static String SEARCH_SAMPLE_CONTAINER_AMOUNT = "search-sample-container-amount";
	public static String SEARCH_SAMPLE_CONTAINER_CONCENTRATION = "search-sample-container-concentration";
	public static String SEARCH_SAMPLE_CONTAINER_ERROR_LABEL = "search-sample-container-error-label";
	
	// main pick list panel
	public static String PICKLIST_STACK_PANE = "picklist-stack-pane";
	public static String PICKLIST_SEARCH_PANEL = "picklist-search-panel";
	public static String PICKLIST_RESULT_PANEL = "picklist-result-panel";
	// the search panel
	public static String PICKLIST_SEARCH_TABLE = "picklist-search-table";
	public static String PICKLIST_SEARCH_REAGENT_LIST = "picklist-search-reagent-list";
	public static String PICKLIST_SEARCH_AMOUNT = "picklist-search-amount";
	public static String PICKLIST_SEARCH_CONCENTRATION = "picklist-search-concentration";
	public static String PICKLIST_SEARCH_LOAD_OPTIONS = "picklist-search-load_options";
	// the result panel
	public static String PICKLIST_RESULT_AVAILABLE_SAMPLES = "picklist-result-available-samples";
	public static String PICKLIST_RESULT_UNAVAILABLE_SAMPLES = "picklist-result-unavailable-samples";
}
