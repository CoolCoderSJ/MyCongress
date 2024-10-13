import $ from 'dom7';
import Framework7, { getDevice } from 'framework7/bundle';
import F7WelcomescreenPlugin from 'f7-welcomescreen';

// Import F7 Styles
import 'framework7/css/bundle';

// Import Icons and App Custom Styles
import '../css/icons.css';
import '../css/app.css';
// Import Cordova APIs
import cordovaApp from './cordova-app.js';

// Import Routes
import routes from './routes.js';
// Import Store
import store from './store.js';

// Import main app component
import App from '../app.f7';

let welcomescreen_slides = [
  {
    id: 'slide0',
    title: 'Welcome to billable!',
    picture: '<i class="f7-icons">building_columns_fill</i>',
    text: 'Welcome to billable! Quickly find out more about who represents you. <br><br><a class="button button-tonal" onclick="app.welcomescreen.next();">Next</a>',
  },
  {
    id: 'slide1',
    title: 'Allow access to your location?',
    picture: '<i class="f7-icons">map_pin_ellipse</i>',
    text: `By allowing access to your location, billable will be able to find your congresspeople automatically based on your location. <br><br><a class="button button-fill" style="margin-bottom: 10px" onclick="getLocation();">Allow Location</a> <a class="button button-tonal" onclick="app.welcomescreen.close(); localStorage.setItem('intro', true);;">Skip</a>`,
  },
];

Framework7.use(F7WelcomescreenPlugin);
var options = {
  bgcolor: '#232b22',
  fontcolor: '#fff',
  open: !localStorage.getItem('intro'),
};

var device = getDevice();
var app = new Framework7({
  name: 'billable', // App name
  theme: 'auto', // Automatic theme detection
  colors: {
    primary: '#0c2b0e',
  },
  darkMode: true,
  el: '#app', // App root element
  component: App, // App main component
  // App store
  store: store,
  // App routes
  routes: routes,



  // Input settings
  input: {
    scrollIntoViewOnFocus: device.cordova,
    scrollIntoViewCentered: device.cordova,
  },
  // Cordova Statusbar settings
  statusbar: {
    iosOverlaysWebView: true,
    androidOverlaysWebView: false,
  },
  on: {
    init: function () {
      var f7 = this;
      if (f7.device.cordova) {
        // Init cordova APIs (see cordova-app.js)
        cordovaApp.init(f7);
      }
    },
  },

  welcomescreen: {
    slides: welcomescreen_slides,
    options: options,
  },
});

window.app = app;

function getLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(showPosition);
  } else {
    alert("Geolocation is not supported by this browser.");
    app.welcomescreen.close();
    localStorage.setItem('intro', true);
  }
}

function showPosition(position) {
  localStorage.setItem('pos', JSON.stringify({ lat: position.coords.latitude, lon: position.coords.longitude }));
  app.welcomescreen.close();
  localStorage.setItem('intro', true);
}

window.getLocation = getLocation;