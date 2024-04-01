<script setup>
    const props = defineProps(['selectedBarcode', 'selectedContainer']);

    function containerIsParent() {
        let children = props.selectedContainer.value?.containers;
        return children != null;
    }

    function containerHasChildren() {
        let children = props.selectedContainer.value?.containers;
        return children?.length != null && children.length > 0;
    }

    function tableRowClicked(barcode) {
        props.selectedBarcode.barcode = barcode;
    }
</script>

<template>
    <div v-show="containerIsParent()">
        <div v-show="!containerHasChildren()">
            <h1>There are no child containers</h1>
        </div>    
        <div v-show="containerHasChildren()">
            <h3>Click on a row to see the contents of that container</h3>
            <!-- set the width so it maintains a constant width regardless of barcode length or if there is a reagent -->
            <table class="dataTable" style="width: 600px">
                <colgroup>
                    <col width="100px"/>
                    <col width="150px"/>
                    <col width="100px"/>
                    <!-- reagent will take up the remainder-->
                </colgroup>
                <thead>
                    <tr>
                        <th>Barcode</th>
                        <th>Container Type</th>
                        <th>Position</th>
                        <th>Reagent</th>
                    </tr>
                </thead>
                <tbody v-for="(cont,index) in props.selectedContainer.value?.containers">
                    <!-- n-th child class didn't work so we manually alter the class using the index -->
                    <tr :class="(index%2 == 1) ? 'dataTableRow' : ''" v-on:click="tableRowClicked(cont.barcode)" :key="index">
                        <td>{{(cont.barcode) ? cont.barcode : 'EMPTY'}}</td>
                        <td>{{cont.container_type}}</td>
                        <td>{{cont.position}}</td>
                        <td>{{cont.reagent}}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

</template>

<style scoped>

</style>