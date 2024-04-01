<script setup>
import { ref, watch } from 'vue'

import SearchPanel from './SearchPanel.vue';
import SearchChildContainers from './SearchChildContainers.vue';

// these HAVE to be objects for the change to be detected.  String (for selectedBarcode) will NOT do!!
// selectedContainer - used to communicate the selected container (result of search) from SearchPanel
//                     to SearchChildContainers
// selectedBarcode - used to communicate the barcode of the child container clicked in the table
//                   SearctChildContainers to SearchPanel so it can do the search.
const selectedBarcode = ref({}),
      selectedContainer = ref({});

</script>

<template>
    <div class="main-panel">
        <SearchPanel :selectedBarcode="selectedBarcode" :selectedContainer="selectedContainer"/>
        <SearchChildContainers :selectedBarcode="selectedBarcode" :selectedContainer="selectedContainer"/>
    </div>

</template>