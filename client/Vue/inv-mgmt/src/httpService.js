import axios from 'axios';

import { HTTP_OK, HTTP_BAD_REQUEST, HTTP_NOT_FOUND } from './constants';
const SERVER_URL_BASE = import.meta.env.VITE_SERVICE_URL_BASE;

const headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
};

async function doRequest(url, method, data = null, params = null, allow_404=false) {
    let requestConfig = {
      baseURL: SERVER_URL_BASE,
      url: url,
      method: method, 
      // mode: this.mode,
      headers: headers,
      params: params,
      data: data,
      validateStatus: function (status) {
        // seems we need to include NOT FOUND.  we only want that ON DEMAND since we want to catch invalid api endpoints.
        // maybe returning NOT_FOUND for lookups by ID is not really a great idea???
        return (status >= 200 && status < 300) || status == HTTP_BAD_REQUEST || (allow_404 && status == HTTP_NOT_FOUND);
      },
    };
    let resp = axios(requestConfig);
    return resp.then(
        // we want to pass the response status (and matching text) and the returned payload
        // to the next step.  the returned payload is still a promise so we can't get to it yet.
        // we want all 3 values to create an appropriate error message since "operational errors"
        // (like invalid lot) WILL come back as JSON.  we don't want to blindly look at status != 200.
        (res) => {
          const response_status = res.status,
                response_status_text = res.statusText,
                response_data = res.data
          return Promise.all([response_status, response_status_text, response_data])
        }
      ).then(
        // now turn those 3 items into one object since dr bobby hates that "tuple-like" return value
        (data) => {
            return {status: data[0], statusText: data[1], data: data[2]};
        }
      ).then(
        (data) => {
          // assure we have a data object with success, data (if success is true) and errors (if not)
          // only applies if status code is HTTP_OK or HTTP_BAD_REQUEST
          if (data.status == HTTP_OK || data.status == HTTP_BAD_REQUEST) {
            const respData = data.data;
            if (!respData) {
              throw "No data found in response";
            }
            if (respData.success == undefined) {
              throw "Success flag not in response data";
            }
            if (respData.success) {
              if (respData.data == undefined) {
                throw "Data value not in response data";
              }
            }
            // let the caller deal with the errors if no success
          }
          return data;
        }
      );
  }

export function addVial(vialData) {
    return doRequest("container", "POST", vialData);
}

export function getContainerByBarcode(barcode) {
  return doRequest("container_by_barcode", "GET", null, {barcode:barcode}, true)
}

export function updateVial(vialData) {
  return doRequest("container/" + vialData.id, "PUT", vialData);
}

export function deleteVial(vialId) {
  return doRequest("container/" + vialId, "DELETE");
}

export function locateVial(locateData) {
  return doRequest("locate_container", "PUT", locateData);
}

export function pickList(pickListData) {
  return doRequest("pick_list", "POST", pickListData);
}
