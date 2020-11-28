import { Component, OnInit } from '@angular/core';

import * as json from '../mock-data/data.json';



@Component({
  selector: 'app-visualization',
  templateUrl: './visualization.component.html',
  styleUrls: ['./visualization.component.less']
})
export class VisualizationComponent implements OnInit {
  xs = [];
  ys = [];
  labels = [];
  layout;
  constructor() { }

  getData(): void{
    // json[‘xy’][i][0] == xs
    // json[‘xy’][i][1] == ys
    // json[‘labels’][i][j] == label
    const xy = json['xy'];
    const jsonLabels = json['labels'];

    for (const item of xy) {
      this.xs.push(item[0]);
      this.ys.push(item[1]);
    }
  }

  ngOnInit(): void {
    this.getData();
  }

}
