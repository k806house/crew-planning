import {BrowserModule} from '@angular/platform-browser';
import {NgModule} from '@angular/core';

import {AppRoutingModule} from './app-routing.module';
import {AppComponent} from './app.component';
import {LoginComponent} from './login/login.component';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {MatCardModule} from '@angular/material/card';
import {MatInputModule} from '@angular/material/input';
import {MatButtonModule} from '@angular/material/button';
import {OptionsComponent} from './options/options.component';


@NgModule({
  declarations: [
    AppComponent,
    LoginComponent,
    OptionsComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    MatCardModule,
    MatInputModule,
    MatButtonModule,

  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
