'use client'

import {useState, useEffect}  from 'react';

export interface ConfirmProps {
    dialogInfo: {};
    showModal: boolean;
    setShowModal: Function;
    yesHandler: Function|null;
    caller: Function|null;
}

export default function Confirm({dialogInfo,showModal,setShowModal}) {
    // each dialog MUST have a unique id
    let dialogId : string = Math.random().toString(36).replace('0.','alert.');
    console.log("*** dialog id " + dialogId);

    useEffect( () => {
        if (showModal) {
            showDialog();
        }
        else {
            closeDialog();
        }
     }, [showModal]);

     function closeDialog() {
        document.getElementById(dialogId)?.close()
    }
    
    function showDialog() {
        document.getElementById(dialogId)?.showModal();
    }

    function doYes() {
        setShowModal(false);
        if (dialogInfo.caller && dialogInfo.yesHandler) {
            dialogInfo.yesHandler.call(dialogInfo.caller);
        }
    }

    return (
        <dialog id={dialogId}>
            <div style={{margin: "20px"}}>
                <div className="dialogTitle">{dialogInfo.title}</div>
                {dialogInfo.messages?.map((msg,idx) => (
                            <p key={idx}>{msg}</p>
                        ))}
                <p>
                    <button className="normalButton" onClick={() => setShowModal(false)}>No</button>
                    <span style={{margin: "0px 20px 0px 20px"}}>&nbsp;</span>
                    <button className="normalButton" onClick={() => doYes()}>Yes</button>
                </p>
            </div>
        </dialog>
    );
}