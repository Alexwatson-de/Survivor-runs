import {defineConfig} from '@playwright/test';
export default defineConfig({
 testDir:'./tests/overhaul/browser',timeout:150000,workers:1,retries:0,
 reporter:[['list'],['json',{outputFile:'artifacts/survivor-browser-results.json'}]],
 use:{baseURL:process.env.SURVIVOR_URL||'http://127.0.0.1:5193',viewport:{width:1280,height:720},headless:true,screenshot:'only-on-failure',trace:'retain-on-failure'},
 projects:[{name:'chromium',use:{browserName:'chromium',channel:'chrome'}},{name:'webkit',testMatch:/smoke.spec.js/,use:{browserName:'webkit'}}],
 webServer:{command:'PORT=5193 node serve-built-game.mjs',url:'http://127.0.0.1:5193',reuseExistingServer:true,timeout:30000}
});
