import {Component,inject,signal} from '@angular/core';
import {FormsModule} from '@angular/forms';
import {Router} from '@angular/router';
import {AuthService,rolePath} from '../core/auth.service';
@Component({standalone:true,imports:[FormsModule],template:`<main><form class="card login" (ngSubmit)="login()"><span class="eyebrow">SECURE WORKSPACE</span><h1>Sign in</h1><p>Your account determines which workspace you can access.</p><label>Email<input name="email" type="email" [(ngModel)]="email" required autocomplete="username"></label><label>Password<input name="password" type="password" [(ngModel)]="password" required autocomplete="current-password"></label><button class="primary" [disabled]="busy">{{busy?'Signing in…':'Sign in'}}</button>@if(error()){<div class="message error" role="alert">{{error()}}</div>}</form></main>`})
export class LoginComponent {
  auth=inject(AuthService);router=inject(Router);email='';password='';busy=false;error=signal('');
  async login(){this.busy=true;this.error.set('');try{const user=await this.auth.login(this.email,this.password);this.password='';await this.router.navigateByUrl(rolePath(user.role));}catch(e){this.error.set(e instanceof Error?e.message:String(e));}finally{this.busy=false;}}
}
