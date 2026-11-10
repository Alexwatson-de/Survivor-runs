export function objectivesMet(r){const m=r.mission;return !!m&&r.distance>=(m.distance||0)&&r.kills>=(m.kills||0)&&r.dogKills>=(m.dogKills||0)&&r.supplies>=(m.supplies||0)&&r.rescues>=(m.rescues||0);}
export function settle(r,success){
 if(r.result)return;r.phase=success?'complete':'dead';r.score=Math.floor(r.distance)+r.kills*60+r.headshots*25+r.supplies*25+r.rescues*250;
 const p=r.profile,first=success&&r.mission&&!p.completed.includes(r.mission.id),credits=Math.floor(r.distance/10)+r.kills*4+r.rescues*40+(first?r.mission.reward:0);
 r.result={success,credits,distance:Math.floor(r.distance),kills:r.kills,dogKills:r.dogKills,headshots:r.headshots,score:r.score,accuracy:r.shots?Math.round(r.hits/r.shots*100):0,time:r.time,damage:r.damageTaken,rescues:r.rescues,supplies:r.supplies};
 p.credits+=credits;p.best=Math.max(p.best,Math.floor(r.distance));p.runs++;p.totalKills+=r.kills;p.totalDistance+=Math.floor(r.distance);p.totalShots+=r.shots;p.totalHits+=r.hits;p.totalTime+=r.time;p.totalDamage+=r.damageTaken;p.totalRescues+=r.rescues;
 if(first)p.completed.push(r.mission.id);r.emit('finish',r.result);
}
