<script setup>

import { ref, watch } from 'vue'

import { MIN_BARCODE_LENGTH, MIN_AMOUNT, MAX_AMOUNT, MIN_CONCENTRATION, MAX_CONCENTRATION,
            AMOUNT_UNIT, CONCENTRATION_UNIT } from '../../constants.js';

import { getContainerByBarcode, updateVial, deleteVial } from '@/httpService.js';
import { displayAlertDialog, displayConfirmationDialog } from '@/utils.js';
import Alert from '@/components/dialogs/Alert.vue';
import Confirm from '@/components/dialogs/Confirm.vue';

const props = defineProps(['selectedBarcode','selectedContainer'])

const dialogInfo = ref({ title: "", messages: []});

const alertDialog = ref(),
      confirmDialog = ref();

// this MUST be a ref for the changes pulled from the db to ne displayed on the form.
const formData = ref({
    id: null,
    search_barcode: null,
    barcode: null,
    container_type: null,
    location: null,
    reagent: null,
    lot: null,
    amount: null,
    amount_unit: AMOUNT_UNIT,
    concentration: null,
    concentration_unit: CONCENTRATION_UNIT
});

const amountField = 'search-amount',
    concentrationField = 'search-concentration';

const disabledFlag = ref(true);

// used to catch changes to the show ref
watch(props.selectedBarcode, (newValue, prevValue) => {
    let barcode = newValue?.barcode;
    if (barcode) {
        searchBarcode(barcode);
    }
});

function copyContainerData(containerData) {
    let formValues = formData.value;
    formValues.id = containerData.id;
    formValues.search_barcode = containerData.barcode;
    formValues.barcode = containerData.barcode;
    formValues.container_type = containerData.container_type;
    formValues.location = containerData.position;
    formValues.reagent = containerData.reagent
    formValues.lot = containerData.lot;
    formValues.amount = containerData.amount;
    formValues.concentration = containerData.concentration;
    disabledFlag.value = (containerData.lot == null);
}


// although rather obsessive, we do NOT want to validate the amount and concentration fields when
// doing a search.  they'd only be validated when visible.  that "noformvalidate" or "formnovalidate"
// shit does not seem to work, so we disable the fields during the search and reenable them when the
// search is done.  we also use the form's reportValidity() function to do the validation as it 
// also will flag the fields on the page!!!
function doSearch(event) {
    // event.preventDefault();
    let frm = document.getElementById('searchPanelForm');
    try {
        disableFieldValidation(frm, true);
        let valid = frm.reportValidity();
        if (valid) {
            searchBarcode(formData.value.search_barcode);
        }
    }
    catch (exc) {
        displayAlertDialog(alertDialog, dialogInfo, "Search Failed", exc);
    }finally {
        disableFieldValidation(frm, false);
    }
}

function disableFieldValidation(frm, disabled) {
    try {
        frm[amountField].disabled = disabled;
        frm[concentrationField].disabled = disabled;
    }
    catch (exc) {
        alert(exc);
    }
}

function searchBarcode(barcode) {
    let response = getContainerByBarcode(barcode);
    response.then((result) => {
        if (result.status == 404) {
            displayAlertDialog(alertDialog, dialogInfo, "That barcode is invalid!");
            return;
        }
        try {
            let jsonData = result.data;
            if (jsonData.success) {
                let containerData = jsonData.data;
                // NOTE - if a value comes back as null, the formData value WILL NOT CHANGE!!!
                // dr bobby thinks that is because null is no value so nothing can be equal to, or not
                // equal to, null.  so, we make them blanks.  note we use == to cover the bases of null or undefined.
                copyContainerData(containerData);
                props.selectedContainer.value = containerData;
            }
            else {
                displayAlertDialog(alertDialog, dialogInfo, "Search failed", jsonData.errors); 
            }
        }
        catch (ex) {
            console.log(ex);
            // can't use Promise.reject here (because of the resolutions???  no next step????)
            // throw an exception
            throw("Error code " + result.status + " : " + result.statusText);
        }
    })
    // upon reject, we end here!!!
    .catch((error) => {
        displayAlertDialog(alertDialog, dialogInfo, "An error occurred", error);
    });
}

function barcodeChanged(event) {
    formData.value.search_barcode = event.target.value;
    // and diosable the update/delete buttons until a search is done
    disabledFlag.value = true;
}

