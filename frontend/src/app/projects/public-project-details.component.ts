import {Component,Input,Output,EventEmitter} from '@angular/core';
import {CommonModule} from '@angular/common';
import {Project} from '../models';
@Component({selector:'pcm-public-project-details',standalone:true,imports:[CommonModule],template:`<div class="overlay"><section class="modal" role="dialog" aria-modal="true" aria-labelledby="public-record-title"><div class="section-head"><h2 id="public-record-title">Project details</h2><button aria-label="Close project details" (click)="closed.emit()">✕</button></div><dl>@for(c of fields;track c.key){<dt><b>{{c.label}}</b></dt><dd class="cell-text">@if(c.key==='commitment_usd'){ {{value(c.key)==null?'Not disclosed':(value(c.key)|currency:'USD':'symbol':'1.0-0')}} }@else{ {{display(c.key)}} }</dd>}</dl></section></div>`})
export class PublicProjectDetailsComponent {
  @Input() project!:Project;@Input() screenOptions:any[]=[];@Output() closed=new EventEmitter<void>();
  get fields(){return this.screenOptions.filter(c=>!c.hidden_public&&!c.internal);}
  value(key:string):any{return (this.project as any)[key];}
  display(key:string){const v=this.value(key);return Array.isArray(v)?v.map(n=>'P'+n).join(', '):typeof v==='boolean'?(v?'Yes':'No'):v??'—';}
}
