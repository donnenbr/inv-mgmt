<script setup>
import { ref } from 'vue'

import { MIN_BARCODE_LENGTH, MIN_AMOUNT, MAX_AMOUNT, MIN_CONCENTRATION, MAX_CONCENTRATION,
            AMOUNT_UNIT, CONCENTRATION_UNIT } from '../../constants.js';

import { addVial } from '@/httpService.js';
import {  displayAlertDialog } from '@/utils.js';
import Alert from '@/components/dialogs/Alert.vue';

const dialogInfo = ref({ title: "", messages: []});

const alertDialog = ref();

// formData does NOT need to be a ref since we only want to pull data from the form
// it WOULD need to be a ref if we wanted to update data on the form.
const formData = {
    barcode: null,
    lot: null,
    amount: null,
    amount_unit: AMOUNT_UNIT,
    concentration: null,
    concentration_unit: CONCENTRATION_UNIT
};

function submitAddVial() {
    const resp = addVial(formData);
    resp.then((result) => {
      try {
        // we expect to get here if the response status code is OK or BAD REQUEST.  both should have the usual
        // data included.  returned data is already deserialized.
        let jsonData = result.data;
        if (jsonData.success) {
            displayAlertDialog(alertDialog, dialogInfo, "Vial successfully added!!!");
        }
        else {
            displayAlertDialog(alertDialog, dialogInfo, "Add vial failed", jsonData.errors); 
        }
      }
      catch (ex) {
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
</script>

<template>
  <!-- align everything to the center.  really just effects the <p> and <button> at the end-->
    <div class="main-panel">
        <form v-on:submit.prevent="submitAddVial" id="addVialForm">
            <table style="margin-left:auto;margin-right:auto; border-spacing:5px;">
                <tr>
                    <td class="formFieldLabel">
                        <!-- <label works too-->
                        <label for="addvial-barcode">Barcode (min {{MIN_BARCODE_LENGTH}} chars):</label></td>
                    <td class="formField">
                        <input type="text" v-model="formData.barcode" required :minlength="MIN_BARCODE_LENGTH"/>
                    </td>
                </tr>
                <tr>
                    <td class="formFieldLabel">Lot name:</td>
                    <td class="formField">
                        <input type="text" v-model="formData.lot" style="width:100%" required />
                    </td>
                </tr>
                <tr>
                    <td class="formFieldLabel">Amount ({{AMOUNT_UNIT}}):</td>
                    <td class="formField">
                        <!-- this will allow floating point values through.  for now just enter integers.  -->
                        <input type="number" class="no-spinners" :min="MIN_AMOUNT" :max="MAX_AMOUNT" 
                            required v-model="formData.amount"/>
                        <input type="hidden" v-model="formData.amount_unit"/>
                    </td>
                </tr>
                <tr>
                    <td class="formFieldLabel">Concentration ({{CONCENTRATION_UNIT}}):</td>
                    <td class="formField">
                        <input type="number" class="no-spinners" :min="MIN_CONCENTRATION" :max="MAX_CONCENTRATION" 
                            required v-model="formData.concentration"/>
                        <input type="hidden" v-model="formData.concentration_unit"/>
                    </td>
                </tr>
            </table>
            <p class="importantMessage">ALL Fields are required</p>
            <!-- this disables the save button if the form is invalid, but we want to display the errors to the user
                instead of them wondering why the buuton is disabled.
            <button type="submit" [disabled]="!dataForm.valid">Save It</button>
            -->
            <button class="normalButton" type="submit">Save It</button>
        </form>
        <Alert :dialogInfo="dialogInfo" ref="alertDialog"/>
    </div>
</template>

<style scoped>

</style>
