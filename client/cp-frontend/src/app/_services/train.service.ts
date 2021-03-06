import {Injectable} from '@angular/core';
import {environment} from '../../environments/environment';
import {ScheduleItem, TrainAdd, TrainDelete} from '../_models';
import {HttpClient} from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class TrainService {

  constructor(private http: HttpClient) {
  }


  // tslint:disable-next-line:typedef
  addTrain(train: TrainAdd) {
    return this.http.post(`${environment.apiUrl}/route`,
      {
        trainTitle: train.title,
        from: +train.route === 1 ? 'Самара' : 'Пенза-1',
        to: +train.route === 2 ? 'Самара' : 'Пенза-1',
        startDate: `${train.dateStart} ${train.timeStart}:00`,
        endDate: `${train.dateEnd} ${train.timeEnd}:00`
      });
  }

  // check idk if works
  // tslint:disable-next-line:typedef
  deleteTrain(train: TrainDelete) {
    return this.http.request('delete', `${environment.apiUrl}/route`, {
      body:
        {
          trainTitle: train.title,
          from: +train.from === 1 ? 'Самара' : 'Пенза-1',
          startDate: `${train.date} ${train.time}:00`
        }
    });
  }

  getCrewPairs(start: string, end: string) {
    return this.http.post<ScheduleItem[]>(`${environment.apiUrl}/crew`, {
      startDate: '28/11/2020 03:00:00',
      endDate: '31/12/2020 23:00:00'
    });
  }

  updateCrew(start: string, end: string) {
    return this.http.post(`${environment.apiUrl}/trip_pairing`, {
      startDate: '28/11/2020 03:00:00',
      endDate: '31/12/2020 23:00:00'
    });
  }

}
