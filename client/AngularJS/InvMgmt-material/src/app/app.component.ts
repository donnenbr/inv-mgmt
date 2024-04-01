import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import {AddVial} from '../addVial/addVial';
import {SearchInventory} from '../searchInventory/searchInventory';
import {LocateVial} from '../locateVial/locateVial';
import {PickList} from '../pickList/pickList';

import {MatTabsModule} from '@angular/material/tabs';

// import *  as my_class from '/src/assets/scripts/my_class.js';
import * as logger  
    from "../scripts/logger" ;


@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterOutlet, AddVial, SearchInventory, LocateVial, PickList, MatTabsModule],
  templateUrl: './app.component-material.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {

  title = 'Inventory Management';
  selected_panel = "add vial";
  hideMe = false;

  ngOnInit() {
    console.log("*** NG INIT");
    logger.print();
    let me = new logger.MyClass("bobby","da bear", 65);
    console.log(me.printMe());
  }
}
