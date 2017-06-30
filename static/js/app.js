'use strict';

angular.module('oClock',
    ['oClock.services'],
    function($locationProvider) {
      $locationProvider.html5Mode(true);
    }
);