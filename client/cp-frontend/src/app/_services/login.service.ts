import {Injectable} from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class LoginService {
  public isLogin: boolean;

  constructor() {
    this.isLogin = true;
    console.log('constr');
  }
}
