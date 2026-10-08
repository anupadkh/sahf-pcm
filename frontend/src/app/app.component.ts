import {Component,inject} from '@angular/core';
import {RouterLink,RouterOutlet} from '@angular/router';
import {AuthService,rolePath} from './core/auth.service';
@Component({standalone:true,selector:'pcm-app',imports:[RouterLink,RouterOutlet],templateUrl:'./app.component.html'})
export class AppComponent {auth=inject(AuthService);rolePath=rolePath;constructor(){void this.auth.restore();}}
