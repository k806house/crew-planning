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
  data;
  constructor() { }

  getData(): void{
    // json[‘xy’][i][0] == xs
    // json[‘xy’][i][1] == ys
    // json[‘labels’][i][j] == label
    const xy = json['xy'];
    const jsonLabels = json['labels'];

    // with open('data.json', 'r') as f:
    // data = f.read()
    // data = json.loads(data)
    // xs = []
    // ys = []
    // for i in range(len(data['xy'])):
    // xs.append(data['xy'][0])
    // ys.append(data['xy'][1])
    //
    // labels = []
    // for i in range(len(data['labels'])):
    // labels.append(data['labels'][i])

    for (const item of xy) {
      this.xs.push(item[0]);
      this.ys.push(item[1]);
    }

    for (const label of jsonLabels) {
      this.labels.push(label);
    }
    console.log('xs', this.xs);
    console.log('ys', this.ys);
    console.log('labels', this.labels);
    const trace1 = {
      x: this.xs[0],
      y: this.ys[0],
      mode: 'lines',
      type: 'scatter'
    };

    const trace2 = {
      x: this.xs[1],
      y: this.ys[1],
      mode: 'lines',
      type: 'scatter'
    };

    const trace3 = {
      x: this.xs[2],
      y: this.ys[2],
      mode: 'lines',
      type: 'scatter'
    };

    const trace4 = {
      x: this.xs[3],
      y: this.ys[3],
      mode: 'lines',
      type: 'scatter'
    };

    this.data = [trace1, trace2, trace3, trace4];
  }

  ngOnInit(): void {
    this.getData();
  }

}
