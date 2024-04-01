import { ref } from 'vue'

export function displayAlertDialog(alertDialog, dialogInfo, title, messages = null) {
    dialogInfo.value.title = title;
    let messageArr;
    if (messages) {
        if (Array.isArray(messages)) {
            messageArr = messages;
        }
        else {
            messageArr = [messages];
        }
        dialogInfo.value.messages = messageArr;
    }
    else {
        dialogInfo.value.messages = [];
    }
    alertDialog.value.showDialog();
}

export function displayConfirmationDialog(confirmDialog, dialogInfo, title, messages = null, yesHandler=null) {
    dialogInfo.value.title = title;
    dialogInfo.value.yesHandler = yesHandler;
    let messageArr;
    if (messages) {
        if (Array.isArray(messages)) {
            messageArr = messages;
        }
        else {
            messageArr = [messages];
        }
        dialogInfo.value.messages = messageArr;
    }
    else {
        dialogInfo.value.messages = [];
    }
    confirmDialog.value.showDialog();
}