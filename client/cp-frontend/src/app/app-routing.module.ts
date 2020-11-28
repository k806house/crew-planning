import {NgModule} from '@angular/core';
import {Routes, RouterModule} from '@angular/router';
import {LoginComponent} from './login/login.component';
import {TopbarComponent} from './topbar/topbar.component';
import {OptionsComponent} from './options/options.component';
import {BrigadeScheduleComponent} from './brigade-schedule/brigade-schedule.component';
import {VisualizationComponent} from './visualization/visualization.component';

const routes: Routes = [
  {path: '', component: LoginComponent},
  {path: 'options', component: OptionsComponent},
  {path: 'testtopbar', component: TopbarComponent},
  {path: 'brigade-schedule', component: BrigadeScheduleComponent},
  {path: 'visualization', component: VisualizationComponent},
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {
}
