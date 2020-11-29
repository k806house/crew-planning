import {Component, OnInit} from '@angular/core';
import {FormGroup, FormControl, Validators, FormBuilder} from '@angular/forms';
import {TrainDelete, TrainAdd} from '../_models';
import {DatePipe} from '@angular/common';
import {TrainService} from '../_services/train.service';

interface Route {
  value: number;
  viewValue: string;
}

@Component({
  selector: 'app-options',
  templateUrl: './options.component.html',
  styleUrls: ['./options.component.less']
})
export class OptionsComponent implements OnInit {
  addForm: FormGroup;
  deleteForm: FormGroup;

  constructor(private formBuilder: FormBuilder, public datepipe: DatePipe, private trainService: TrainService) {
  }

  currentInterval: string;
  intervals: string[] = ['Следущая неделя', 'Следущий месяц', 'Другой'];
  routs: Route[] = [
    {value: 1, viewValue: 'Самара – Пенза 1'},
    {value: 2, viewValue: 'Пенза 1 – Самара'}
  ];

  range = new FormGroup({
    start: new FormControl(),
    end: new FormControl()
  });

  trainsToDelete: TrainDelete[] = [];
  trainsToAdd: TrainAdd[] = [];

  get f() {
    return this.addForm.controls;
  }

  get g() {
    return this.deleteForm.controls;
  }

  ngOnInit(): void {
    this.addForm = this.formBuilder.group({
      title: ['', Validators.required],
      timeStart: ['', Validators.required],
      route: ['', Validators.required],
      dateStart: ['', Validators.required],
      timeEnd: ['', Validators.required],
      dateEnd: ['', Validators.required]
    });

    this.deleteForm = this.formBuilder.group({
      title: ['', Validators.required],
      date: ['', Validators.required],
      time: ['', Validators.required],
      route: ['', Validators.required]
    });
  }

  // tslint:disable-next-line:typedef
  onSubmit() {
    const train = new TrainAdd();
    train.title = this.f.title.value;
    train.dateStart = this.datepipe.transform(this.f.dateStart.value, 'dd/MM/yyyy');
    train.dateEnd = this.datepipe.transform(this.f.dateEnd.value, 'dd/MM/yyyy');
    train.route = this.f.route.value;
    train.timeStart = this.f.timeStart.value;
    train.timeEnd = this.f.timeEnd.value;
    this.trainsToAdd.push(train);
    console.log(train);
    this.trainService.addTrain(train).pipe().subscribe(data => console.log(data));
    return 0;
  }

  // tslint:disable-next-line:typedef
  onDelete() {
    const train = new TrainDelete();
    train.title = this.g.title.value;
    train.date = this.datepipe.transform(this.g.date.value, 'dd/MM/yyyy');
    train.time = this.g.time.value;
    train.from = this.g.route.value;
    this.trainsToDelete.push(train);
    console.log(train);
    this.trainService.deleteTrain(train).pipe().subscribe(data => console.log(data));
    return 0;
  }
}
