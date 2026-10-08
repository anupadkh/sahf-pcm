import {Component, Input, Output, EventEmitter} from '@angular/core';
import {CommonModule} from '@angular/common';
import {FormsModule} from '@angular/forms';
import {Project, User} from '../models';
@Component({selector:'pcm-project-editor',standalone:true,imports:[CommonModule,FormsModule],templateUrl:'./project-editor.component.html'})
export class ProjectEditorComponent {
  @Input() editor:Project|null=null;
  @Input() area='public'; @Input() user:User|null=null; @Input() taxonomy:any={};
  @Input() busy=false; @Input() errorMessage=''; @Input() isDuplicate=false;
  @Input() moderationMode=false; @Input() reviewNote='';
  @Output() moderation=new EventEmitter<{action:string;target:string}>();
  @Output() reviewNoteChange=new EventEmitter<string>();
  @Output() closed=new EventEmitter<void>(); @Output() saved=new EventEmitter<void>();
  @Output() review=new EventEmitter<string>();
  field(project:Project,key:string){return (project as unknown as Record<string,unknown>)[key];}
  togglePillar(n:number){if(this.editor)this.editor.pillars=this.editor.pillars.includes(n)?this.editor.pillars.filter(x=>x!==n):[...this.editor.pillars,n];}
}
