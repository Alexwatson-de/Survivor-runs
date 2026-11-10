// Survivor Runs 0.2. The existing project and v1 records are retained/migrated.
export const WEAPONS={
 pistol:{label:'PX9 · Sidearm',asset:'weapon_pistol',damage:40,interval:.28,reload:1.45,mag:12,reserve:60,range:55,spread:.009,recoil:.025,cost:0,muzzle:.19},
 revolver:{label:'R6 · Trail Revolver',asset:'weapon_revolver',damage:94,interval:.50,reload:2.45,mag:6,reserve:36,range:60,spread:.006,recoil:.055,cost:220,muzzle:.27},
 shotgun:{label:'M12 · Pump Shotgun',asset:'weapon_shotgun',damage:24,pellets:7,interval:.88,reload:2.6,mag:6,reserve:30,range:30,spread:.055,recoil:.080,cost:180,muzzle:.76},
 rifle:{label:'AR4 · Carbine',asset:'weapon_rifle',damage:33,interval:.105,reload:2.1,mag:30,reserve:120,range:70,spread:.014,recoil:.022,cost:400,muzzle:.61},
 smg:{label:'V9 · Compact SMG',asset:'weapon_smg',damage:24,interval:.075,reload:1.8,mag:32,reserve:128,range:43,spread:.025,recoil:.018,cost:500,muzzle:.34},
 hunting:{label:'H7 · Hunting Rifle',asset:'weapon_hunting',damage:152,interval:1.05,reload:2.8,mag:5,reserve:25,range:100,spread:.002,recoil:.070,cost:650,muzzle:.80}
};
export const DOGS={shepherd:{label:'Rook',breed:'German Shepherd',ability:'Guardian · strong bite and resilient health',damage:92,reach:24,cooldown:3.0,hp:125,speed:13,cost:0},husky:{label:'Ghost',breed:'Siberian Husky',ability:'Scout · wide detection and faster interception',damage:66,reach:34,cooldown:2.15,hp:100,speed:16,cost:300}};
export const CHARACTERS={mara:{label:'The Drifter',role:'Supplied cowboy · faster stamina recovery',hp:100,regen:15,cost:0},ellis:{label:'Field Medic',role:'Same supplied cowboy · 125 health loadout',hp:125,regen:12,cost:200}};
export const ENEMIES={walker:{hp:90,speed:1.05,chase:1.0,damage:23,radius:.32,height:1.82},runner:{hp:72,speed:3.5,chase:2.4,damage:28,radius:.3,height:1.82},brute:{hp:240,speed:.65,chase:.75,damage:44,radius:.49,height:1.98},military:{hp:145,speed:1.4,chase:1.3,damage:29,radius:.36,height:1.86,armor:.58},stalker:{hp:82,speed:2.7,chase:2.2,damage:32,radius:.31,height:1.82}};
export const MISSIONS=[
 {id:'firstlight',title:'01 / First Light',brief:'Break through the exclusion zone. Reach 500 m.',distance:500,reward:150},
 {id:'clearance',title:'02 / Clear the Road',brief:'Stop 20 infected in a single run.',kills:20,reward:220},
 {id:'pack',title:'03 / Never Alone',brief:'Survive 800 m with 8 companion kills.',distance:800,dogKills:8,reward:300},
 {id:'supplyline',title:'04 / The Supply Line',brief:'Collect 4 supply cases and reach 450 m.',distance:450,supplies:4,reward:320},
 {id:'extraction',title:'05 / One More Life',brief:'Find the stranded survivor. Press E nearby to rescue. Reach 650 m.',distance:650,rescues:1,reward:450}
];
export const LOCATIONS=[{id:'forest',label:'Blackpine Forest',best:0},{id:'village',label:'Hollow Creek Village',best:240},{id:'checkpoint',label:'Quarantine Line',best:480},{id:'industrial',label:'Rusted Works',best:720},{id:'highway',label:'The Vehicle Graveyard',best:960},{id:'camp',label:'Last Ember Camp',best:1200}];
export const THEMES=LOCATIONS.map(l=>l.label),SEGMENT=48,PATH_HALF=144;
// 0.3 world-space X/S replaces the curved endless-runner corridor. Kept as a zero
// transform for old presentation utilities; travel distance is no longer a position.
export const pathCenter=s=>0;
export const clamp=(n,a,b)=>Math.max(a,Math.min(b,n));
export function defaultProfile(){return {version:2,credits:0,best:0,runs:0,totalKills:0,totalDistance:0,totalShots:0,totalHits:0,totalTime:0,totalDamage:0,totalRescues:0,unlocked:{mara:true,shepherd:true,pistol:true},upgrades:{weapon:0,dog:0},completed:[],character:'mara',dog:'shepherd',weapon:'pistol',location:'forest',settings:{volume:.55,autofire:false,quality:'high',weather:true,shake:true,blood:true,companionMode:'guard',sensitivity:1}};}
export function normalizeProfile(p){
 const d=defaultProfile();if(!p||![1,2].includes(p.version))return d;
 const q={...d,...p,version:2,settings:{...d.settings,...p.settings},unlocked:{...d.unlocked,...p.unlocked},upgrades:{...d.upgrades,...p.upgrades}};
 for(const k of ['credits','best','runs','totalKills','totalDistance','totalShots','totalHits','totalTime','totalDamage','totalRescues'])q[k]=Math.max(0,Number.isFinite(q[k])?q[k]:0);
 for(const k of ['weapon','dog'])q.upgrades[k]=clamp(Math.floor(Number(q.upgrades[k])||0),0,5);
 for(const [k,items,fallback]of [['character',CHARACTERS,'mara'],['dog',DOGS,'shepherd'],['weapon',WEAPONS,'pistol']])if(!items[q[k]]||!q.unlocked[q[k]])q[k]=fallback;
 q.completed=Array.isArray(q.completed)?q.completed.filter(x=>MISSIONS.some(m=>m.id===x)):[];
 q.settings.volume=clamp(Number(q.settings.volume)||0,0,1);q.settings.sensitivity=clamp(Number(q.settings.sensitivity)||1,.35,2);
 if(!['guard','aggressive','scout'].includes(q.settings.companionMode))q.settings.companionMode='guard';
 if(!LOCATIONS.some(l=>l.id===q.location&&q.best>=l.best))q.location='forest';
 return q;
}
export function purchase(p,key,category){
 if(category==='location'){const l=LOCATIONS.find(l=>l.id===key);if(!l||p.best<l.best)return false;p.location=key;return true;}
 if(category==='upgrade'){const lv=p.upgrades[key];if(lv===undefined||lv>=5)return false;const cost=100+lv*100;if(p.credits<cost)return false;p.credits-=cost;p.upgrades[key]++;return true;}
 const item=({character:CHARACTERS,dog:DOGS,weapon:WEAPONS})[category]?.[key];if(!item)return false;
 if(!p.unlocked[key]){if(p.credits<item.cost)return false;p.credits-=item.cost;p.unlocked[key]=true;}p[category]=key;return true;
}
