<script setup>
import { ref, watch } from 'vue'

import { MIN_BARCODE_LENGTH  } from '../../constants.js';
import { locateVial } from '@/httpService.js';
import { displayAlertDialog } from '@/utils.js';
import Alert from '@/components/dialogs/Alert.vue';

const dialogInfo = ref({ title: "", messages: []});

const alertDialog = ref();

const formData = {
    barcode: null,
    parent_barcode: null,
    position: null
};

function submitLocateVial() {
    const resp = locateVial(formData);
    resp.then((result) => {
      try {
        let jsonData = result.data;
        if (jsonData.success) {
            displayAlertDialog(alertDialog, dialogInfo, "Vial successfully located!!!");
        }
        else {
            displayAlertDialog(alertDialog, dialogInfo, "Locate vial failed", jsonData.errors); 
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
    <div class="main-panel">
        <form v-on:submit.prevent="submitLocateVial">
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
                    <td class="formFieldLabel">Parent Barcode (min {{MIN_BARCODE_LENGTH}} chars):</td>
                    <td class="formField">
                        <input type="text" v-model="formData.parent_barcode" required :minlength="MIN_BARCODE_LENGTH"/>
                    </td>
                </tr>
                <tr>
                    <td class="formFieldLabel">Position:</td>
                    <td class="formField">
                        <input type="text" v-model="formData.position" required />
                    </td>
                </tr>
            </table>
            <p class="importantMessage">ALL Fields are required</p>
            <button class="normalButton" type="submit">Locate It</button>
        </form>
        <Alert :dialogInfo="dialogInfo" ref="alertDialog"/>
    </div>

</template>

<style scoped>

</style>