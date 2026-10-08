import {Project} from '../models';
export function fundingGroups(projects:Project[]){
  const counts=new Map<string,number>();projects.forEach(p=>counts.set(p.funding_partner,(counts.get(p.funding_partner)||0)+1));
  return [...counts].map(([name,count])=>({name,count})).sort((a,b)=>b.count-a.count);
}
export function countryBubbles(projects:Project[]){
  const coordinates:Record<string,[number,number]>={'Afghanistan':[67,34],'Pakistan':[69,30],'India':[79,22],'Nepal':[84,28],'Bhutan':[90,27],'Bangladesh':[90,24],'Myanmar':[96,20],'Sri Lanka':[81,7],'Maldives':[73,3]};
  return Object.entries(coordinates).map(([name,[lon,lat]])=>({name,x:40+(lon-60)*12,y:330-lat*8,count:projects.filter(p=>p.country===name).length}));
}
