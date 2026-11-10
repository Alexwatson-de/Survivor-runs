import {defineConfig} from '@playwright/test';
export default defineConfig({
 testDir:'./tests/browser',timeout:90000,workers:1,retries:0,
 reporter:[['list'],['json',{outputFile:'artifacts/browser-results.json'}]],
 use:{baseURL:process.env.ASHFALL_URL||'http://127.0.0.1:5188',viewport:{width:1280,height:720},headless:true,screenshot:'only-on-failure',trace:'retain-on-failure'},
 projects:[{name:'chromium',use:{browserName:'chromium',channel:'chrome'}},{name:'webkit',testMatch:/smoke.spec.js/,use:{browserName:'webkit'}}],
 webServer:{command:'npm run dev -- --strictPort',url:'http://127.0.0.1:5188',reuseExistingServer:true,timeout:30000}
});
