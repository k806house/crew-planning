import {Component, OnInit} from '@angular/core';
import {FormGroup, FormControl, Validators, FormBuilder} from '@angular/forms';
import {Train, TrainPrintable} from '../_models';
import {DatePipe} from '@angular/common';

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

  constructor(private formBuilder: FormBuilder, public datepipe: DatePipe) {
  }

  currentInterval: string;
  intervals: string[] = ['Следущая неделя', 'Следущий месяц', 'Другой'];
  currentRout: string;
  routs: Route[] = [
    {value: 1, viewValue: 'Самара – Пенза 1'},
    {value: 2, viewValue: 'Пенза 1 – Самара'}
  ];

  range = new FormGroup({
    start: new FormControl(),
    end: new FormControl()
  });

  trainsToDelete: Train[] = [];
  trainsToAdd: TrainPrintable[] = [];

  get f() {
    return this.addForm.controls;
  }

  ngOnInit(): void {
    this.addForm = this.formBuilder.group({
      title: ['', Validators.required],
      time: ['', Validators.required],
      route: ['', Validators.required],
      date: ['', Validators.required],

    });
  }

  // tslint:disable-next-line:typedef
  onSubmit() {
    console.log(this.f);
    const train = new TrainPrintable();
    train.title = this.f.title.value;
    train.date = this.datepipe.transform(this.f.date.value, 'dd/MM/yyyy');
    train.route = this.f.route.value;
    train.time = this.f.time.value;
    this.trainsToAdd.push(train);
    return 0;
    // this.trainsToAdd
    // this.submitted = true;
    //
    // // stop here if form is invalid
    // if (this.loginForm.invalid) {
    //   return;
    // }
    //
    // this.loading = true;
    // this.authenticationService.login(this.f.username.value, this.f.password.value)
    //   .pipe(first())
    //   .subscribe(
    //     data => {
    //       this.router.navigate([this.returnUrl]);
    //     },
    //     error => {
    //       this.error = error;
    //       this.loading = false;
    //     });
  }
}
