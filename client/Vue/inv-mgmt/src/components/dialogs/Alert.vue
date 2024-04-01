<script setup>
    const props = defineProps(['dialogInfo'])
    
    let dialogId = Math.random().toString(36).replace('0.','alert.');

    function closeDialog() {
        document.getElementById(dialogId)?.close();
    }
    
    function showDialog() {
        document.getElementById(dialogId)?.showModal();
    }

    // this exposes the show value to the outside so it can be set to true to show the dialog
    defineExpose({
        showDialog
    })

</script>

<template>
    <dialog :id="dialogId">
        <div style="margin: 10px">
            <div class="dialogTitle">{{props.dialogInfo.title}}</div>
            <p>
                <div v-for="msg in props.dialogInfo.messages">
                    {{ msg }}
                </div>
            </p>
            <button class="normalButton dialogButton" @click="closeDialog">Continue</button>
        </div>
        </dialog>
</template>

<style scoped src="./dialogs.css">

</style>
