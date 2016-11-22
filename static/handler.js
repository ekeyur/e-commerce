var app = angular.module('mystore',['ui.router','ngCookies']);

app.config(function($stateProvider,$urlRouterProvider){
  $stateProvider
  .state({
    name: 'allProducts',
    url: '/all-products',
    templateUrl:'all-products.html',
    controller: 'all-productsCtrl'
  })

  .state({
    name: 'thankyou',
    url : '/thankyou',
    templateUrl:'checkout_success.html',
    controller: 'checkoutSuccessCtrl'
  })

  .state({
    name: 'oneProduct',
    url: '/all-products/{id}',
    templateUrl:'one-product.html',
    controller: 'one-productCtrl'
  })

  .state({
    name: 'signup',
    url:'/user/signup',
    templateUrl:'signup.html',
    controller:'signupCtrl'
  })

  .state({
    name: 'confirmCheckout',
    url:'/api/shopping_cart/checkout',
    templateUrl:'checkout_success.html',
    controller:'checkoutSuccessCtrl'
  })

  .state({
    name: 'login',
    url:'/user/login',
    templateUrl:'login.html',
    controller:'loginCtrl'
  })

  .state({
    name: 'checkout',
    url:'/shopping_cart/checkout',
    templateUrl:'checkout.html',
    controller:'checkoutCtrl'
  })

  .state({
    name: 'viewCart',
    url:'/api/shopping_cart',
    templateUrl:'view_shopping_cart.html',
    controller:'viewCartCtrl'
  });

});

app.factory('BackEndService',function($http,$cookies,$rootScope){
  var service = {};
  var cart = {};
  service.auth_token = $cookies.getObject('user_cookie').auth_token.token;
  $rootScope.user = $cookies.getObject('user_cookie').user;

  service.login = function(user){
    var url = "/api/user/login";
    console.log(user);
    return $http({
      method : 'POST',
      url : url,
      data : user
    }).success(function(data){
      service.auth_token = data.auth_token.token;
    });
  };

  service.view_cart = function(){
    var url = "/api/shopping_cart";
    return $http({
      method : 'GET',
      url : url,
      params : {'auth_token' : service.auth_token}
    });
  };

  //service for checkout controller
  service.checkOut = function(obj){
    cart = obj;
  };

  service.getCart = function(){
    return cart;
  };

  service.checkout_success = function(purchase){
    var url = "/api/shopping_cart/checkout";
    {
      return $http({
        method: 'POST',
        url: url,
        data:purchase
      });
    }
  };

  service.signup = function(user){
    var url = "/api/user/signup";
    {
      return $http({
        method: 'POST',
        url: url,
        data : user
      });
    }
  };

  service.addtoCart = function(data){
    var url = "api/shopping_cart";
    {
      return $http({
        method : 'POST',
        url: url,
        data : data
      });
    }
  };

  service.allProducts = function(){
    var url = "/api/products";
    return $http({
      method: 'GET',
      url: url,
    });
  };

  service.oneProduct = function(id){
    var url = "/api/products/"+id;
    return $http({
      method: 'GET',
      url:url,
    });
  };

  return service;
});

app.controller('checkoutSuccessCtrl',function(BackEndService,$scope,$state,$cookies){

});

app.controller('viewCartCtrl',function(BackEndService,$scope,$state){
  BackEndService.view_cart().success(function(data){
    $scope.cart = data;
    console.log(data);
    BackEndService.checkOut(data);
    $state.go('viewCart');

    $scope.checkOut = function(){
    $state.go('checkout');
    };

  });
});

app.controller('addCartCtrl',function($state,BackEndService,$stateParams,$scope,$cookies){
  $scope.addtoCart = function(){
    var cookie = $cookies.getObject('user_cookie').auth_token.token;
    var obj = {'auth_token':cookie, 'product_id' : $stateParams.id};
    BackEndService.addtoCart(obj).success(function(data){
      $state.go('allProducts');
    });
  };
});

app.controller('checkoutCtrl',function($scope,$state,BackEndService,$cookies){
  console.log(BackEndService.getCart());
     $scope.ccart = BackEndService.getCart();
     $scope.submit_address = function(){
       var xsn = {'address' : $scope.address, 'city' : $scope.city, 'state' : $scope.state, 'zip' : $scope.zip, 'total_price' : BackEndService.getCart().cart_total[0].sum, 'auth_token' :  $cookies.getObject('user_cookie').auth_token.token};
       console.log(xsn);
       BackEndService.checkout_success(xsn).success(function(data){
         console.log('CheckoutOut Successful');
         $state.go('confirmCheckout');
         return data;
       });
     };
});

app.controller('loginCtrl',function($state,$rootScope,BackEndService,$scope,$cookies){
  $scope.login = function()
  {
    var user = {'uname':$scope.uname, 'pass' : $scope.password};
    BackEndService.login(user).success(function(data){
      $cookies.putObject('user_cookie',data);
      $rootScope.user = data.user;
      $state.go('allProducts');
    });
  };
});

app.controller('all-productsCtrl',function($scope,BackEndService){
  BackEndService.allProducts().success(function(data){
    console.log(data);
    $scope.products = data;
  });
});

app.controller('signupCtrl',function($scope,BackEndService,$state)
{
  $scope.signup = function(){
    var user = {'uname':$scope.uname, 'fname':$scope.fname, 'lname':$scope.lname, 'email':$scope.email, 'password':$scope.password};
    BackEndService.signup(user).success(function(data){
      $state.go('login');
      console.log(data);
    });
  };
});

app.controller('one-productCtrl',function($scope,BackEndService,$stateParams){
  BackEndService.oneProduct($stateParams.id).success(function(data){
    console.log(data);
    $scope.oneproduct = data[0];
  });
});
