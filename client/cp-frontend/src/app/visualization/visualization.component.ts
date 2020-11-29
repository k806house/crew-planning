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
  data = [];
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

    for (const label of jsonLabels) {
      this.labels.push(label);
    }
    this.layout = {
      xaxis: {
        range: [this.xs[0][0], this.xs[0][7]]
      }};
    console.log('xs', this.xs);
    console.log('ys', this.ys);
    console.log('labels', this.labels);
    const size = this.xs.length;
    for (let i = 0; i < size; i++) {
      const trace = {
        x: this.xs[i],
        y: this.ys[i],
        mode: 'lines',
        type: 'scatter'
      };
      this.data.push(trace);
    }
  }

  ngOnInit(): void {
    this.getData();
  }

}
