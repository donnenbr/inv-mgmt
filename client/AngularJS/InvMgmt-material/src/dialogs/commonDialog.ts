import { Component, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';

import {
  MAT_DIALOG_DATA,
  MatDialogRef,
  MatDialogActions,
  MatDialogClose,
  MatDialogTitle,
  MatDialogContent
} from '@angular/material/dialog';
import {MatButtonModule} from '@angular/material/button';


@Component({
  selector: 'common--dialog',
  templateUrl: './commonDialog.html',
  styleUrls: ['../app/app.component.scss'],
  standalone: true,
  imports: [CommonModule, MatButtonModule, MatDialogActions, MatDialogClose, MatDialogTitle, MatDialogContent],
})


export class CommonDialog {
  constructor(public dialogRef: MatDialogRef<CommonDialog>,
    @Inject(MAT_DIALOG_DATA) public data: {title: string, messages: string[]}) {}
}