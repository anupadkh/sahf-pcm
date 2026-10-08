import {Injectable,inject,signal} from '@angular/core';
import {ApiService} from './api.service';
import {User} from '../models';
export function rolePath(role:string){return '/'+({technical_manager:'technical-manager',administrator:'administrator',contributor:'contributor'}[role]||'');}
@Injectable({providedIn:'root'})
export class AuthService {
  private api=inject(ApiService);user=signal<User|null>(null);
  private restoration:Promise<void>|null=null;
  async restore(){
    if(!this.api.token){this.user.set(null);return;}
    if(this.user())return;
    if(!this.restoration)this.restoration=this.api.request<User>('/auth/me').then(u=>{this.user.set(u);}).catch(()=>{sessionStorage.removeItem('pcm-token');this.user.set(null);}).finally(()=>{this.restoration=null;});
    await this.restoration;
  }
  async login(email:string,password:string){const result=await this.api.request<{token:string;user:User}>('/auth/login','POST',{email,password});sessionStorage.setItem('pcm-token',result.token);this.user.set(result.user);return result.user;}
  async logout(){try{if(this.api.token)await this.api.request('/auth/logout','POST');}finally{sessionStorage.removeItem('pcm-token');this.user.set(null);}}
}
