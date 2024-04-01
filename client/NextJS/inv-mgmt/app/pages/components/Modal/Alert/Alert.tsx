'use client'

import {useEffect}  from 'react';

export interface AlertProps {
    dialogInfo: {};
    showModal: boolean;
    setShowModal: Function;
}

export default function Alert({dialogInfo,showModal,setShowModal}) {
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

    return (
        <dialog id={dialogId}>
            <div style={{margin: "20px"}}>
                <div className="dialogTitle">{dialogInfo.title}</div>
                {dialogInfo.messages?.map((msg,idx) => (
                            <p key={idx}>{msg}</p>
                        ))}
                <button className="normalButton" onClick={() => setShowModal(false)}>Continue</button>
            </div>
        </dialog>
    );
}

