<script setup>
import { ref, watch } from 'vue';

const props = defineProps(['pickData','showMode']);

const showAvailable = ref(true), 
      showUnavailable = ref(true);

// this will fire every time we enter this component.  we want to reset the flags for showing available/unavailable
// samples whenever we return to this page.
watch(props.pickData, (newValue, prevValue) => {
    showAvailable.value = showUnavailable.value = true;
});

function availableSamplesExist() {
    return props.pickData.value?.available != null && props.pickData.value?.available.length > 0;
}
function unavailableSamplesExist() {
    return props.pickData.value?.unavailable != null && props.pickData.value?.unavailable.length > 0;
}
</script>

<template>
    <div class="main-panel">
        <div v-show="showAvailable && availableSamplesExist()">
            <table class="dataTable">
                <caption>Available Samples</caption>
                <thead>
                    <tr>
                        <th>Reagent</th>
                        <th>Requested<br/>Amount (uL)</th>
                        <th>Barcode</th>
                        <th>Location</th>
                        <th>Container<br/>Amount(uL)</th>
                        <th>Conc. (uM)</th>
                    </tr>
                </thead>
                <tbody v-for="(row,index) in props.pickData.value?.available">
                    <tr :class="(index%2 == 1) ? 'dataTableRow' : ''">
                        <td>{{row.reagent}}</td>
                        <td>{{row.requested_amount}}</td>
                        <td>{{row.barcode}}</td>
                        <td>{{row.position}}</td>
                        <td>{{row.amount}}</td>
                        <td>{{row.concentration}}</td>
                    </tr>
                </tbody>
            </table>
        </div>
        <br/>
        <div v-show="showUnavailable && unavailableSamplesExist()">
            <table class="dataTable">
                <caption>Unavailable Samples</caption>
                <thead>
                    <tr>
                        <th>Reagent</th>
                        <th>Requested<br/>Amount (uL)</th>
                        <th>Requested<br/>Conc. (uM)</th>
                    </tr>
                </thead>
                <tbody v-for="(row,index) in props.pickData.value?.unavailable">
                    <tr :class="(index%2 == 1) ? 'dataTableRow' : ''">
                        <td>{{row.reagent}}</td>
                        <td>{{row.amount}}</td>
                        <td>{{row.concentration}}</td>
                    </tr>
                </tbody>
            </table>
        </div>
        <p class="buttonRow">
            <button class="normalButton" @click="props.showMode.value='request'">Back to Request</button>
            <span v-show="availableSamplesExist() && unavailableSamplesExist()">
                <span class="spacerSmall"/>
                <button class="normalButton" @click="showAvailable = !showAvailable">Toggle Available</button>
                <span class="spacerSmall"/>
                <button class="normalButton" @click="showUnavailable = !showUnavailable">Toggle Unavailable</button>
            </span>
            </p>
    </div>
</template>

<style scoped>
</style>