export interface Project {import_issues?:string;created_by?:string;creator_name?:string;created_at?:string;has_published?:boolean;published_data?:Project|null;conflicts?:any[];comments?:any[];merged_into?:string;id?:string; title:string; description:string; external_id:string; implementing_partner:string; funding_partner:string; country:string; project_status:string; start_date:string|null; end_date:string|null; commitment_usd:number|null; pillars:number[]; ibf_relevance:string; hazard:string; sector:string; multi_sector:boolean; notes:string; confidence:string; workflow?:string; org?:string; updated?:string; review_note?:string;}
export interface User {active?:boolean;email:string; name:string; role:string; org:string; country:string;}

export const blank = ():Project => ({title:'',description:'',external_id:'',implementing_partner:'',funding_partner:'ADB',country:'Nepal',project_status:'Ongoing',start_date:null,end_date:null,commitment_usd:0,pillars:[],ibf_relevance:'No',hazard:'Flood',sector:'DRR',multi_sector:false,notes:'',confidence:'Medium'});


