/*
 * This file launches the application by asking Ext JS to create
 * and launch() the Application class.
 */
Ext.application({
    extend: 'InvMgmt.Application',

    name: 'InvMgmt',

    requires: [
        // This will automatically load all classes in the InvMgmt namespace
        // so that application classes do not need to require each other.
        'InvMgmt.*'
    ],

    // The name of the initial view to create.
    mainView: 'InvMgmt.view.main.Main'
});
