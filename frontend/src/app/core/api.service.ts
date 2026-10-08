import {Injectable} from '@angular/core';
@Injectable({providedIn:'root'})
export class ApiService {
  get token(){return sessionStorage.getItem('pcm-token')||'';}
  async request<T=any>(path:string,method='GET',body?:unknown):Promise<T>{
    const headers:Record<string,string>={};
    if(this.token)headers['Authorization']='Bearer '+this.token;
    if(body&&!(body instanceof FormData))headers['Content-Type']='application/json';
    const response=await fetch('/api'+path,{method,headers,body:body instanceof FormData?body:body?JSON.stringify(body):undefined});
    const text=await response.text();let data:any;
    try{data=text?JSON.parse(text):{};}catch{throw new Error('The server returned an unexpected response. Check that the FastAPI backend is running.');}
    if(!response.ok){if(response.status===401)sessionStorage.removeItem('pcm-token');throw new Error(typeof data.detail==='string'?data.detail:JSON.stringify(data.detail||data));}
    return data;
  }
}
