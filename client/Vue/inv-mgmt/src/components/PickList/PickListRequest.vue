<script setup>
import { ref } from 'vue';
import { pickList } from '@/httpService.js';
import { displayAlertDialog } from '@/utils.js';
import Alert from '@/components/dialogs/Alert.vue';
import { MIN_BARCODE_LENGTH, MIN_AMOUNT, MAX_AMOUNT, MIN_CONCENTRATION, MAX_CONCENTRATION,
            AMOUNT_UNIT, CONCENTRATION_UNIT } from '../../constants.js';

// sample reagents:
    /*
    Child_X10000015-8
    Child_X10000017-8
    Child_X10000051-6
    Child_X10000101-7
    Child_X10000104-7
    Child_X10000164-9
    Child_X10000181-3
    Child_X10000254-8
    Child_X10000262-5
    Child_X10000304-9
    Child_X10000386-5
    Child_X10000535-2
    Child_X10000543-9
    Child_X10000649-5
    Child_X10000762-5
    Child_X10000892-2
    Child_X10000900-5
    Child_X10000914-2
    Child_X10001118-9
    Child_X10001221-2
    Child_X10001224-2
    Child_X10001393-7
    Child_X10001493-3
    Child_X10001541-4
    Child_X10001694-5
    Child_X10001704-8
    Child_X10001721-2
    Child_X10001741-6
    Child_X10001776-7
    Child_X10001806-4
*/

const props = defineProps(['pickData','showMode']);

const dialogInfo = ref({ title: "", messages: []});

const alertDialog = ref();

function createEmptyFormData() {
    let data = [];
    for (let i = 1; i <= 10; ++i) {
        data.push({line_number: i, reagent: null, amount: null, concentration: null});
    }
    return data;
}

// the model does NOT have to be a ref
const formData = createEmptyFormData();

function unloadValues() {
    let valueArray = [];
    formData.forEach((row,idx) => {
        let reagent = row.reagent,
            amount = row.amount,
            concentration = row.concentration;
        if (reagent) {
            reagent = reagent.trim();
        }
        if (reagent) { // paranoid
            let record = { reagent: reagent, amount: amount, concentration: concentration, lineNum: row.line_number };
            valueArray.push(record);
        }
    });
    return valueArray;
}

function validateRows() {
    let errors = [];
    formData.forEach((row,idx) => {
        let reagent = row.reagent,
            amount = row.amount,
            concentration = row.concentration;
        if (reagent) {
            reagent = reagent.trim();
        }
        // at this point amount and concentration CANNOT be zero!!
        if (reagent || amount || concentration) {
            // if blanked out, amount and concentration will be '', not null or undefined
            if (!reagent || !amount  || !concentration) {
                errors.push('Data is incomplete on line ' + row.line_number);
            }
        }
    });
    return errors;
}

function doRequest() {
    // note that the field values are valid as far as their values if we get here.
    // we need to validate that each row with a val;ue in it is complete.
    let errors = validateRows();
    if (errors.length > 0) {
        displayAlertDialog(alertDialog, dialogInfo, "Please fix the following errors:", errors);
        return;
    }
    // so far so good
    let values = unloadValues();
    if (values.length < 1) {
        displayAlertDialog(alertDialog, dialogInfo, "No values were entered !!!");
        return;
    }
    let response = pickList(values);
    response.then((result) => {
        // try {
            let jsonData = result.data;
            if (jsonData.success) {
                let resultData = jsonData.data;
                // console.log(resultData);
                let available_samples = jsonData.data.available,
                    unavailable_samples = jsonData.data.unavailable;
                if (available_samples == null || unavailable_samples == null) {
                    console.dir(jsonData);
                    displayAlertDialog(alertDialog, dialogInfo, 
                        "Did not get back lists of available and unavailable samples");
                }
                else {
                    if (available_samples.length < 1) {
                        displayAlertDialog(alertDialog, dialogInfo, "No samples were available");
                    }
                    else {
                        props.pickData.value = jsonData.data;
                        props.showMode.value = 'result';
                    }
                }
            }
            else {
                displayAlertDialog(alertDialog, dialogInfo,
                    "Pick list request failed", jsonData.errors); 
            }
        // }
        // catch (ex) {
            // can't use Promise.reject here (because of the resolutions???  no next step????)
            // throw an exception
        //     throw("Error code " + result.status + " : " + result.statusText);
        // }
    })
    // upon reject, we end here!!!
    .catch((error) => {
        displayAlertDialog(alertDialog, dialogInfo, "An error occurred", error);
    });
}

</script>

<template>
     <div class="main-panel">
        <form id='picklist-form' v-on:submit.prevent="doRequest">
            <table className="dataTable">
                <thead>
                    <tr>
                        <th></th>
                        <th>Reagent</th>
                        <th>Amount {{AMOUNT_UNIT}}</th>
                        <th>Concentration {{CONCENTRATION_UNIT}}</th>
                    </tr>
                </thead>
                <tbody v-for="(row,index) in formData">
                    <!-- note how we can link each field to a property in an array element.  just like struts.
                        How cool!!!!-->
                    <tr>
                        <td>{{ row.line_number }}</td>
                        <td>
                                <input type="text" v-model="formData[index].reagent"/>
                        </td>
                        <td>
                            <input type="number" className="no-spinners" :min="MIN_AMOUNT" :max="MAX_AMOUNT" 
                                v-model="formData[index].amount"/>
                        </td>
                        <td>
                        <input type="number" className="no-spinners" :min="MIN_CONCENTRATION" :max="MAX_CONCENTRATION"
                            v-model="formData[index].concentration"/>
                        </td>
                    </tr>
                </tbody>
            </table>
            <p class="importantMessage">For any line, all fields are required</p>
            <p class="buttonRow">
                <button class="normalButton" type="submit">Request</button>
            </p>
        </form>
        <Alert :dialogInfo="dialogInfo" ref="alertDialog"/>
     </div>
</template>