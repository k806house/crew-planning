import {AfterViewInit, Component, ViewChild} from '@angular/core';
import {MatPaginator} from '@angular/material/paginator';
import {MatTableDataSource} from '@angular/material/table';
import {PdfService} from '../_services/pdf.service';
import {TrainService} from '../_services/train.service';
import {first} from 'rxjs/operators';
import {ScheduleItem} from '../_models';

@Component({
  selector: 'app-brigade-schedule',
  templateUrl: './brigade-schedule.component.html',
  styleUrls: ['./brigade-schedule.component.less']
})
export class BrigadeScheduleComponent implements AfterViewInit {
  displayedColumns: string[] = ['train', 'time', 'from', 'to', 'brigade', 'brigadir'];
  dataSource: MatTableDataSource<ScheduleItem>;
  crewPairs: ScheduleItem[];

  @ViewChild(MatPaginator) paginator: MatPaginator;

  constructor(private pdfService: PdfService, private trainService: TrainService) {
    this.trainService.getCrewPairs('01.01.2000', '01.01.2020').pipe(first()).subscribe(items => {
      this.crewPairs = items;
      this.dataSource = new MatTableDataSource<ScheduleItem>(items);
      this.dataSource.paginator = this.paginator;
    });
  }

  ngAfterViewInit() {
    // this.dataSource.paginator = this.paginator;
  }

  // tslint:disable-next-line:typedef
  PrintPdf() {
    this.pdfService.generatePdf(this.crewPairs);
  }
}


// export interface ScheduleElement {
//   train: string;
//   time: string;
//   from: string;
//   to: string;
//   brigade: number;
//   brigadir: string;
// }
//
// const ELEMENT_DATA: ScheduleElement[] = [
//   {train: '132У', time: '07:03', from: 'Пенза', to: 'Самара', brigade: 109, brigadir: 'Леонов'},
//   {train: '111У', time: '07:30', from: 'Самара', to: 'Пенза', brigade: 103, brigadir: 'Иванов'},
//   {train: '131У', time: '12:45', from: 'Самара', to: 'Пенза', brigade: 104, brigadir: 'Петров'},
//   {train: '101Й', time: '12:55', from: 'Самара', to: 'Пенза', brigade: 204, brigadir: 'Сидоров'},
//   {train: '109Й', time: '18:48', from: 'Самара', to: 'Пенза', brigade: 106, brigadir: 'Константинов'},
//   {train: '110Й', time: '16:30', from: 'Пенза', to: 'Самара', brigade: 203, brigadir: 'Еремин'},
// ];
