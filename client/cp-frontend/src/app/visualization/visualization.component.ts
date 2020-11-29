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
  layout = {
    annotations: [],
  };
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
    this.layout['xaxis'] = {
      range: [this.xs[0][0], this.xs[0][7]]
    };
    console.log('xs', this.xs);
    console.log('ys', this.ys);
    console.log('labels', this.labels);

    for (let i = 0; i < this.xs.length; i++) {
      for (let j = 0; j < this.xs[i].length; j++) {
        this.layout['annotations'].push({
          x: this.xs[i][j],
          y: this.ys[i][j],
          xref: 'x',
          yref: 'y',
          text: 'Text',
          showarrow: false,
          bordercolor: '#f0f0f0',
          borderwidth: 2,
          borderpad: 4,
          bgcolor: '#ff7f0e',
          opacity: 0.8
        });
      }
    }

    console.log('annotatios', this.layout);

    const size = this.xs[0].length;
    for (let i = 0; i < size; i++) {
      const trace = {
        x: this.xs[i],
        y: this.ys[i],
        // mode: 'lines',
        type: 'scatter',
      };
      this.data.push(trace);
    }
  }

  ngOnInit(): void {
    this.getData();
  }

}
