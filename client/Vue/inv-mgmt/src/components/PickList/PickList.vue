<script setup>
import { ref, watch } from 'vue'

import PickListRequest from './PickListRequest.vue';
import PickListResult from './PickListResult.vue';

const pickData = ref({}),
      showMode = ref({value: 'request'})

watch(pickData, (newValue, prevValue) => {
    console.log("*** pick data changed");
    console.log(newValue);
    console.log(pickData);
});

</script>

<template>
    <div class="main-panel">
        <div v-show="showMode.value == 'request'">
            <PickListRequest :pickData="pickData" :showMode="showMode"/>
        </div>
        <div v-show="showMode.value == 'result'">
            <PickListResult :pickData="pickData" :showMode="showMode"/>
        </div>
    </div>

</template>