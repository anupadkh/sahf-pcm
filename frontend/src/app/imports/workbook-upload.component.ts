import {Component,inject,signal,Output,EventEmitter,ChangeDetectorRef} from '@angular/core';
import {FormsModule} from '@angular/forms';
import {ApiService} from '../core/api.service';
@Component({selector:'pcm-workbook-upload',standalone:true,imports:[FormsModule],templateUrl:'./workbook-upload.component.html'})
export class WorkbookUploadComponent {
  api=inject(ApiService);changeDetector=inject(ChangeDetectorRef);@Output() imported=new EventEmitter<any>();
  file:File|null=null;sheets:any[]=[];selected='';busy=false;error=signal('');
  async select(event:Event){const input=event.target as HTMLInputElement;this.file=input.files?.[0]||null;this.sheets=[];this.selected='';this.error.set('');if(!this.file)return;
    if(!this.file.name.toLowerCase().endsWith('.xlsx')||this.file.size>10*1024*1024){this.error.set('Select an XLSX workbook smaller than 10 MB.');return;}
    this.busy=true;try{const data=new FormData();data.append('file',this.file);const result=await this.api.request('/import/sheets','POST',data);this.sheets=result.sheets;this.selected=result.selected;}catch(e){this.error.set(e instanceof Error?e.message:String(e));}finally{this.busy=false;input.value='';this.changeDetector.markForCheck();}}
  async upload(){if(!this.file||!this.selected||this.busy)return;this.busy=true;this.error.set('');try{const data=new FormData();data.append('file',this.file);data.append('sheet',this.selected);const result=await this.api.request('/import','POST',data);if(result.errors.length&&!result.imported)this.error.set(result.errors.map((e:any)=>'Row '+e.row+': '+e.message).join('\n'));else{this.imported.emit(result);this.file=null;this.sheets=[];this.selected='';}}catch(e){this.error.set(e instanceof Error?e.message:String(e));}finally{this.busy=false;this.changeDetector.markForCheck();}}
}
