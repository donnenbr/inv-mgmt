<script setup>
  import AddVial from '@/components/AddVial/AddVial.vue'
  import SearchInventory from '@/components/SearchInventory/SearchInventory.vue';
  import LocateVial from '@/components/LocateVial/LocateVial.vue';
  import PickList from '@/components/PickList/PickList.vue';

  import { ref } from 'vue'
  const selected_panel = ref("add vial");
</script>

<template>
  <div id="button-panel" style='text-align:center;'>
      <button class="tabPanelButton" @click="selected_panel='add vial'">Add New Vial</button>
      <button class="tabPanelButton" @click="selected_panel='search inventory'">Search Inventory</button>
      <button class="tabPanelButton" @click="selected_panel='locate vial'">Locate Vial</button>
      <button class="tabPanelButton" @click="selected_panel='pick list'">Pick List</button>
    </div>
    <hr class="tabPanelBlank"/>
    <div id="main-panel">
      <div v-show="(selected_panel == 'add vial')" id="add_vial_panel">
        <AddVial />
      </div>
      <div v-show="(selected_panel == 'search inventory')" id="search_inventory_panel">
       <SearchInventory/>
      </div>
      <div v-show="(selected_panel == 'locate vial')" id="locate_vial_panel">
        <LocateVial/>
      </div>
      <div v-show="(selected_panel == 'pick list')" id="pick_list_panel">
        <pickList/>
      </div>
    </div>
</template>

<style scoped>
.tabPanelButton {
  background-color: var(--theme);
  color: white;
  font-size: 14pt;
  font-weight: bold;
  font-style: italic;
  padding: 10px;
  border-style: solid;
  border-width: 0;
  border-left-width: 1px;
  border-right-width: 1px;
  border-color: white;
  border-top-left-radius: 10px;
  border-top-right-radius: 10px;
}
.tabPanelBlank {
  margin: 0px;
  height: 5px;
  background-color: var(--theme);
  border: none;
}

</style>
./components/AddVial/AddVial.vue