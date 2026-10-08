export function downloadCsv(rows:Record<string,unknown>[],filename:string){
  if(!rows.length)return;
  const keys=Object.keys(rows[0]);
  const quote=(value:unknown)=>'"'+String(value??'').replace(/^[=+@-]/,"'").replace(/"/g,'""')+'"';
  const csv=[keys.map(quote).join(','),...rows.map(row=>keys.map(key=>quote(row[key])).join(','))].join('\r\n');
  const url=URL.createObjectURL(new Blob([csv],{type:'text/csv'}));
  const anchor=document.createElement('a');anchor.href=url;anchor.download=filename;anchor.click();URL.revokeObjectURL(url);
}
