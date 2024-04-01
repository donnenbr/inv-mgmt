
export function serverError(message:string, errorMessages: string[]|string) {
    // effectively copied from the extjs version
    let errors = errorMessages;
    
    if (!Array.isArray(errors)) {
        errors = [errors];
    }
    displayAlert(message, errors);
}

export function displayAlert(title: string, messages: string[]|null = null) {
    // for now
    let msg = title ;
    if (messages) {
        msg += "\n\n";
        msg += messages.join("\n");
    }
    alert(msg);
}
