import {Component, OnInit} from '@angular/core';
import {Router} from '@angular/router';


@Component({
  selector: 'app-toolbar',
  templateUrl: './topbar.component.html',
  styleUrls: ['./topbar.component.less']
})
export class TopbarComponent implements OnInit {

  constructor(private router: Router) {
  }

  ngOnInit(): void {
    //this.router.navigate(['login']);
  }

}
