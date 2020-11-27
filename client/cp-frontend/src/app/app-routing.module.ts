import {NgModule} from '@angular/core';
import {Routes, RouterModule} from '@angular/router';
import {LoginComponent} from './login/login.component';
import {TopbarComponent} from './topbar/toolbar.component';
import {OptionsComponent} from './options/options.component';

const routes: Routes = [
  {path: '', component: LoginComponent},
  {path: 'options', component: OptionsComponent},
  {path: 'testtopbar', component: TopbarComponent},
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {
}
