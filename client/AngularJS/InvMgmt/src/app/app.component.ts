import { Component, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import {AddVial} from '../addVial/addVial';
import {SearchInventory} from '../searchInventory/searchInventory';
import {LocateVial} from '../locateVial/locateVial';
import {PickList} from '../pickList/pickList';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterOutlet, AddVial, SearchInventory, LocateVial, PickList],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  // @ViewChild('panel1', { static: false }) panel1: Panel1;

  // don't need this
  /*
  @ViewChild(Panel1) panel1!: Panel1;
  @ViewChild(Panel2) panel2!: Panel2;
  @ViewChild(Panel3) panel3!: Panel3;
  @ViewChild(Panel4) panel4!: Panel4;
  panels : any = [];
  */

  title = 'Inventory Management';
  selected_panel = "add vial";
  hideMe = false;

  // or this
  /*
  ngAfterViewInit() {
      // let csrfToken = get_csrftoken();
      console.log("*** NEW csrf token " + this.csrfToken);
  }
  */

  showPanel(panelName:string) {
    this.selected_panel = panelName;
  }
}
