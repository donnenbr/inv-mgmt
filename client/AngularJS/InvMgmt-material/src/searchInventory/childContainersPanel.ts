import { Component, Input, Output,  EventEmitter, ViewChild, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';

import {MatTableModule, MatTableDataSource} from '@angular/material/table';
import {MatSort, Sort, MatSortModule} from '@angular/material/sort';

@Component({
  selector: 'search-child-containers',
  standalone: true,
  templateUrl: './childContainersPanel.html',
  styleUrls: ['../app/app.component.scss'],
  imports: [ CommonModule, MatTableModule, MatSortModule ],
})
export class SearchChildContainersPanel {

   @Input() displayedContainer: any = null;
   // the current container
   dataSource: any = null;

   @Output() containerSelected = new EventEmitter<string>();
    tableRowClicked(row: any) {
      if (row && row.barcode) {
    	  this.containerSelected.emit(row.barcode);
      }
    }
    _displayedColumns = ["barcode", "container_type", "position", "reagent"];

  constructor() { }

  // this allows the sort val;ue to change when the view does.  by default, the table of
  // child containers is NOT included because there are no children when the panel is
  // initially created at app startup.
  // because of this version of TypeScript, we MUST assign it a value even if undefined.
  @ViewChild(MatSort) sort: MatSort|any = undefined;

  ngOnChanges(changes: any) {
    // currentValue can be null the first time thru
    if (changes.displayedContainer && changes.displayedContainer.currentValue &&
      changes.displayedContainer.currentValue.containers) {
      this.dataSource = new MatTableDataSource(changes.displayedContainer.currentValue.containers);
      // even tho the view changed to include the table we still don't have sort defined (because of
      // ViewChild) yest, so the timeout waits for the next eventy cycle where it WILL be defined.
      setTimeout(() => {
        this.dataSource.sort = this.sort; 
      })
      this.dataSource.sort = this.sort;
    }
    else {
      this.dataSource = null;
    }
  }  
  
  announceSortChange(sortState: Sort) {
    if (sortState.direction) {
      console.log('Sorted ' + sortState.direction + ' ending');
      console.dir(this.dataSource);
    }
    else {
      console.log("sort cleared");
    }
  }
  
}