import React from 'react';

export default class HttpService {

    private baseURL = process.env.NEXT_PUBLIC_SERVICE_URL_BASE;
    private mode = 'cors';
    private headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    };
    /*
    private headers = new HttpHeaders({
      "Content-Type": "application/json",
      "Accept": "application/json"
    });
    */
    // private mode = 'same-origin';  // Do not send CSRF token to another domain.

    get_reagents() {
        let url = this.baseURL + "reagents/?limit=10";
        let resp = fetch(
            url, {
              method: 'GET', 
              // mode: this.mode,
              headers: this.headers,
            });
        return resp;
    }

    doRequest(url: string, method: string, data: any = null, params: any = null) {
      let requestURL = this.baseURL + url;
      if (params) {
        requestURL += '?' + new URLSearchParams(params);
      }
      console.log("*** request " + requestURL);
      let requestOptions = {
        method: method, 
        // mode: this.mode,
        headers: this.headers,
        body: data ? JSON.stringify(data) : null
      };
      let resp = fetch(requestURL, requestOptions);
      return resp.then(
        // we want to pass the response status (and matching text) and the returned payload
        // to the next step.  the returned payload is still a promise so we can't get to it yet.
        // we want all 3 values to create an appropriate error message since "operational errors"
        // (like invalid lot) WILL come back as JSON.  we don't want to blindly look at status != 200.
        (res) => {
          const response_status = res.status,
                response_status_text = res.statusText,
                response_text = res.text();
          return Promise.all([response_status, response_status_text, response_text])
        }
      ).then(
        // now turn those 3 items into one object since dr bobby hates that "tuple-like" return value
        (data) => {
            return {status: data[0], statusText: data[1], text: data[2]};
        }
      );
    }

    addVial(vialData: any) {
      return this.doRequest("container", "POST", vialData);
    }

    updateVial(vialData: any) {
      return this.doRequest("container/" + vialData.id, "PUT", vialData);
    }

    deleteVial(vialId: number) {
      return this.doRequest("container/" + vialId, "DELETE");
    }

    locateVial(locateData: any) {
      return this.doRequest("locate_container", "PUT", locateData);
    }

    getContainerByBarcode(barcode: string) {
      return this.doRequest("container_by_barcode", "GET", null, {barcode:barcode})
    }

    pickList(pickListData: [any]) {
      return this.doRequest("pick_list", "POST", pickListData);
    }
}