function doUpdateContainer() {
    let frm = document.getElementById('searchPanelForm');
    if (!frm.reportValidity()) {
        return;
    }
    let formValues = formData.value;
    let vialData = {
        id: formValues.id,
        container_type: formValues.container_type,
        barcode: formValues.barcode,
        lot: formValues.lot,
        amount: formValues.amount,
        amount_unit: formValues.amount_unit,
        concentration: formValues.concentration,
        concentration_unit: formValues.concentration_unit
    };
    // console.log(vialData);
    let response = updateVial(vialData);
    response.then((result) => {
        try {
            let jsonData = result.data;
            if (jsonData.success) {
                // nothing should change, but ...
                copyContainerData(jsonData.data);
                displayAlertDialog(alertDialog, dialogInfo, "Update successful!!!");
            }
            else {
                displayAlertDialog(alertDialog, dialogInfo, "Update vial failed", jsonData.errors); 
            }
        }
        catch (ex) {
            console.log(ex);
            // can't use Promise.reject here (because of the resolutions???  no next step????)
            // throw an exception
            throw("Error code " + result.status + " : " + result.statusText);
        }
    })
    // upon reject, we end here!!!
    .catch((error) => {
        displayAlertDialog(alertDialog, dialogInfo, "An error occurred", error);
    });
}

function _deleteContainer() {
    let response = deleteVial(formData.value.id);
    response.then((result) => {
        let jsonData = result.data;
        if (jsonData.success) {
            // we'll just leave everything.
            displayAlertDialog(alertDialog, dialogInfo, "Vial successfully deleted !!!");
        }
        else {
            displayAlertDialog(alertDialog, dialogInfo, "Delete vial failed", jsonData.errors); 
        }
    })
    // upon reject, we end here!!!
    .catch((error) => {
        displayAlertDialog(alertDialog, dialogInfo, "An error occurred", error);
    });
}

function doDeleteContainer() {
    displayConfirmationDialog(confirmDialog, dialogInfo, "Do you really want to delete his container ???", 
        "There ain't no going back!", _deleteContainer);
}

</script>

<template>
    <div class="main-panel">
        <form id="searchPanelForm" v-on:submit.prevent="">
            <table style="margin-left:auto;margin-right:auto; border-spacing:5px;">
                <tr>
                    <td class="formFieldLabel">
                        <!-- <label works too-->
                        <label>Barcode (min {{MIN_BARCODE_LENGTH}} chars):</label></td>
                    <td class="formField">
                        <!-- note that the onChange event only fires when we leave the field.  onInput fires
                             whenever the field changes (each key) but NOT for ctrl, alt, shift, arrows, etc-->
                        <input type="text" v-model="formData.barcode" required :minlength="MIN_BARCODE_LENGTH"
                            v-on:input="barcodeChanged"/>
                    </td>
                    <td></td>
                    <td>
                        <button className="normalButton" v-on:click="doSearch">Search</button>
                    </td>
                </tr>
                <tr>
                    <td class="formFieldLabel">Container Type:</td>
                    <td class="formField">
                        <input type="text" v-model="formData.container_type" readonly/>
                    </td>
                </tr>
                <tr>
                    <td class="formFieldLabel">Location:</td>
                    <td class="formField">
                        <input type="text" v-model="formData.location" readonly />
                    </td>
                </tr>
                <tr v-show="formData.lot">
                    <td class="formFieldLabel">Reagent Name:</td>
                    <td class="formField">
                        <input type="text" v-model="formData.reagent" readonly />
                    </td>
                </tr>
                <tr v-show="formData.lot">
                    <td class="formFieldLabel">Lot Name:</td>
                    <td class="formField">
                        <input type="text" v-model="formData.lot" readonly />
                    </td>
                </tr>
                <tr v-show="formData.lot">
                    <td class="formFieldLabel">Amount ({{AMOUNT_UNIT}}):</td>
                    <td class="formField">
                        <!-- this will allow floating point values through.  for now just enter integers.  -->
                        <input type="number" class="no-spinners" :min="MIN_AMOUNT" :max="MAX_AMOUNT" 
                            required :id="amountField" v-model="formData.amount"/>
                        <input type="hidden" v-model="formData.amount_unit"/>
                    </td>
                </tr>
                <tr v-show="formData.lot">
                    <td class="formFieldLabel">Concentration ({{CONCENTRATION_UNIT}}):</td>
                    <td class="formField">
                        <input type="number" class="no-spinners" :min="MIN_CONCENTRATION" :max="MAX_CONCENTRATION" 
                            required :id="concentrationField" v-model="formData.concentration"/>
                        <input type="hidden" v-model="formData.concentration_unit"/>
                    </td>
                </tr>
            </table>
        </form>
        <p v-show="formData.lot" className="importantMessage">
            You can only change the amount and concentration.<br/>
            You cannot change the barcode.
        </p>
        <div v-show="formData.lot" className="buttonRow">
            <button class="normalButton" :disabled="disabledFlag"
                v-on:click="doUpdateContainer">Update</button>
            <span class="spacerSmall"/>
            <button class="normalButton" :disabled="disabledFlag"
                v-on:click="doDeleteContainer">Delete</button>
        </div>
        <Alert :dialogInfo="dialogInfo" ref="alertDialog"/>
        <Confirm :dialogInfo="dialogInfo" ref="confirmDialog"/>
    </div>
</template>

<style scoped>

</style>
