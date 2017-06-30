'use strict';

function oClockCtrl($scope, $location, Conf, oClockApi) {
  // signIn
  $scope.userProfile = undefined;
  $scope.hasUserProfile = false;
  $scope.isSignedIn = false;
  $scope.immediateFailed = false;
  
  $scope.disconnect = function() {
    oClockApi.disconnect().then(function() {
      $scope.userProfile = undefined;
      $scope.hasUserProfile = false;
      $scope.isSignedIn = false;
      $scope.immediateFailed = true;
      $scope.userPhotos = [];
      $scope.friendsPhotos = [];
      //$scope.renderSignIn();
    });
  }
  
  $scope.signedIn = function(profile) {
    $scope.isSignedIn = true;
    $scope.userProfile = profile;
    $scope.hasUserProfile = true;
  };
  
  $scope.signIn = function(authResult) {
    $scope.$apply(function() {
      $scope.processAuth(authResult);
    });
  }
  
  $scope.processAuth = function(authResult) {
    $scope.immediateFailed = true;
    if ($scope.isSignedIn) {
      return 0;
    }
    if (authResult['access_token']) {
      $scope.immediateFailed = false;
      // Successfully authorized, create session
      oClockApi.signIn(authResult).then(function(response) {
        $scope.signedIn(response.data);
      });
    } else if (authResult['error']) {
      if (authResult['error'] == 'immediate_failed') {
        $scope.immediateFailed = true;
      } else {
        console.log('Error:' + authResult['error']);
      }
    }
  }
  
  $scope.renderSignIn = function() {
    gapi.signin.render('myGsignin', {
      'callback': $scope.signIn,
      'clientid': Conf.clientId,
      'requestvisibleactions': Conf.requestvisibleactions,
      'scope': Conf.scopes,
      'apppackagename': Conf.apppackagename,
      'theme': 'dark',
      'cookiepolicy': Conf.cookiepolicy,
      'accesstype': 'offline'
    });
  }
  
  $scope.start = function() {
	  $scope.renderSignIn();
    
	  var options = {
	    'clientid': Conf.clientId,
	    'contenturl': Conf.rootUrl + '/invite.html',
	    'contentdeeplinkid': '/',
	    'calltoactionlabel': 'Join',
	    'calltoactionurl': Conf.rootUrl,
	    'calltoactiondeeplinkid': '/',
	    'callback': $scope.signIn,
	    'requestvisibleactions': Conf.requestvisibleactions,
	    'scope': Conf.scopes,
	    'cookiepolicy': Conf.cookiepolicy
	  };
	  gapi.interactivepost.render('invite', options);
  }
  
  $scope.start();
  
}
