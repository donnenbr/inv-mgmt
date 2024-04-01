import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams, HttpParamsOptions } from  '@angular/common/http';

@Injectable({
  providedIn: 'root'
})

export class HttpService {

    private baseURL = '/service';
    private headers = new HttpHeaders({
      "Content-Type": "application/json",
      "Accept": "application/json"
    });

    constructor(private http: HttpClient) { }
    private what: any;

    // just a test
    getContainerTypes() {
      let url = this.baseURL + "container_type";
      return this.http.get(url);
    }

    addVial(vial: any) {
      let url = this.baseURL + "container";
      return this.http.post(url=url,JSON.stringify(vial),{headers:this.headers});
    }

    locateVial(data:any) {
      let url = this.baseURL + "locate_container";
      return this.http.put(url=url,JSON.stringify(data),{headers:this.headers});
    }

    searchContainer(barcode: string) {
      let url = this.baseURL + "container_by_barcode",
          httpParams = new HttpParams().set("barcode", barcode);
        return this.http.get(url, {params:httpParams});
    }

    updateVial(vial: any) {
      let url = this.baseURL + "container/" + vial.id;
      return this.http.put(url=url,JSON.stringify(vial),{headers:this.headers});
    }

    deleteVial(vial: any) {
      let url = this.baseURL + "container/" + vial.id;
      return this.http.delete(url=url,{headers:this.headers});
    }

    pickList(values: [any]) {
      let url = this.baseURL + "pick_list";
      return this.http.post(url=url,JSON.stringify(values),{headers:this.headers});
    }
}
