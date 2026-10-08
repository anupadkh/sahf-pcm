import {PublicProjectDetailsComponent} from '../projects/public-project-details.component';
import {ProjectListComponent} from '../projects/project-list.component';
import {downloadCsv} from '../utilities_functions/csv';
import {fundingGroups,countryBubbles} from '../utilities_functions/reporting';
import {Component, inject, signal, ChangeDetectorRef} from '@angular/core';
import {CommonModule} from '@angular/common';
import {FormsModule} from '@angular/forms';
import {ActivatedRoute, Router, RouterLink, RouterLinkActive} from '@angular/router';
import {Project, User, blank} from '../models';
import {ApiService} from '../core/api.service';
import {AuthService} from '../core/auth.service';
import {WorkbookUploadComponent} from '../imports/workbook-upload.component';
import {ProjectEditorComponent} from '../projects/project-editor.component';
@Component({standalone:true,imports:[CommonModule,FormsModule,RouterLink,RouterLinkActive,WorkbookUploadComponent,ProjectEditorComponent,ProjectListComponent,PublicProjectDetailsComponent],templateUrl:'./workspace.component.html'})
export class WorkspaceComponent {
  Math=Math;
  changeDetector=inject(ChangeDetectorRef);
  pendingBulk=signal<{action:string;records:Project[];note:string}|null>(null);bulkMessage='';bulkError=signal('');
  route=inject(ActivatedRoute); router=inject(Router); area=this.route.snapshot.data['area'] as string;
  adminPage=this.route.snapshot.data['adminPage']||'overview';
  get showRecords(){return this.area!=='administrator'||this.adminPage==='records';}
  userSearch='';editingEmail='';userActive=true;
  filteredUsers(){return this.users().filter(u=>(u.name+' '+u.email+' '+u.org+' '+u.role).toLowerCase().includes(this.userSearch.toLowerCase()));}
  auth=inject(AuthService); apiService=inject(ApiService);
  user=this.auth.user; projects=signal<Project[]>([]); taxonomy=signal<any>({countries:[],funding_partners:[],hazards:[],sectors:[],pillars:[]});
  screenOptions:any[]=[];
  publicVisible(key:string){return this.area!=='public'||this.screenOptions.some(c=>c.key===key&&!c.hidden_public&&!c.internal);}
  async saveScreenOptions(){await this.run(async()=>{this.screenOptions=await this.api('/admin/screen-options','PUT',{columns:this.screenOptions.map(({key,hidden_public,show_table})=>({key,hidden_public,show_table}))});this.notice.set('Screen options saved.');});}
  logs=signal<any[]>([]); users=signal<User[]>([]); error=signal(''); notice=signal(''); loading=signal(true);
  importErrors=''; creator=''; email=''; password=''; search=''; country=''; status=''; projectStatus=''; implementer=''; funder=''; sectorFilter=''; editor:Project|null=null; reviewNote=''; settings={enforce_pillars:false,require_ibf:true};
  newUser={email:'',name:'',password:'',role:'contributor',org:'',country:'Nepal'}; showUser=false; busy=false;
  get title(){if(this.area==='administrator')return {overview:'Administrator Overview',records:'Manage Records',users:'Manage Users',audit:'System Audit Log',screenOptions:'Screen Options'}[this.adminPage as string]||'Administrator';return {public:'South Asia Hydrological Forum',contributor:'My Projects Workspace',technical_manager:'Data Validation & Consolidation Hub',administrator:'System Administrator Console'}[this.area];}
  get subtitle(){return {public:'A shared view of hydromet investment and early warning initiatives across South Asia.',contributor:'Create project records and submit your organization’s initiatives for technical review.',technical_manager:'Validate submissions, resolve data quality issues and publish regional initiatives.',administrator:'Manage platform access, validation policies and the system audit trail.'}[this.area];}
  constructor(){this.email={contributor:'contributor@pcm.local',technical_manager:'reviewer@pcm.local',administrator:'admin@pcm.local'}[this.area]||''; void this.load();}
  async load(){this.loading.set(true);this.error.set('');try{this.taxonomy.set(await this.api('/taxonomy'));if(this.area==='public'){this.screenOptions=await this.api('/public/screen-options');this.projects.set(await this.api('/public/projects'));}else{await this.auth.restore();if(!this.user()){this.loading.set(false);return;}if(this.user()!.role!==this.area){this.error.set('Your account does not have access to this workspace.');this.loading.set(false);return;}this.screenOptions=await this.api('/screen-options');if(this.showRecords)this.projects.set(await this.api('/projects'));if(this.area==='administrator'){if(this.adminPage==='audit')this.logs.set(await this.api('/admin/audit'));if(this.adminPage==='users')this.users.set(await this.api('/admin/users'));if(this.adminPage==='overview')this.settings=await this.api('/admin/settings');}}}catch(e){this.error.set(String(e));}finally{this.loading.set(false);}}
  async logout(){await this.auth.logout();await this.router.navigateByUrl('/');}
  private api<T=any>(path:string,method='GET',body?:unknown){return this.apiService.request<T>(path,method,body);}
  async run(fn:()=>Promise<void>){if(this.busy)return;this.busy=true;this.error.set('');this.notice.set('');try{await fn();}catch(e){this.error.set(String(e));}finally{this.busy=false;this.changeDetector.markForCheck();}}
  filtered(){return this.projects().filter(p=>(!this.search||(p.title+' '+p.external_id+' '+p.funding_partner).toLowerCase().includes(this.search.toLowerCase()))&&(!this.importErrors||(this.importErrors==='errors'?!!p.import_issues?.trim():!p.import_issues?.trim()))&&(!this.creator||p.created_by===this.creator)&&(!this.country||p.country===this.country)&&(!this.status||(this.status==='published'?p.has_published:p.workflow===this.status))&&(!this.projectStatus||p.project_status===this.projectStatus)&&(!this.implementer||p.implementing_partner===this.implementer)&&(!this.funder||p.funding_partner===this.funder)&&(!this.sectorFilter||p.sector===this.sectorFilter));}
  values(key:'implementing_partner'|'funding_partner'){return [...new Set(this.projects().map(p=>p[key]).filter(Boolean))].sort();}
  ibfCount(){return this.filtered().filter(p=>p.ibf_relevance==='Yes').length;}
  countryCount(c:string){return this.filtered().filter(p=>p.country===c).length;}
  fundingGroups(){return fundingGroups(this.filtered());}
  mapCountries(){return countryBubbles(this.filtered());}
  resetFilters(){this.importErrors='';this.creator='';this.country='';this.projectStatus='';this.implementer='';this.funder='';this.sectorFilter='';this.search='';}
  total(){return this.filtered().reduce((n,p)=>n+(p.commitment_usd||0),0);}
  countries(){return [...new Set(this.filtered().map(p=>p.country))];}
  pillarCount(n:number){return this.filtered().filter(p=>p.pillars?.includes(n)).length;}
  hazardCount(h:string){return this.filtered().filter(p=>p.hazard===h).length;}
  open(p?:Project){this.moderationTarget='';this.moderationSource='';this.editor=p?structuredClone(p):blank();if(!p&&this.user()?.role==='contributor')this.editor.country=this.user()!.country;this.reviewNote=p?.review_note||'';}
  togglePillar(n:number){if(this.editor)this.editor.pillars=this.editor.pillars.includes(n)?this.editor.pillars.filter(x=>x!==n):[...this.editor.pillars,n];}
  moderationTarget='';moderationSource='';
  async save(){if(this.moderationTarget){await this.moderate('update_existing',this.moderationTarget);return;}await this.run(async()=>{if(!this.editor)return;this.editor.start_date=this.editor.start_date||null;this.editor.end_date=this.editor.end_date||null;await this.api('/projects'+(this.editor.id?'/'+this.editor.id:''),this.editor.id?'PUT':'POST',this.editor);this.editor=null;await this.load();this.notice.set('Project saved. Published edits are sent for approval; the previous approved version remains public.');});}
  async transition(p:Project,action:string){await this.run(async()=>{await this.api('/projects/'+p.id+'/transition','POST',{action,note:this.reviewNote,expected_updated:p.updated});this.editor=null;await this.load();this.notice.set(action==='reject_delete'?'Deletion rejected.':action==='publish'?'Project published.':action==='return'?'Project returned for correction.':'Submitted for technical review.');});}
  async deleteProject(p:Project){await this.bulkAction({action:'delete',records:[p],note:''});}
  creators(){return [...new Map(this.projects().filter(p=>p.created_by).map(p=>[p.created_by!,{email:p.created_by!,name:p.creator_name||p.created_by!}])).values()].sort((a,b)=>a.name.localeCompare(b.name));}
  async approveList(records:Project[]){await this.bulkAction({action:'approve',records,note:''});}
  async bulkAction(event:{action:string;records:Project[];note:string}){
    if(!event.records.length||this.busy)return;
    if(this.area==='contributor'&&!['submit','delete'].includes(event.action)){this.error.set('Contributors can only submit for review or request deletion.');return;}
    this.bulkMessage=event.note;this.bulkError.set('');this.pendingBulk.set({...event,records:[...event.records]});
  }
  async confirmBulk(){
    const event=this.pendingBulk();if(!event||this.busy)return;
    const {action,records}=event;const note=this.bulkMessage.trim();
    if(['reject','delete'].includes(action)&&!note){this.bulkError.set('Enter a common message for rejection or deletion.');return;}
    await this.run(async()=>{let success=0;const failures:string[]=[];
      for(const p of records){try{
        if(action==='delete'){await this.api('/projects/'+p.id,'DELETE',{note,expected_updated:p.updated});}
        else {const transition=action==='submit'?'submit':p.workflow==='deletion_pending'?(action==='approve'?'approve_delete':'reject_delete'):(action==='approve'?'publish':'return');
          await this.api('/projects/'+p.id+'/transition','POST',{action:transition,note,expected_updated:p.updated});}
        success++;
      }catch(e){failures.push((p.title||'Record')+': '+(e instanceof Error?e.message:String(e)));}}
      this.pendingBulk.set(null);await this.load();
      this.notice.set(success+' of '+records.length+' record(s) processed.'+(action==='submit'?' Submitted records are sent for review.':action==='delete'?' Published records await deletion approval.':''));
      if(failures.length)this.error.set(failures.join('\n'));
    });
  }
  async imported(result:any){this.resetFilters();this.status='draft';await this.load();this.notice.set(result.imported+' draft records imported from '+result.sheet+'.'+(result.warnings?.length?' Review notes: '+result.warnings.map((w:any)=>'Row '+w.row+': '+w.message).join('; '):''));}
  async saveSettings(){await this.run(async()=>{await this.api('/admin/settings','PUT',this.settings);await this.load();this.notice.set('Validation policy saved.');});}
  openUser(u?:User){this.editingEmail=u?.email||'';this.userActive=u?!!u.active:true;this.newUser=u?{email:u.email,name:u.name,password:'',role:u.role,org:u.org,country:u.country}:{email:'',name:'',password:'',role:'contributor',org:'',country:'Nepal'};this.showUser=true;}
  async provision(){await this.run(async()=>{if(this.editingEmail){const {email,password,...fields}=this.newUser;await this.api('/admin/users/'+encodeURIComponent(this.editingEmail),'PUT',{...fields,active:this.userActive,password:password||undefined});}else{await this.api('/admin/users','POST',this.newUser);}this.showUser=false;await this.load();this.notice.set(this.editingEmail?'User updated.':'User created.');});}
  async deleteUser(u:User){if(!window.confirm('Delete access for '+u.name+'? Their project ownership and history will be retained.'))return;await this.run(async()=>{await this.api('/admin/users/'+encodeURIComponent(u.email),'DELETE');await this.load();this.notice.set('User access deleted. Project ownership and history retained.');});}
  duplicate(p:Project){return !!p.conflicts?.length;}
  async moderate(action:string,target:string){await this.run(async()=>{if(!this.editor)return;await this.api('/projects/'+(this.moderationSource||this.editor.id)+'/moderate','POST',{action,existing_id:target,changes:action==='update_existing'?this.editor:undefined,note:this.reviewNote||'Conflict resolved by moderator'});this.editor=null;this.moderationTarget='';this.moderationSource='';await this.load();this.notice.set('Conflict resolved. The approved existing record is now public.');});}
  moderationChoice(event:{action:string;target:string}){if(event.action==='replace_existing'){void this.moderate(event.action,event.target);return;}const conflict=this.editor?.conflicts?.find(c=>c.id===event.target);if(!conflict||!this.editor)return;this.moderationSource=this.editor.id!;this.moderationTarget=event.target;this.editor={...structuredClone(conflict.data),id:this.moderationSource,workflow:'pending_review',conflicts:[]};}
  exportCsv(audit=false){const rows=audit?this.logs():this.filtered().map(p=>Object.fromEntries(this.screenOptions.filter(c=>c.show_table&&(this.area!=='public'||(!c.hidden_public&&!c.internal))).map(c=>[c.label,(p as any)[c.key]])));downloadCsv(rows,audit?'pcm-audit.csv':'pcm-projects.csv');}

}




