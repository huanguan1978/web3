//Disable jQM routing and component creation events. ref:https://github.com/ccoenraets/backbone-jquerymobile
$(document).bind("mobileinit", function(){     

   $.mobile.hashListeningEnabled = false;    // disable hash-routing
   $.mobile.linkBindingEnabled = false;    // disable anchor-control
   $.mobile.ajaxEnabled = false;    // can cause calling object creation twice and back button issues are solved
   $.mobile.autoInitializePage = false;    // Otherwise after mobileinit, it tries to load a landing page
   $.mobile.page.prototype.options.domCache = false;   // we want to handle caching and cleaning the DOM ourselves

   // consider due to compatibility issues
   $.mobile.pushStateEnabled = false;    // not supported by all browsers
   $.mobile.phonegapNavigationEnabled = true;    // Solves phonegap issues with the back-button
   $.mobile.page.prototype.options.degradeInputs.date = true;    //no native datepicker will conflict with the jQM component
});