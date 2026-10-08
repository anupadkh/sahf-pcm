import {Component,Input,Output,EventEmitter} from '@angular/core';
import {FormsModule} from '@angular/forms';
import {CommonModule} from '@angular/common';
import {Project} from '../models';
@Component({selector:'pcm-project-list',standalone:true,imports:[CommonModule,FormsModule],templateUrl:'./project-list.component.html'})
export class ProjectListComponent {
  get moderator(){return this.area==='administrator'||this.area==='technical_manager';}
  selected=new Set<string>();message='';
  get selectedRecords(){return this.projects.filter(p=>p.id&&this.selected.has(p.id));}
  eligible(p:Project){return !['merged','deleted'].includes(p.workflow||'');}
  toggle(p:Project){if(!p.id)return;this.selected.has(p.id)?this.selected.delete(p.id):this.selected.add(p.id);}
  selectAll(){for(const p of this.projects)if(p.id)this.selected.add(p.id);}
  act(action:string){this.bulk.emit({action,records:this.selectedRecords,note:this.message});}
  @Output() bulk=new EventEmitter<{action:string;records:Project[];note:string}>();
  @Output() deleted=new EventEmitter<Project>();@Output() approved=new EventEmitter<Project[]>();@Output() rejected=new EventEmitter<Project>();

  @Input() screenOptions:any[]=[];
  get columns(){return this.screenOptions.filter(c=>c.show_table&&(this.area!=='public'||(!c.hidden_public&&!c.internal)));}
  value(p:Project,key:string):any{return (p as any)[key];}
  display(p:Project,key:string){const value=this.value(p,key);return Array.isArray(value)?value.map(v=>'P'+v).join(', '):typeof value==='boolean'?(value?'Yes':'No'):value===null||value===undefined||value===''?' - ':String(value).replaceAll('_',' ');}
  @Input() projects:Project[]=[];@Input() area='public';@Input() busy=false;
  @Output() opened=new EventEmitter<Project>();@Output() submitted=new EventEmitter<Project>();
}
