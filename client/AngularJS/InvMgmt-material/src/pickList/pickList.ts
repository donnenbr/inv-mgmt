import { Component } from '@angular/core';
import {PickListRequest} from './request'
import {PickListResult} from './result'


@Component({
  selector: 'pick-list',
  standalone: true,
  templateUrl: './pickList.html',
  styleUrls: ['../app/app.component.scss'],
  imports: [PickListRequest, PickListResult]
})
export class PickList {
  showRequest = true;

  resultData = null;

  resultChanged(data: any) {
    this.resultData = data;
    this.showRequest = false;
  }

  displayRequestChanged(flag:boolean) {
    this.showRequest = true;
  }

}